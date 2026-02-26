# dev-standards

Zentrale Sammlung von Entwicklungsstandards, Coding Guidelines und Quality-Gate-Werkzeugen. Dieses Repository wird als Git Submodule in Projekte eingebunden und stellt einheitliche Regeln für Code-Qualität, Architektur und AI-gestützte Entwicklung bereit.

## Inhalt

| Pfad | Beschreibung |
|------|-------------|
| `docs/ai_guidelines.md` | Globale AI Coding Standards (Quality Gates, Python Standards, Architektur-Patterns) |
| `docs/implementation.md` | Implementierungs-Richtlinien & Coding Standards (Naming, Typing, Error Handling) |
| `docs/architect_workflow.md` | Automatisierte Qualitätskontrolle mit der Architekten-Ampel |
| `docs/feature_development_workflow.md` | Feature-Entwicklungsprozess: Spezifikation → Prototyp → Architektur-Review → Code-Review |
| `scripts/maintain_tools.py` | Quality-Gate-Script: Komplexität (Radon), toter Code (Vulture), Duplikation (jscpd) |

## Voraussetzungen

Das Quality-Gate-Script (`scripts/maintain_tools.py`) benötigt folgende Tools:

| Tool | Zweck | Typ |
|------|-------|-----|
| **radon** | Zyklomatische Komplexität messen | Python-Paket |
| **vulture** | Toten Code erkennen | Python-Paket |
| **jscpd** | Code-Duplikation erkennen | Node.js-Paket (optional) |

### Automatische Installation (Empfohlen)

Das Script enthält ein `--setup` Flag, das alle Tools automatisch installiert:

```bash
python standards/scripts/maintain_tools.py --setup
```

Dies führt automatisch 3 Schritte aus:
1. **Python-Pakete** installieren: `radon`, `vulture`, `ruff`, `pyright`, `sqlfluff`
2. **Node.js/npm** installieren via `nodeenv` (falls npm nicht vorhanden)
3. **Node.js-Pakete** installieren: `jscpd`, `@biomejs/biome`, `knip`

### Manuelle Installation

```bash
# Python-Tools
pip install -U radon vulture ruff pyright sqlfluff

# Node.js-Tools
npm install --save-dev @biomejs/biome knip jscpd
```

---

# Git Submodule Setup

Diese Anleitung beschreibt, wie das Repository `dev-standards` als Submodule in ein Projekt integriert wird und wie andere Entwickler das Projekt korrekt auschecken.

## 1. Submodule hinzufügen

Um das externe Repository direkt in den Ordner `standards` zu laden, führe im Hauptverzeichnis des Projekts folgenden Befehl aus:

```bash
git submodule add https://github.com/StefanFVogel/dev-standards.git standards
```

## 2. Änderungen speichern (Commit & Push)

Damit das Haupt-Repository die Verknüpfung speichert, müssen die `.gitmodules`-Datei und der neue Ordner committet werden:

```bash
git add .gitmodules standards
git commit -m "Füge dev-standards als Submodule im Ordner 'standards' hinzu"
git push
```

---

## 3. Das Projekt auschecken / klonen (Für andere Entwickler)

Wenn das Projekt neu aufgesetzt oder von einem anderen Entwickler geklont wird, muss sichergestellt werden, dass auch die Inhalte des Submodules heruntergeladen werden.

**Variante A: Neues Klonen (Empfohlen)**
Hänge das Flag `--recurse-submodules` an den Clone-Befehl an, um das Hauptprojekt inklusive aller Submodule herunterzuladen:

```bash
git clone --recurse-submodules <deine-projekt-url.git>
```

**Variante B: Bereits geklont, aber Ordner 'standards' ist leer**
Falls das Projekt mit einem normalen `git clone` heruntergeladen wurde, bleibt der Ordner `standards` zunächst leer. Führe in diesem Fall im Projektverzeichnis folgenden Befehl aus, um das Submodule nachträglich zu laden:

```bash
git submodule update --init --recursive
```

---

## 4. Submodule aktualisieren (Optional)

Wenn es im `dev-standards`-Repository neue Änderungen gibt und du diese in dein Projekt übernehmen möchtest:

```bash
cd standards
git pull origin main
cd ..
git add standards
git commit -m "Aktualisiere dev-standards Submodule"
git push
```
