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

## 5. 🟨 JavaScript Coding Standards

Das Projekt nutzt **Vanilla JavaScript (ES2020+)** ohne TypeScript, ohne Module-System und ohne Build-Prozess. Dateien werden direkt per `<script>`-Tag geladen.

### Architektur

*   **Kein Module-System:** Kein `import`/`export`, kein `require`. Klassen liegen im globalen Namespace.
*   **Kein Build-Prozess:** Kein Webpack, Vite o.ä. Dateien werden as-is ausgeliefert.
*   **Kein TypeScript:** Reines JavaScript.
*   **Abhängigkeiten:** jQuery 3.6, Bootstrap 5, Plotly, DataTables, Marked.js — als minifizierte Bundles eingebunden.

### Manager Pattern (Zentrale Konvention)

Jede UI-Funktionalität wird durch eine **Manager-Klasse** abgebildet mit einheitlicher Struktur:

```javascript
class PortfolioManager {
    constructor() { /* State initialisieren */ }
    init() { /* Event-Listener binden */ }

    // jQuery-Selektoren als Getter (lazy)
    get $form() { return $(".portfolio-form"); }
    get $transactionId() { return this.$form.find('.transactionId'); }

    // Zwei-Wege-Binding
    bindToView = (data) => { this.$transactionId.val(data.id ?? ''); }
    bindFromView = () => { return { id: this.$transactionId.val() }; }
}
```

*   **Singleton-Registrierung:** `window.PortfolioManager = new PortfolioManager();`
*   **Daten-Hub:** `DataHub` als zentraler Observer für komponentenübergreifende Events.

### Naming Conventions

| Element | Konvention | Beispiel |
|---------|-----------|----------|
| Klassen | `PascalCase` | `ConversationsManager`, `DataHub` |
| Methoden / Funktionen | `camelCase` | `setFavourites()`, `bindToView()` |
| Private Properties | `_` Prefix | `_favourites`, `_pendingUpdate` |
| jQuery-Referenzen | `$` Prefix | `$messagesContainer`, `$userPromptInput` |
| Konstanten | `UPPER_CASE` | `MAX_RETRIES` |

### ES2020+ Features (erlaubt)

*   Arrow Functions: `const fn = (x) => x * 2`
*   Template Literals: `` `Hallo ${name}` ``
*   Optional Chaining: `obj?.nested?.value`
*   Nullish Coalescing: `value ?? defaultValue`
*   `const` / `let` (kein `var`)
*   Array-Methoden: `.map()`, `.filter()`, `.find()`, `.some()`, `.every()`

### Verboten / Vermeiden

*   ❌ `var` — immer `const` oder `let`
*   ❌ `async/await` — wird nicht verwendet; AJAX via jQuery `$.ajax()` mit Callbacks/Promises
*   ❌ ES-Module (`import`/`export`) — nicht kompatibel mit der Lade-Architektur
*   ❌ Neue npm-Runtime-Dependencies — nur Dev-Tools (Biome, jscpd, Knip)
*   ❌ Inline-`<script>`-Blöcke in HTML — JS gehört in separate Dateien unter `resources/js/`

### Dateistruktur

```
resources/
├── js/                      # Frontend-JS
│   ├── data-hub.js          # Zentraler Observer (Singleton)
│   ├── *-manager.js         # Feature-Manager (je einer pro UI-Bereich)
│   ├── alert-init.js        # Alert-Widget
│   ├── custom.js            # Theme-Toggle, responsive UI
│   ├── PWA_init.js          # Service-Worker-Registration
│   └── PWA_sw.js            # Service-Worker (Network-First)
├── admin/js/                # Admin-spezifische Manager
└── vendor/                  # Third-Party Libs (minifiziert)
```

### Quality Gates (JS-spezifisch)

| Tool | Zweck | Aufruf |
|------|-------|--------|
| **Biome** | Linter & Formatter | `npx biome lint <files>` |
| **jscpd** | Duplikat-Erkennung | `npx jscpd <files> --threshold 5` |
| **Knip** | Dead Code & Unused Deps | `npx knip` |

Alle drei werden via `maintain_tools.py` automatisch geprüft.

### Script-Ladereihenfolge (kritisch!)

Da kein Module-System existiert, ist die Reihenfolge der `<script>`-Tags in HTML-Templates entscheidend:

1. jQuery + jQuery UI
2. Bootstrap Bundle
3. Third-Party Libs (Plotly, DataTables, etc.)
4. `data-hub.js` (stellt `window.DataHub` bereit)
5. Feature-Manager (`*-manager.js`)
6. Init-Skripte (`alert-init.js`, `custom.js`)

