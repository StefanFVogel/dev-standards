# 💻 Implementation Guidelines & Coding Standards

Dieses Dokument definiert die verbindlichen Standards für die Entwicklung in **StockBuddyAlerts**. Es ergänzt die automatisierten Checks aus `architect_workflow.md` und dient als Leitfaden für sauberen, wartbaren Code.

---

## 1. 🛡️ Quality Gates & "The Architect"

Wir verlassen uns nicht auf guten Willen, sondern auf harte Metriken. Bevor Code gemerged wird, muss er die **Architekten-Ampel** (`scripts/maintain_tools.py`) passieren.

### Die 3 Todsünden (Automatisch geprüft)
1.  **Zyklomatische Komplexität (Radon)**
    *   **Ziel:** CC ≤ 10 (Grün)
    *   **Limit:** CC < 20. Alles ab 20 ist **blockierend**.
    *   *Lösung:* Zerlege komplexe Funktionen. Nutze Early Returns. Vermeide tiefe Verschachtelung.
2.  **Toter Code (Vulture)**
    *   **Toleranz:** 0%.
    *   *Lösung:* Lösche ungenutzte Funktionen, Variablen und Importe sofort.
3.  **Code Duplikation (jscpd)**
    *   **Limit:** < 5%.
    *   *Lösung:* Extrahiere gemeinsame Logik in Hilfsfunktionen oder Basisklassen (DRY-Prinzip).

---

## 2. 🏗️ Architektur-Layer & Patterns

Wir folgen einer strikten Trennung der Verantwortlichkeiten (Separation of Concerns).

### A. API Layer (`stock_buddy/routers/`)
*   **Zweck:** HTTP-Handling, Validierung, Routing.
*   **Regel:** **Keine Business-Logik** in Routern!
*   **Pattern:** Dependency Injection (FastAPI `Depends`) für Services und Repositories nutzen.

### B. Business Logic & LLM (`stock_buddy/llm/`, `stock_buddy/llm_tools/`)
*   **Agenten:** Nutzen das **ReAct Pattern** (Reasoning + Acting).
*   **Tools:**
    *   Müssen von `LlamaIndex FunctionTool` erben.
    *   **Docstrings sind funktionaler Code!** Das LLM nutzt sie, um das Tool zu verstehen. Sei präzise.
    *   Rückgabewerte müssen strukturiert und LLM-freundlich sein (JSON/Text).

### C. Data Access (`stock_buddy/repositories/`)
*   **Pattern:** Repository Pattern.
*   **Tech:** SQLModel (SQLAlchemy Core + Pydantic).
*   **Regel:** Datenbank-Queries gehören **ausschließlich** hierher. Niemals SQL in Routern oder Tools.
*   **Async:** Alle DB-Operationen müssen `async/await` nutzen.

---

## 3. 🐍 Python Coding Standards

Wir nutzen moderne Python (3.12+) Features.

### Naming Conventions (Sprechende Namen)
*   **Variablen:** `snake_case`. Namen müssen den **Inhalt** beschreiben, nicht den Typ.
    *   ❌ `d = get_data()`
    *   ✅ `stock_prices = get_stock_prices()`
    *   ❌ `l = []`
    *   ✅ `active_users = []`
*   **Keine Einbuchstaben-Variablen** — außer `i`, `j`, `k` als Loop-Counter oder `_` für explizit ignorierte Werte.
    *   ❌ `c` in Comprehensions → ✅ `constraint`
    *   ❌ `x` → ✅ den tatsächlichen Inhalt benennen
*   **Keine kryptischen Abkürzungen.** Der Name muss ohne Kontextsprung verständlich sein.
    *   ❌ `sub`, `subs` → ✅ `subscriber`, `subscribers`
    *   ❌ `cs` → ✅ `cumulative_score`
    *   ❌ `uid` → ✅ `user_id`
    *   ❌ `xss_name` → ✅ `xss_payload` (beschreibt den Inhalt, nicht den Typ)
