# dev-standards

Zentrale Sammlung von Entwicklungsstandards, Coding Guidelines und Quality-Gate-Werkzeugen. Dieses Repository wird als Git Submodule in Projekte eingebunden und stellt einheitliche Regeln für Code-Qualität, Architektur und AI-gestützte Entwicklung bereit.

## Inhalt

| Pfad | Beschreibung |
|------|-------------|
| `docs/ai_guidelines.md` | Globale AI Coding Standards (Quality Gates, Python Standards, Architektur-Patterns) |
| `docs/implementation.md` | Implementierungs-Richtlinien & Coding Standards (Naming, Typing, Error Handling) |
| `docs/architect_workflow.md` | Automatisierte Qualitätskontrolle mit der Architekten-Ampel |
| `docs/feature_development_workflow.md` | Feature-Entwicklungsprozess: Spezifikation → Prototyp → Architektur-Review → Code-Review |
| `docs/frontend_coding_guidelines.md` | Frontend-Coding-Standards (JS, HTML/CSS, Bootstrap-Patterns) |
| `docs/deployment_checklist.md` | Deployment-Checkliste |
| `docs/claude_coding_rules.md` | Coding-Regeln für Claude Code (wird per `@import` in `CLAUDE.md` geladen) |
| `docs/claude_permissions.json` | Berechtigungs-Template für `.claude/settings.local.json` |
| `commands/setup.md` | Claude Code Slash-Command: `/setup` — Projekt-Setup |
| `commands/changes.md` | Claude Code Slash-Command: `/changes` — Änderungen seit letztem Commit |
| `commands/review-fix.md` | Claude Code Slash-Command: `/review-fix` — Automatischer Review-Fix-Loop |
| `scripts/maintain_tools.py` | Quality-Gate-Script: Setup, Review, Komplexität, toter Code, Duplikation |

---

## Quick Start

### 1. Submodule einbinden

```bash
git submodule add https://github.com/StefanFVogel/dev-standards.git standards
git add .gitmodules standards
git commit -m "Add dev-standards submodule"
```

### 2. Automatisches Setup ausführen

```bash
python standards/scripts/maintain_tools.py --setup
```

Das Script führt 5 Schritte aus:

| Schritt | Was passiert |
|---------|-------------|
| **[1/5]** Python-Pakete | `ruff`, `vulture`, `radon`, `pyright`, `sqlfluff`, `djlint` |
| **[2/5]** Node.js | Installiert Node.js via `nodeenv` (falls npm nicht vorhanden) |
| **[3/5]** Node-Pakete | `@biomejs/biome`, `knip`, `jscpd` |
| **[4/5]** Claude Commands | Kopiert `standards/commands/*.md` → `.claude/commands/` |
| **[5/5]** Claude Permissions | Generiert `.claude/settings.local.json` aus Template |

Nach dem Setup stehen die Slash-Commands `/setup`, `/changes` und `/review-fix` in Claude Code zur Verfügung.

### 3. CLAUDE.md konfigurieren

Im Projekt eine `CLAUDE.md` anlegen und die Coding-Regeln per `@import` laden:

```markdown
# CLAUDE.md

## Global Standards
@standards/docs/claude_coding_rules.md

## Project-spezifische Infos
...
```

Die `@import`-Zeile sorgt dafür, dass Claude Code bei jedem Gespräch automatisch die Coding-Regeln aus dem Submodule lädt.

---

## Claude Code Integration

### Übersicht

```
standards/                          Projekt/
├── docs/                           ├── .claude/
│   ├── claude_coding_rules.md ──@import──→ CLAUDE.md (automatisch geladen)
│   └── claude_permissions.json ──setup──→  │   ├── settings.local.json
├── commands/                       │   └── commands/
│   ├── setup.md ─────────────copy──→       │       ├── setup.md → /setup
│   ├── changes.md ───────────copy──→       │       ├── changes.md → /changes
│   └── review-fix.md ───────copy──→        │       └── review-fix.md → /review-fix
└── scripts/
    └── maintain_tools.py ──────────────────→ (führt Setup + Review aus)
```

### Slash-Commands

| Command | Beschreibung |
|---------|-------------|
| `/setup` | Führt `maintain_tools.py --setup` aus und verifiziert Permissions |
| `/changes` | Zeigt alle Änderungen seit dem letzten Commit als Zusammenfassung |
| `/review-fix` | Automatischer Review-Fix-Loop (max. 3 Iterationen bis Ampel GRÜN) |

### Permissions

Das Template `docs/claude_permissions.json` definiert die Standardberechtigungen:

- **Allow:** Alle Claude-Tools (Read, Write, Edit, Glob, Grep, ...), Python/Node Kommandos, Git-Lesebefehle
- **Deny:** Git-Schreibbefehle (`commit`, `push`, `reset`, `checkout`, `rebase`, `merge`)

Der Platzhalter `{{PROJECT_ROOT_UNIX}}` wird beim Setup automatisch durch den Git-Bash-Pfad des Projekts ersetzt (z.B. `/c/Users/dev/projects/my-app`).

**Merge-Verhalten:** Wenn `.claude/settings.local.json` bereits existiert, werden nur fehlende Permissions ergänzt. Eigene Anpassungen bleiben erhalten.

---

## Quality-Gate: Architekten-Ampel

### Review ausführen

```bash
# Änderungen auf aktuellem Branch vs. main prüfen
PYTHONIOENCODING=utf-8 python standards/scripts/maintain_tools.py --mode branch

# Nur uncommittete Änderungen prüfen
PYTHONIOENCODING=utf-8 python standards/scripts/maintain_tools.py --mode commit

# Alle Dateien prüfen
PYTHONIOENCODING=utf-8 python standards/scripts/maintain_tools.py --mode all
```

### Ampel-Schwellwerte

| Ampel | Kriterium |
|-------|----------|
| 🟢 GRÜN | Keine Findings in geänderten Dateien |
| 🟡 GELB | Komplexität 10–19 (Radon CC Rank C) |
| 🔴 ROT | Komplexität ≥ 20, oder toter Code, oder Duplikation > 5%, oder Lint-Fehler |

### Toolchain

| Tool | Sprache | Prüfung |
|------|---------|---------|
| **Ruff** | Python | Linting & Formatierung |
| **Vulture** | Python | Toter Code |
| **Radon** | Python | Zyklomatische Komplexität |
| **Pyright** | Python | Type-Checking |
| **Biome** | JS/TS | Linting, Formatierung & Complexity |
| **Knip** | JS/TS | Toter Code & ungenutzte Dependencies |
| **jscpd** | Alle | Code-Duplikation |
| **djLint** | HTML | Template-Linting |
| **SQLFluff** | SQL | T-SQL Linting |

### Manuelle Installation (falls kein `--setup` gewünscht)

```bash
# Python-Tools
pip install -U ruff vulture radon pyright sqlfluff djlint

# Node.js-Tools
npm install --save-dev @biomejs/biome knip jscpd
```

---

## Git Submodule Referenz

### Projekt klonen (mit Submodule)

```bash
# Variante A: Neues Klonen (empfohlen)
git clone --recurse-submodules <projekt-url.git>

# Variante B: Bereits geklont, Ordner 'standards' ist leer
git submodule update --init --recursive
```

### Submodule aktualisieren

Wenn es im `dev-standards`-Repository neue Änderungen gibt:

```bash
cd standards
git pull origin main
cd ..
git add standards
git commit -m "Update dev-standards submodule"
```

Nach dem Update `--setup` erneut ausführen, um neue Commands und Permissions zu synchronisieren:

```bash
python standards/scripts/maintain_tools.py --setup
```
