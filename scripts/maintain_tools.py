import argparse
import json
import os
import re
import shutil
import subprocess
import sys

# --- ARCHITEKTUR GRENZWERTE ---
MAX_COMPLEXITY = 10  # Gelb ab 10
CRITICAL_COMPLEXITY = 20  # Rot ab 20
MAX_DUPLICATION = 5  # Rot ab 5% Duplikaten
MIN_VULTURE_CONF = 80  # Sicherheitsschwelle für toten Code

# --- ALLOWLIST: Bewusst akzeptierte Findings ---
# Format: "datei:funktionsname" für Komplexität, "datei:zeile" für toten Code
# Jeder Eintrag braucht eine Begründung.
COMPLEXITY_ALLOWLIST = {
    "afx_press.py:parallel_processing",  # Thread-Pipeline: nested closures über shared state, nicht sinnvoll zerlegbar
}
DEAD_CODE_ALLOWLIST = {
    # __exit__ / __enter__ params sind Python-Pflicht, kein echter toter Code
    "unused variable 'exc_type'",
    "unused variable 'exc_value'",
    "unused variable 'exc_val'",
    "unused variable 'exc_tb'",
    "unused variable 'traceback'",
}


def run_cmd(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True)
    except Exception as e:
        return f"Error: {str(e)}"


def py_tool(tool_name):
    venv_path = os.path.join(os.path.dirname(sys.executable), tool_name)
    if os.name == "nt":
        venv_path += ".exe"
    return venv_path if os.path.exists(venv_path) else tool_name


def _is_dead_code_allowed(line):
    """Checks if a vulture finding matches the dead code allowlist."""
    return any(pattern in line for pattern in DEAD_CODE_ALLOWLIST)


def get_vulture_dead_code(py_files):
    """Scannt nach totem Code und ignoriert Treffer in Tests und Allowlist."""
    if not py_files:
        return []
    res = run_cmd(f"{py_tool('vulture')} {' '.join(py_files)} --min-confidence {MIN_VULTURE_CONF}")
    lines = res.stdout.splitlines()
    return [
        line for line in lines
        if not re.search(r"test_|tests/|/_test", line) and not _is_dead_code_allowed(line)
    ]


def get_duplication_rate(files):
    """Extrahiert die Duplikationsrate aus jscpd."""
    if not shutil.which("npx") or not files:
        return 0
    res = run_cmd(f"npx jscpd {' '.join(files)} --threshold {MAX_DUPLICATION} --reporter json")
    match = re.search(r"(\d+\.\d+)%\s+duplicated lines", res.stdout)
    return float(match.group(1)) if match else 0


def _is_complexity_allowed(filepath, name):
    """Checks if a radon finding matches the complexity allowlist."""
    basename = os.path.basename(filepath)
    return f"{basename}:{name}" in COMPLEXITY_ALLOWLIST


def get_complexity_max(py_files):
    """Returns max complexity score, ignoring allowlisted functions."""
    if not py_files:
        return 0
    res = run_cmd(f"{py_tool('radon')} cc {' '.join(py_files)} --json")
    try:
        data = json.loads(res.stdout)
        scores = [
            b.get("complexity", 0) for f, blocks in data.items() for b in blocks
            if not _is_complexity_allowed(f, b.get("name", ""))
        ]
        return max(scores) if scores else 0
    except (json.JSONDecodeError, ValueError):
        return 0


def evaluate_ampel(max_cc, dead_items, dup_rate):
    """Evaluates metrics and returns (status, issues)."""
    issues = []
    status = "🟢 GRÜN"

    if max_cc >= CRITICAL_COMPLEXITY:
        status = "🔴 ROT"
        issues.append(f"KOMPLEXITÄT: {max_cc} (Kritisch!)")
    elif max_cc >= MAX_COMPLEXITY:
        status = "🟡 GELB"
        issues.append(f"KOMPLEXITÄT: {max_cc} (Hoch)")

    if len(dead_items) > 0:
        status = "🔴 ROT"
        issues.append(f"TOTER CODE: {len(dead_items)} Funde (außerhalb Tests)")

    if dup_rate > MAX_DUPLICATION:
        status = "🔴 ROT"
        issues.append(f"DUPLIKATE: {dup_rate}% (Struktur-Problem)")

    return status, issues


def _get_filtered_complexity(py_files):
    """Returns radon findings filtered by allowlist, only C/D/F rank."""
    res = run_cmd(f"{py_tool('radon')} cc {' '.join(py_files)} --json")
    try:
        data = json.loads(res.stdout)
    except (json.JSONDecodeError, ValueError):
        return {}
    filtered = {}
    for filepath, blocks in sorted(data.items()):
        entries = [
            b for b in blocks
            if b.get("rank", "A") not in ("A", "B") and not _is_complexity_allowed(filepath, b.get("name", ""))
        ]
        if entries:
            filtered[filepath] = entries
    return filtered


def print_detailed_scan(py_files, dead_items, files):
    """Prints radon complexity, vulture dead code, and jscpd duplicates."""
    if py_files:
        print("--- [DETAILED SCAN] ---")
        type_map = {"method": "M", "function": "F", "class": "C"}
        for filepath, entries in _get_filtered_complexity(py_files).items():
            print(filepath)
            for b in entries:
                t = type_map.get(b.get("type", ""), "?")
                cls = f"{b['classname']}." if b.get("classname") else ""
                print(f"    {t} {b['lineno']}:{b.get('col_offset', 0)} {cls}{b['name']} - {b['rank']}")

        if dead_items:
            print("\n[Vulture] Fundstellen für toten Code:")
            for item in dead_items:
                print(f"  {item}")

    if shutil.which("npx"):
        subprocess.run(f"npx jscpd {' '.join(files)}", shell=True)


def run_review(mode):
    files = get_files(mode)
    if not files:
        print("[INFO] Keine Änderungen gefunden.")
        return

    py_files = [f for f in files if f.endswith(".py")]

    max_cc = get_complexity_max(py_files)
    dead_items = get_vulture_dead_code(py_files)
    dup_rate = get_duplication_rate(files)

    status, issues = evaluate_ampel(max_cc, dead_items, dup_rate)

    print(f"\n{'=' * 60}")
    print(f"\U0001f3db\ufe0f  ARCHITEKTEN-AMPEL: {status}")
    for issue in issues:
        print(f"  - {issue}")
    print(f"{'=' * 60}\n")

    print_detailed_scan(py_files, dead_items, files)


def get_files(mode):
    cmds = {
        "commit": "git diff --name-only HEAD",
        "branch": "git diff --name-only main...",
        "yesterday": "git diff --name-only @{yesterday}",
        "all": "git ls-files",
    }
    res = run_cmd(cmds.get(mode, cmds["commit"]))
    files = [f.strip() for f in res.stdout.splitlines() if f.strip() and os.path.exists(f)]
    return [f for f in files if f.endswith((".py", ".js", ".ts", ".sql"))]


def setup_tools():
    print("--- [SETUP] ---")
    subprocess.run([sys.executable, "-m", "pip", "install", "-U", "ruff", "vulture", "sqlfluff", "pyright", "radon"])
    if shutil.which("npm"):
        subprocess.run("npm install --save-dev @biomejs/biome knip jscpd", shell=True)
    print("[OK] Setup bereit.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", action="store_true")
    parser.add_argument("--mode", choices=["commit", "branch", "yesterday", "all"], default="commit")
    args = parser.parse_args()
    if args.setup:
        setup_tools()
    else:
        run_review(args.mode)
