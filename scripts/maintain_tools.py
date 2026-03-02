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
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    except Exception as e:
        # Fallback return object to prevent crashes on attribute access
        return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr=str(e))


def py_tool(tool_name):
    venv_path = os.path.join(os.path.dirname(sys.executable), tool_name)
    if os.name == "nt":
        venv_path += ".exe"
    return venv_path if os.path.exists(venv_path) else tool_name


def _find_npx():
    """Finds npx, checking nodeenv path if not on system PATH."""
    if shutil.which("npx"):
        return "npx"
    # nodeenv installs into <venv>/node_env/Scripts/ (Windows) or <venv>/node_env/bin/ (Unix)
    venv_dir = os.path.dirname(sys.executable)
    node_env = os.path.normpath(os.path.join(venv_dir, "..", "node_env"))
    bin_dir = os.path.join(node_env, "Scripts" if os.name == "nt" else "bin")
    npx_cmd = os.path.join(bin_dir, "npx.cmd" if os.name == "nt" else "npx")
    if os.path.exists(npx_cmd):
        # Also ensure node.exe is findable by adding bin_dir to PATH for child processes
        os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
        return npx_cmd
    return None


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
    npx = _find_npx()
    if not npx or not files:
        return 0
    res = run_cmd(f"{npx} jscpd {' '.join(files)} --threshold {MAX_DUPLICATION} --reporter json")
    match = re.search(r"(\d+\.\d+)%\s+duplicated lines", res.stdout)
    return float(match.group(1)) if match else 0


def get_biome_issues(js_files):
    """Prüft JS/TS Dateien mit Biome und extrahiert Komplexitäts-Warnungen."""
    npx = _find_npx()
    if not npx or not js_files:
        return [], 0
    # --reporter=json liefert strukturierten Output
    res = run_cmd(f"{npx} biome lint {' '.join(js_files)} --reporter=json")
    issues = []
    max_comp = 0
    try:
        data = json.loads(res.stdout)
        for d in data.get("diagnostics", []):
            desc = d.get("description", "")
            # Versuche, die Komplexitätszahl aus der Meldung zu lesen
            # Bsp: "This function has a cognitive complexity of 25..."
            comp_match = re.search(r"complexity of (\d+)", desc)
            
            if comp_match:
                score = int(comp_match.group(1))
                max_comp = max(max_comp, score)
                loc = d.get("location", {})
                path = loc.get("path", {}).get("file", "unknown")
                issues.append(f"JS KOMPLEXITÄT: {path} hat Score {score} (Limit überschritten)")
            elif d.get("severity") == "error":
                loc = d.get("location", {})
                path = loc.get("path", {}).get("file", "unknown")
                issues.append(f"JS LINT: {path} - {desc}")
    except (json.JSONDecodeError, AttributeError):
        pass
    return issues, max_comp


def get_djlint_issues(html_files):
    """Prüft HTML Dateien mit djLint."""
    if not html_files:
        return []
    # --json liefert strukturierten Output
    res = run_cmd(f"{py_tool('djlint')} {' '.join(html_files)} --lint --json")
    issues = []
    try:
        data = json.loads(res.stdout)
        for filepath, errors in data.items():
            for err in errors:
                issues.append(f"HTML LINT: {filepath}:{err.get('line')} - {err.get('message')}")
    except (json.JSONDecodeError, AttributeError):
        pass
    return issues


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
            b.get("complexity", 0) for f, blocks in data.items()
            if isinstance(blocks, list)
            for b in blocks
            if isinstance(b, dict) and not _is_complexity_allowed(f, b.get("name", ""))
        ]
        return max(scores) if scores else 0
    except (json.JSONDecodeError, ValueError):
        return 0


