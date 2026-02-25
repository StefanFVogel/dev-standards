# 🏗️ AI Architect Workflow: Deep Code Quality & Guardrails

Dieses Dokument beschreibt das Verfahren zur automatisierten Qualitätskontrolle. Es kombiniert statische Code-Analyse mit einer **"Architekten-Ampel"**, um objektiv zu messen, ob Code den Standards für Wartbarkeit und Design-Patterns entspricht.

---

## 🛠️ 1. Vorbereitung (Einmalig)

Speichere das folgende Skript unter `scripts/maintain_tools.py` und installiere die Sensoren:

```python
import os, shutil, subprocess, sys, argparse, json, re

# --- ARCHITEKTUR GRENZWERTE ---
MAX_COMPLEXITY = 10      # Gelb ab 10 (Radon C)
CRITICAL_COMPLEXITY = 20 # Rot ab 20 (Radon D/E)
MAX_DUPLICATION = 5      # Rot ab 5% Duplikaten (jscpd)
MIN_VULTURE_CONF = 80    # Sicherheitsschwelle für Vulture

def run_cmd(cmd):
    try: return subprocess.run(cmd, shell=True, capture_output=True, text=True)
    except Exception as e: return f"Error: {str(e)}"

def get_vulture_dead_code(py_files):
    if not py_files: return []
    res = run_cmd(f"vulture {' '.join(py_files)} --min-confidence {MIN_VULTURE_CONF}")
    return [l for l in res.stdout.splitlines() if not re.search(r'test_|tests/|/_test', l)]

def get_duplication_rate(files):
    if not shutil.which("npx") or not files: return 0
    res = run_cmd(f"npx jscpd {' '.join(files)} --threshold {MAX_DUPLICATION}")
    match = re.search(r"(\d+\.\d+)%\s+duplicated lines", res.stdout)
    return float(match.group(1)) if match else 0

def get_complexity_max(py_files):
    if not py_files: return 0
    res = run_cmd(f"radon cc {' '.join(py_files)} --json")
    try:
        data = json.loads(res.stdout)
        scores = [b.get("complexity", 0) for f in data.values() for b in f]
        return max(scores) if scores else 0
    except: return 0

def get_files(mode):
    cmds = {"commit": "git diff --name-only HEAD", "branch": "git diff --name-only main...", 
            "yesterday": "git diff --name-only @{yesterday}", "all": "git ls-files"}
    res = run_cmd(cmds.get(mode, cmds["commit"]))
    files = [f.strip() for f in res.stdout.splitlines() if f.strip() and os.path.exists(f)]
    return [f for f in files if f.endswith((".py", ".js", ".ts", ".sql"))]

def run_review(mode):
    files = get_files(mode)
    if not files: return print("[INFO] Keine Änderungen gefunden.")
    py_files = [f for f in files if f.endswith(".py")]
    max_cc, dead_items, dup_rate = get_complexity_max(py_files), get_vulture_dead_code(py_files), get_duplication_rate(files)
    
    status = "🟢 GRÜN"
    issues = []
    if max_cc >= MAX_COMPLEXITY: 
        status = "🔴 ROT" if max_cc >= CRITICAL_COMPLEXITY else "🟡 GELB"
        issues.append(f"KOMPLEXITÄT: {max_cc}")
    if dead_items: status = "🔴 ROT"; issues.append(f"TOTER CODE: {len(dead_items)} Funde")
    if dup_rate > MAX_DUPLICATION: status = "🔴 ROT"; issues.append(f"DUPLIKATE: {dup_rate}%")

    print(f"\n{'='*60}\n🏛️  ARCHITEKTEN-AMPEL: {status}\n" + "\n".join([f"  - {i}" for i in issues]) + f"\n{'='*60}\n")
    if py_files: 
        subprocess.run(f"radon cc {' '.join(py_files)} -nc", shell=True)
        if dead_items: print("\n[Vulture] Tote Stellen:\n" + "\n".join(dead_items))
    if shutil.which("npx"): subprocess.run(f"npx jscpd {' '.join(files)}", shell=True)

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--setup", action="store_true"); p.add_argument("--mode", default="commit")
    args = p.parse_args()
    if args.setup:
        subprocess.run([sys.executable, "-m", "pip", "install", "-U", "ruff", "vulture", "sqlfluff", "pyright", "radon"])
        if shutil.which("npm"): subprocess.run("npm install --save-dev jscpd", shell=True)
    else: run_review(args.mode)

```

---

Das Quality-Gate-Script liegt unter `scripts/maintain_tools.py` und nutzt drei Sensoren:

| Tool | Zweck | Grenzwert |
|------|-------|-----------|
| **Radon** | Zyklomatische Komplexität | CC ≤ 10 (Gelb), CC < 20 (Rot) |
| **Vulture** | Toter Code | 0% Toleranz |
| **jscpd** | Code-Duplikation | < 5% |

### Tools installieren

Alle benötigten Tools lassen sich mit einem einzigen Befehl installieren:

```bash
python standards/scripts/maintain_tools.py --setup
```

Dies führt automatisch 3 Schritte aus:
1. **Python-Pakete** installieren (via pip): `radon`, `vulture`, `ruff`, `pyright`, `sqlfluff`
2. **Node.js/npm** installieren via `nodeenv` (falls npm nicht vorhanden)
3. **Node.js-Pakete** installieren (via npm): `jscpd`, `@biomejs/biome`, `knip`

**Manuelle Installation** (alternativ):

```bash
# Python-Tools
pip install -U radon vulture ruff pyright sqlfluff

# Node.js-Tools
npm install --save-dev @biomejs/biome knip jscpd
```

---

## 🔄 2. Der Review-Zyklus (in Claude Code)

1. **Analyse starten:**
`run python scripts/maintain_tools.py --mode commit` (oder `branch` / `yesterday`)
2. **Den Architekten-Prompt nutzen:**
> "Agiere als **Senior Python Architekt**. Analysiere die Ergebnisse der **Architekten-Ampel**:


> 1. Bei **Toter Code = ROT**: Lösche ungenutzte Elemente sofort.
> 2. Bei **Komplexität = GELB/ROT**: Brich Spaghetti-Logik auf (Single Responsibility).
> 3. Bei **Duplikate = ROT**: Erstelle Abstraktionen (DRY-Prinzip).
> 4. **Patterns**: Schlage Factory, Strategy oder Repository Patterns vor, wo sinnvoll.
> Zeig mir die Top-Prioritäten und starte das Refactoring."
> 
> 



---

## 🎯 3. Goldene Regeln für den Review

* **Kein Spaghetti:** Funktionen mit einem Radon-Rating von **C** oder schlechter (>10) müssen aufgeteilt werden.
* **Toter Code ist Ballast:** Variablen oder Funktionen, die nicht von Tests oder der App genutzt werden, fliegen sofort raus.
* **Variable Hygiene:** Keine Variablen "auf Vorrat". Redundanter State wird eliminiert.
* **SOLID-Fokus:** Jede Klasse/Funktion hat genau **eine** klar definierte Aufgabe.

---

## 📈 4. Refactoring-Strategie

1. **Entwurf prüfen:** Lass dir von Claude erst das neue Interface oder Pattern-Design erklären.
2. **Iterative Umsetzung:** Bearbeite erst den Toten Code, dann die Komplexität, dann die Patterns.
3. **Abschluss-Check:** Nach dem Refactoring das Skript erneut laufen lassen, um die **GRÜNE Ampel** zu bestätigen.
