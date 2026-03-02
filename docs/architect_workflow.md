# 🏗️ AI Architect Workflow: Deep Code Quality & Guardrails (Perfection Mode)

Dieses Dokument beschreibt das Verfahren zur automatisierten Qualitätskontrolle. Es kombiniert statische Code-Analyse mit einer **"Architekten-Ampel"**, um objektiv zu messen, ob Code den Standards für Wartbarkeit, Sicherheit und Design-Patterns entspricht.

---

## 🛠️ 1. Vorbereitung (Einmalig)

Das Quality-Gate-Script liegt unter `standards/scripts/maintain_tools.py` und nutzt folgende Sensoren:

| Tool | Zweck | Grenzwert (Strict Mode) |
|------|-------|-----------|
| **Radon** | Zyklomatische Komplexität (Python) | CC ≤ 6 (Gelb), CC < 10 (Rot) |
| **Vulture** | Toter Code (Python) | 0% Toleranz |
| **jscpd** | Code-Duplikation (Alle) | < 5% |
| **Biome** | Linter & Komplexität (JS/TS) | Cognitive Complexity ≤ 15 |
| **djLint** | HTML Linter | Keine Fehler |
| **Bandit** | Security Scanning (Python) | Keine High/Medium Issues |
| **npm audit** | Security Scanning (JS) | Keine High/Critical Issues |
| **interrogate** | Docstring Coverage | 100% für Public API |

### Tools installieren

Alle benötigten Tools lassen sich mit einem einzigen Befehl installieren:

```bash
python standards/scripts/maintain_tools.py --setup
```

Dies führt automatisch 3 Schritte aus:
1. **Python-Pakete** installieren (via pip): `radon`, `vulture`, `ruff`, `pyright`, `sqlfluff`, `djlint`, `bandit`, `interrogate`
2. **Node.js/npm** installieren via `nodeenv` (falls npm nicht vorhanden)
3. **Node.js-Pakete** installieren (via npm): `jscpd`, `@biomejs/biome`, `knip`

---

## 🔄 2. Der Review-Zyklus (in Claude Code)

1. **Analyse starten:**
`run python standards/scripts/maintain_tools.py --mode commit` (oder `branch` / `yesterday`)
2. **Den Architekten-Prompt nutzen:**
> "Agiere als **Senior Python Architekt**. Analysiere die Ergebnisse der **Architekten-Ampel**:


> 1. Bei **Toter Code = ROT**: Lösche ungenutzte Elemente sofort.
> 2. Bei **Komplexität = GELB/ROT**: Brich Spaghetti-Logik auf (Single Responsibility).
> 3. Bei **Duplikate = ROT**: Erstelle Abstraktionen (DRY-Prinzip).
> 4. **Patterns**: Schlage Factory, Strategy oder Repository Patterns vor, wo sinnvoll.
> 5. **Security**: Behebe alle Bandit/npm audit Issues sofort.
> Zeig mir die Top-Prioritäten und starte das Refactoring."
> 
> 



---

## 🎯 3. Goldene Regeln für den Review

* **Kein Spaghetti:** Funktionen mit einem Radon-Rating von **B** oder schlechter (>6) müssen aufgeteilt werden.
* **Toter Code ist Ballast:** Variablen oder Funktionen, die nicht von Tests oder der App genutzt werden, fliegen sofort raus.
* **Variable Hygiene:** Keine Variablen "auf Vorrat". Redundanter State wird eliminiert.
* **SOLID-Fokus:** Jede Klasse/Funktion hat genau **eine** klar definierte Aufgabe.
* **Architecture Linting:** Layer-Verletzungen (z.B. Repository importiert Router) sind verboten.
* **Security First:** Keine bekannten Sicherheitslücken (CVEs) in Dependencies.

---

## 📈 4. Refactoring-Strategie

1. **Entwurf prüfen:** Lass dir von Claude erst das neue Interface oder Pattern-Design erklären.
2. **Iterative Umsetzung:** Bearbeite erst den Toten Code, dann die Komplexität, dann die Patterns.
3. **Abschluss-Check:** Nach dem Refactoring das Skript erneut laufen lassen, um die **GRÜNE Ampel** zu bestätigen.