---

## 6. 🌐 HTML & CSS Standards

Das Projekt nutzt **Jinja2** (via FastAPI `Jinja2Templates`) mit **Bootstrap 5** als CSS-Framework. Es gibt genau 3 selbstständige HTML-Templates — keine Template-Vererbung (`extends`/`block`).

### Template-Architektur

*   **Engine:** Jinja2, registriert in `stock_buddy/routers/pages.py`
*   **Templates:** `templates/index.html` (App), `templates/admin.html` (Admin), `templates/stripe-callback.html` (Payment)
*   **Keine Vererbung:** Kein `{% extends %}`, `{% block %}`, `{% include %}`. Jede Seite ist eigenständig.
*   **Jinja2-Nutzung minimal:** Nur `{% if %}` für Role-Gating und `{{ variable }}` für Context-Werte.
*   **Sprache:** `lang="de"` — alle UI-Texte sind Deutsch.

### Seitenstruktur

Beide Haupt-Templates folgen demselben Scaffold:

```html
<!DOCTYPE html>
<html lang="de">
<head>
    <!-- CSS Links -->
    <!-- JS Scripts (außer Bootstrap Bundle) -->
</head>
<body class="show-menu show-sidebar" callback="{{ callback }}">
    <main class="page-wrapper d-flex position-relative">
        <header class="page-header">...</header>      <!-- Linke Sidebar -->
        <section class="page-body flex-grow-lg-1">     <!-- Hauptinhalt -->
            ...
        </section>
        <aside class="page-sidebar">...</aside>        <!-- Rechte Sidebar -->
    </main>

    <!-- Alle Modals außerhalb von <main> -->
    <div class="modal fade ...">...</div>

    <script src="bootstrap.bundle.min.js"></script>
</body>
```

*   **`<body>`-Attribute:** App-State wird über Attribute am `<body>`-Tag übergeben (`callback="{{ callback }}"`), von JS gelesen.
*   **Modals:** Immer außerhalb von `<main>`, am Ende des `<body>`.

### CSS-Konventionen

*   **Framework:** Bootstrap 5 Utility-Klassen durchgängig (`d-flex`, `mt-3`, `col-md-4`, `btn btn-primary`).
*   **Custom CSS:** Flache CSS-Dateien mit modernem CSS-Nesting (kein SCSS).
*   **Zwei CSS-Stacks:** `resources/css/` (App, Barlow-Font) und `resources/admin/css/` (Admin, Ubuntu-Font).
*   **CSS-Variablen:** Markenfarben in `:root`:
    ```css
    :root {
      --white: #fff;
      --black: #333333;
      --blue: #1d3a8e;
      --pink: #e93aa6;
    }
    ```
*   **Sichtbarkeit:** Bootstrap `d-none` Klasse via JS toggeln. Kein `style="display:none"` verwenden.

### CSS-Ladereihenfolge

1. Google Fonts / `css2.css`
2. Font Awesome (`font-awesome.all.min.css`)
3. Bootstrap (`bootstrap.min.css`)
4. jQuery UI, DataTables CSS
5. `style.css` (Layout-System)
6. `custom.css` (Komponenten-Overrides)

### Data-Attribute als JS-Hooks (Zentrale Konvention)

**`data-*` Attribute sind die funktionalen Selektoren** — CSS-Klassen werden nur für Styling verwendet, nie als JS-Hook:

```html
<!-- HTML: State-Container mit data-Attribut -->
<div class="d-none" data-alerts-table-container>...</div>
<button data-retry-loading-alerts>Erneut laden</button>
```

```javascript
// JS: Selektion immer über data-Attribut
$('[data-alerts-table-container]').removeClass('d-none');
$(document).on('click', '[data-retry-loading-alerts]', handler);
```

*   **Naming:** `data-kebab-case-beschreibung`, optional mit `="true"`.
*   **Daten-Transport:** Komplexe Werte als data-Attribut-Werte (`data-kpis="..."`, `data-chart-title="..."`).
*   **Bootstrap-Interop:** `data-bs-toggle`, `data-bs-target`, `data-bs-dismiss` für Bootstrap-Komponenten.

### Icons: Font Awesome

Font Awesome 5/6 ist das einzige Icon-System. Beide Prefix-Varianten koexistieren:

```html
<i class="fas fa-users-cog"></i>                           <!-- FA5 Solid -->
<i class="fa-solid fa-circle-check"></i>                   <!-- FA6 Solid -->
<i class="far fa-file-pdf"></i>                            <!-- Regular -->
<i class="fa fa-spinner fa-pulse"></i>                     <!-- Spinner -->
<i class="fa-solid fa-arrow-trend-up text-success ms-1"></i>  <!-- + Bootstrap Utility -->
```