*   **Rückgabewerte sprechend benennen.** `result` ist selten aussagekräftig — der Name soll verraten, *was* zurückkommt.
    *   ❌ `result = await resolve_user_email(...)` → ✅ `email = await resolve_user_email(...)`
    *   ❌ `result = await get_current_price(...)` → ✅ `price_data = await get_current_price(...)`
    *   ❌ `result = await manager.update_settings(...)` → ✅ `updated_settings = await manager.update_settings(...)`
*   **Funktionen:** `snake_case`. Müssen ein **Verb** enthalten.
    *   ❌ `user()`
    *   ✅ `get_user()`, `calculate_score()`, `validate_input()`
*   **Klassen:** `PascalCase`. Substantive.
    *   ✅ `StockAnalyzer`, `UserRepository`
*   **Konstanten:** `UPPER_CASE`.
    *   ✅ `MAX_RETRY_ATTEMPTS = 3`

### Typing & Pydantic
*   **Type Hints:** Sind **Pflicht** für alle Funktionssignaturen (`def my_func(a: int) -> str:`).
*   **Pydantic:** Nutze Pydantic Models für Datenaustausch und Validierung.
*   **SQLModel:** Trenne Datenbank-Modelle (`table=True`) von API-Schemas (DTOs), wo nötig.

### Async / Await
*   FastAPI ist asynchron. Blockierende Calls (z.B. `requests`, `time.sleep`) sind verboten.
*   Nutze `httpx` statt `requests`.
*   Nutze `asyncio.sleep` statt `time.sleep`.

### Error Handling
*   Nutze `try/except` gezielt, nicht pauschal (`except Exception: pass` ist verboten).
*   Wirf spezifische HTTP-Exceptions (`HTTPException`) in Routern.
*   Logge Fehler mit `loguru` (nicht `print`).

---

## 4. 🛠️ Tooling & Workflow

### Formatierung (Automatisch via Pre-Commit)
*   **Formatter:** `ruff format` (Black-kompatibel, Line-Length 120).
*   **Imports:** `ruff check --select I` (isort).
*   **Linter:** `ruff check`.

### Der Entwickler-Loop
1.  Code schreiben.
2.  `python scripts/maintain_tools.py --mode commit` ausführen.
3.  Falls **ROT/GELB**: Refactoring durchführen (siehe `architect_workflow.md`).
4.  Tests ausführen: `pytest`.
5.  Commit.

### Tool-Aufrufe für den Architekten
Um den Code gegen die Standards zu prüfen, nutze folgende Befehle:

*   **Nur letzte Änderungen (Default):**
    ```bash
    python scripts/maintain_tools.py --mode commit
    ```
*   **Ganzen Branch gegen Main:**
    ```bash
    python scripts/maintain_tools.py --mode branch
    ```
*   **Änderungen seit Gestern:**
    ```bash
    python scripts/maintain_tools.py --mode yesterday
    ```
*   **Alles prüfen (Full Scan):**
    ```bash
    python scripts/maintain_tools.py --mode all
    ```

---

## 5. 📝 Dokumentation

*   **Docstrings:** Google Style Guide. Pflicht für alle Public Modules, Classes und Functions.
*   **Kommentare:** Erkläre das *Warum*, nicht das *Wie*. Der Code sollte selbsterklärend sein.
*   **LLM Prompts:** Prompts in `stock_buddy/prompts/` versionieren. Keine Hardcoded Prompts im Code.

---

## 6. 🚨 Checkliste für Code Reviews

Bevor du einen Pull Request erstellst oder Code als "fertig" markierst:

- [ ] `maintain_tools.py` zeigt **GRÜN**?
- [ ] Keine neuen `print()` Statements (nutze Logger)?
- [ ] Type Hints vollständig?
- [ ] Keine Business-Logik im Router?
- [ ] Asynchrone DB-Zugriffe verwendet?
- [ ] Docstrings für LLM-Tools verständlich?
- [ ] Sprechende Variablennamen verwendet? (keine Einbuchstaben, keine Abkürzungen, kein generisches `result`)
