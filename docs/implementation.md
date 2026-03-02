# 💻 Implementation Guidelines & Coding Standards (Perfection Mode)

Dieses Dokument definiert die verbindlichen Standards für die Entwicklung in **allen Projekten**. Es ergänzt die automatisierten Checks aus `architect_workflow.md` und dient als Leitfaden für sauberen, wartbaren und sicheren Code.

---

## 1. 🛡️ Quality Gates & "The Architect"

Wir verlassen uns nicht auf guten Willen, sondern auf harte Metriken. Bevor Code gemerged wird, muss er die **Architekten-Ampel** (`standards/scripts/maintain_tools.py`) passieren.

### Die 3 Todsünden (Automatisch geprüft)
1.  **Zyklomatische Komplexität (Radon)**
    *   **Ziel:** CC ≤ 6 (Grün)
    *   **Limit:** CC < 10. Alles ab 10 ist **blockierend**.
    *   *Lösung:* Zerlege komplexe Funktionen. Nutze Early Returns. Vermeide tiefe Verschachtelung.
2.  **Toter Code (Vulture)**
    *   **Toleranz:** 0%.
    *   *Lösung:* Lösche ungenutzte Funktionen, Variablen und Importe sofort.
3.  **Code Duplikation (jscpd)**
    *   **Limit:** < 5%.
    *   *Lösung:* Extrahiere gemeinsame Logik in Hilfsfunktionen oder Basisklassen (DRY-Prinzip).

---

## 2. 🏗️ Architektur-Layer & Patterns

Wir folgen einer strikten **Hexagonal Architecture (Ports & Adapters)**.

### A. Application Core (Domain)
*   **Zweck:** Enthält die reine Business-Logik (Use Cases, Domain-Objekte).
*   **Regel:** **Keine externen Abhängigkeiten.** Kein `import fastapi`, `import sqlmodel`. Die Logik ist framework-agnostisch.
*   **Functional Core:** Business-Logik muss aus "Pure Functions" bestehen (keine Side-Effects, kein I/O).
*   **Value Objects:** Primitive Typen (`int`, `str`) sind verboten. Nutze Value Objects (`EmailAddress`, `OrderId`), die sich selbst validieren.

### B. Ports (Interfaces)
*   **Zweck:** Definieren die Verträge (abstrakte Interfaces/Protokolle), die der Application Core benötigt (z.B. `UserRepository`, `PaymentGateway`).

### C. Adapters (Infrastructure)
*   **Zweck:** Implementieren die Ports und kapseln die gesamte externe Kommunikation.
    *   **Driving Adapters:** `routers/`, `api/` (FastAPI, Flask)
    *   **Driven Adapters:** `repositories/`, `db/` (SQLModel, SQLAlchemy)
*   **Contract Testing:** Bei Microservice-Kommunikation müssen Consumer-Driven Contracts (z.B. Pact) genutzt werden.

---

## 3. 🐍 Python Coding Standards

Wir nutzen moderne Python (3.12+) Features.

### Naming Conventions (Sprechende Namen)
*   **Variablen:** `snake_case`. Namen müssen den **Inhalt** beschreiben, nicht den Typ.
*   **Funktionen:** `snake_case`. Müssen ein **Verb** enthalten.
*   **Klassen:** `PascalCase`. Substantive.
*   **Konstanten:** `UPPER_CASE`.

### Typing & Pydantic
*   **Type Hints:** Sind **Pflicht** für alle Funktionssignaturen (`def my_func(a: int) -> str:`).
*   **Strict Typing:** `Any` ist verboten. `Optional` darf nur verwendet werden, wenn `None` ein valider fachlicher Zustand ist.
*   **Immutability:** Alle Datenstrukturen (Pydantic Models, Dataclasses) müssen `frozen=True` sein.

### Error Handling & Logging
*   **Result Pattern:** Für erwartbare Fehler (z.B. "User nicht gefunden") dürfen **keine** Exceptions geworfen werden. Nutze einen `Result`-Typ (`Ok(value)` oder `Err(error)`). Exceptions sind nur für *unerwartete* Systemfehler (Panic).
*   **Custom Exceptions:** Verbot von generischen `ValueError`. Jedes Modul muss seine eigene Exception-Hierarchie definieren.
*   **Structured Logging (JSON):** Jede Log-Zeile *muss* Kontext enthalten (`logger.bind(user_id=uid).info("...")`), damit Logs in Kibana/Datadog filterbar sind.

---

## 4. 🛠️ Tooling & Workflow

### Formatierung (Automatisch via Pre-Commit)
*   **Formatter:** `ruff format` (Black-kompatibel, Line-Length 120).
*   **Imports:** `ruff check --select I` (isort).
*   **Linter:** `ruff check`.

### Der Entwickler-Loop
1.  Code schreiben (TDD: Test zuerst).
2.  `python standards/scripts/maintain_tools.py --mode commit` ausführen.
3.  Falls **ROT/GELB**: Refactoring durchführen (siehe `architect_workflow.md`).
4.  Tests ausführen: `pytest`.
5.  Commit (Conventional Commits).

---

## 5. 🟨 JavaScript Coding Standards (Frontend)

(Dieser Abschnitt ist optional und projektspezifisch anzupassen)

**Constraint:** Vanilla JS (ES2020+), No Build Step, No TypeScript, No Modules (sofern nicht anders definiert).

### Manager Pattern (Empfohlen)

Jede UI-Funktionalität sollte durch eine **Manager-Klasse** abgebildet werden:

```javascript
class FeatureManager {
    constructor() { /* State initialisieren */ }
    init() { /* Event-Listener binden */ }
    get $form() { return $(".feature-form"); }
}
```

### Quality Gates (JS-spezifisch)

| Tool | Zweck | Aufruf |
|------|-------|--------|
| **Biome** | Linter & Formatter | `npx biome lint <files>` |
| **jscpd** | Duplikat-Erkennung | `npx jscpd <files> --threshold 5` |
| **npm audit** | Security Scanning | `npm audit` |

---

## 6. 🌐 HTML & CSS Standards

### Data-Attribute als JS-Hooks (Zentrale Konvention)

**`data-*` Attribute sind die funktionalen Selektoren** — CSS-Klassen werden nur für Styling verwendet, nie als JS-Hook:

```html
<div class="d-none" data-table-container>...</div>
<button data-retry-loading>Erneut laden</button>
```

---

## 7. 📝 Dokumentation

*   **Docstrings:** Google Style Guide. Pflicht für alle Public Modules, Classes und Functions.
*   **Kommentare:** Erkläre das *Warum*, nicht das *Wie*. Der Code sollte selbsterklärend sein.
*   **LLM Prompts:** Prompts versionieren. Keine Hardcoded Prompts im Code.

---

## 8. 🚨 Checkliste für Code Reviews

Bevor du einen Pull Request erstellst oder Code als "fertig" markierst:

- [ ] `maintain_tools.py` zeigt **GRÜN**?
- [ ] Keine neuen `print()` Statements (nur structured logs)?
- [ ] Type Hints vollständig und strikt (kein `Any`)?
- [ ] Business-Logik ist von Frameworks entkoppelt (Hexagonal)?
- [ ] Erwartbare Fehler werden als `Result` zurückgegeben?
- [ ] Alle Datenstrukturen sind immutable (`frozen=True`)?
- [ ] Sprechende Variablennamen verwendet?
- [ ] Review-Checkliste aus `feature_development_workflow.md` abgehakt?