def evaluate_ampel(max_cc, js_max_cc, dead_items, dup_rate, lint_issues):
    """Evaluates metrics and returns (status, issues)."""
    issues = []
    status = "🟢 GRÜN"

    # Python Komplexität
    if max_cc >= CRITICAL_COMPLEXITY:
        status = "🔴 ROT"
        issues.append(f"KOMPLEXITÄT (Python): {max_cc} (Kritisch!)")
    elif max_cc >= MAX_COMPLEXITY:
        status = "🟡 GELB"
        issues.append(f"KOMPLEXITÄT (Python): {max_cc} (Hoch)")

    # JS Komplexität (Biome Standard Limit ist oft 15)
    if js_max_cc > 15:
        status = "🔴 ROT"
        issues.append(f"KOMPLEXITÄT (JS): {js_max_cc} (Cognitive Complexity zu hoch!)")

    if len(dead_items) > 0:
        status = "🔴 ROT"
        issues.append(f"TOTER CODE: {len(dead_items)} Funde (außerhalb Tests)")

    if dup_rate > MAX_DUPLICATION:
        status = "🔴 ROT"
        issues.append(f"DUPLIKATE: {dup_rate}% (Struktur-Problem)")

    if lint_issues:
        status = "🔴 ROT"
        issues.extend(lint_issues)

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
        if not isinstance(blocks, list):
            continue
        entries = [
            b for b in blocks
            if isinstance(b, dict) and b.get("rank", "A") not in ("A", "B") and not _is_complexity_allowed(filepath, b.get("name", ""))
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

    npx = _find_npx()
    if npx:
        subprocess.run(f"{npx} jscpd {' '.join(files)}", shell=True)


def run_review(mode):
    files = get_files(mode)
    if not files:
        print("[INFO] Keine Änderungen gefunden.")
        return

    py_files = [f for f in files if f.endswith(".py")]
    js_files = [f for f in files if f.endswith((".js", ".ts", ".jsx", ".tsx"))]
    html_files = [f for f in files if f.endswith(".html")]

    max_cc = get_complexity_max(py_files)
    dead_items = get_vulture_dead_code(py_files)
    dup_rate = get_duplication_rate(files)

    lint_issues = []
    js_issues, js_max_cc = get_biome_issues(js_files)
    lint_issues.extend(js_issues)
    lint_issues.extend(get_djlint_issues(html_files))

    status, issues = evaluate_ampel(max_cc, js_max_cc, dead_items, dup_rate, lint_issues)

    print(f"\n{'=' * 60}")
    print(f"\U0001f3db\ufe0f  ARCHITEKTEN-AMPEL: {status}")
    for issue in issues:
        print(f"  - {issue}")
    print(f"{'=' * 60}\n")

    print_detailed_scan(py_files, dead_items, files)


def _get_default_branch():
    """Detects the default branch (main/master) of the repository."""
    res = run_cmd("git symbolic-ref refs/remotes/origin/HEAD")
    if res.returncode == 0 and res.stdout.strip():
        return res.stdout.strip().replace("refs/remotes/origin/", "")
    for candidate in ("main", "master"):
        check = run_cmd(f"git rev-parse --verify {candidate}")
        if hasattr(check, "returncode") and check.returncode == 0:
            return candidate
    return "main"


def get_files(mode):
    default_branch = _get_default_branch()
    cmds = {
        "commit": "git diff --name-only HEAD",
        "branch": f"git diff --name-only {default_branch}...",
        "yesterday": "git diff --name-only @{yesterday}",
        "all": "git ls-files",
    }
    res = run_cmd(cmds.get(mode, cmds["commit"]))
    files = [f.strip() for f in res.stdout.splitlines() if f.strip() and os.path.exists(f)]
    # Erweiterte Dateiendungen für JS/HTML
    return [f for f in files if f.endswith((".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".sql"))]


def setup_tools():
    print("--- [SETUP] ---")

    # 1. Python-Pakete installieren
    print("\n[1/3] Python-Pakete installieren...")
    # djlint hinzugefügt
    subprocess.run([sys.executable, "-m", "pip", "install", "-U", "ruff", "vulture", "sqlfluff", "pyright", "radon", "djlint"])

    # 2. Node.js/npm installieren (falls nicht vorhanden), via nodeenv (pyright-Abhängigkeit)
    if not shutil.which("npm"):
        print("\n[2/3] npm nicht gefunden - installiere Node.js via nodeenv...")
        node_dir = os.path.join(os.path.dirname(sys.executable), "..", "node_env")
        node_dir = os.path.normpath(node_dir)
        subprocess.run([sys.executable, "-m", "nodeenv", "--prebuilt", node_dir])
        # npm-Pfad zur aktuellen Session hinzufügen
        if os.name == "nt":
            npm_bin = os.path.join(node_dir, "Scripts")
        else:
            npm_bin = os.path.join(node_dir, "bin")
        os.environ["PATH"] = npm_bin + os.pathsep + os.environ["PATH"]
        if shutil.which("npm"):
            print(f"[OK] Node.js installiert in: {node_dir}")
        else:
            print("[WARN] Node.js Installation fehlgeschlagen - Duplikationsprüfung nicht verfügbar.")
    else:
        print("\n[2/3] npm bereits vorhanden - überspringe Node.js Installation.")

    # 3. Node.js-Pakete installieren
    if shutil.which("npm"):
        print("\n[3/3] Node.js-Pakete installieren...")
        subprocess.run("npm install --save-dev @biomejs/biome knip jscpd", shell=True)
    else:
        print("\n[3/3] Überspringe Node.js-Pakete (npm nicht verfügbar).")

    print("\n[OK] Setup bereit.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", action="store_true")
    parser.add_argument("--mode", choices=["commit", "branch", "yesterday", "all"], default="commit")
    args = parser.parse_args()
    if args.setup:
        setup_tools()
    else:
        run_review(args.mode)