*   Keine SVG-Sprites, keine Bootstrap Icons.
*   Icons auch in JS-Template-Literals erlaubt.

### Modal-Pattern

Bootstrap 5 Modal-Struktur, einheitlich:

```html
<div class="modal fade" id="create-alert-modal" tabindex="-1"
     aria-labelledby="..." aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">...</h5>
                <button type="button" class="btn-close"
                        data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">...</div>
            <div class="modal-footer">
                <button class="btn btn-secondary" data-bs-dismiss="modal">Abbrechen</button>
                <button class="btn btn-primary save-button">Speichern</button>
            </div>
        </div>
    </div>
</div>
```

*   Immer `modal-dialog-centered`.
*   Identifikation über semantische Klasse oder `id`.

### Formular-Pattern

Bootstrap 5 Grid-basiert:

```html
<div class="row g-3 mb-3">
    <div class="col-md-4">
        <label class="form-label">Startdatum</label>
        <input type="date" class="form-control" data-report-start-date="true">
    </div>
</div>
```

*   **Selektoren in Modals:** Semantische Klassen (`.prompt-text`, `.kpi-code`) für `bindToView`/`bindFromView`.
*   **Hidden Inputs:** `<input type="hidden" class="prompt-id">` für IDs.

### Plotly-Chart-Einbettung

Plotly 2.29.1 ist lokal gebundled. Charts werden vom LLM als HTML-Tag im Response-Text geliefert:

```html
<div class="plotly" id="{mid}" src="/get_plot_data" plotdata="{json}"></div>
```

JS scannt nach `.plotly`-Elementen und rendert via `Plotly.newPlot()`.

### Cache Busting

Alle lokalen Assets nutzen den Query-String `?v={{ resources_version }}`:

```html
<link href="../resources/css/style.css?v={{ resources_version }}" rel="stylesheet">
<script src="../resources/js/custom.js?v={{ resources_version }}"></script>
```

### Email-HTML (Sonderfall)

Email-Templates nutzen Jinja2 als **Inline-String-Templates** in `email_templates.py` (nicht file-basiert). Komplett Inline-Styles (email-safe), kein externes CSS.

### Verboten / Vermeiden

*   ❌ `{% extends %}` / `{% block %}` / `{% include %}` — Architektur ist flat, keine Vererbung
*   ❌ CSS-Klassen als JS-Hooks — immer `data-*` Attribute verwenden
*   ❌ Inline `style="display:none"` — Bootstrap `d-none` verwenden
*   ❌ Neue CSS-Frameworks oder Icon-Libraries — Bootstrap 5 + Font Awesome
*   ❌ SCSS / SASS — Plain CSS mit CSS-Nesting
*   ❌ Externe CDN-Links für lokale Assets — alles lokal bundlen mit Cache-Busting

---

## 7. 📝 Dokumentation

*   **Docstrings:** Google Style Guide. Pflicht für alle Public Modules, Classes und Functions.
*   **Kommentare:** Erkläre das *Warum*, nicht das *Wie*. Der Code sollte selbsterklärend sein.
*   **LLM Prompts:** Prompts in `stock_buddy/prompts/` versionieren. Keine Hardcoded Prompts im Code.

---

## 8. 🚨 Checkliste für Code Reviews

Bevor du einen Pull Request erstellst oder Code als "fertig" markierst:

- [ ] `maintain_tools.py` zeigt **GRÜN**?
- [ ] Keine neuen `print()` Statements (nutze Logger)?
- [ ] Type Hints vollständig?
- [ ] Keine Business-Logik im Router?
- [ ] Asynchrone DB-Zugriffe verwendet?
- [ ] Docstrings für LLM-Tools verständlich?
- [ ] Sprechende Variablennamen verwendet? (keine Einbuchstaben, keine Abkürzungen, kein generisches `result`)
- [ ] JS: Manager-Pattern eingehalten? (Getter für Selektoren, `bindToView`/`bindFromView`)
- [ ] JS: Kein `var`, keine ES-Module, keine neuen npm-Runtime-Deps?
- [ ] JS: Script-Ladereihenfolge in HTML-Templates korrekt?
- [ ] HTML: `data-*` Attribute als JS-Hooks (keine CSS-Klassen)?
- [ ] HTML: Sichtbarkeit via `d-none` (kein Inline `style="display:none"`)?
- [ ] HTML: Cache-Busting `?v={{ resources_version }}` auf neuen Assets?
- [ ] HTML: Modals außerhalb `<main>`, mit `modal-dialog-centered`?
