# Frontend Coding Guidelines

Dieses Dokument definiert die Coding-Standards und Best Practices für die Frontend-Entwicklung in diesem Projekt. Ziel ist es, einen konsistenten, wartbaren und qualitativ hochwertigen Code zu gewährleisten.

## 1. Architektur & Code-Struktur

- **Klassen-Dekomposition**: Große "Manager"-Klassen (Gott-Klassen) sind zu vermeiden. Jede Klasse sollte eine klare, abgegrenzte Zuständigkeit haben (Single Responsibility Principle).
  - **Beispiel**: Ein `AlertManager` wird aufgeteilt in `AlertTable`, `AlertWidget`, `AlertForm`. Der Manager selbst dient nur zur Orchestrierung.
- **Datei-Organisation**: Eine Klasse pro Datei, benannt in kebab-case (`alert-form.js` → `AlertForm`, `alert-table.js` → `AlertTable`).
- **Wiederverwendbare Komponenten**: Logik, die an mehreren Stellen benötigt wird (z.B. Instrumenten-Suche), muss in eigene, wiederverwendbare Klassen ausgelagert werden (z.B. `InstrumentAutocomplete`).
- **Utils-Klasse**: Globale Hilfsfunktionen (z.B. `_escapeHtml`) gehören in eine zentrale `Utils`-Klasse und nicht als lose Funktionen in eine Datei.

## 2. API & Backend-Kommunikation

- **Authentifizierung**: Die Authentifizierung erfolgt über Cookies. Manuelles Setzen von `Authorization`-Headern in `$.ajax`-Aufrufen ist nicht notwendig und zu unterlassen.
- **REST-Konventionen**: Endpoints müssen RESTful sein.
  - **Falsch**: `POST /alerts/manual`
  - **Richtig**: `POST /alerts` (Der Typ wird im Body oder serverseitig bestimmt).
- **Redundanz vermeiden**: Vorhandene Endpoints müssen wiederverwendet werden. Beispiel: Die Abfrage von Live-Preisen erfolgt ausschließlich über den Batch-fähigen Endpoint `./instrument-prices`.
- **Methoden-Signaturen**: Funktionen, die Daten an einen Endpoint senden (z.B. `createAlert`), sollten ein Objekt als Parameter akzeptieren, keine lange Liste von Einzelargumenten. Das verbessert die Skalierbarkeit.

## 3. UI, State Management & UX

- **Kein Optimistic UI**: Um die Komplexität zu reduzieren, wird auf Optimistic UI verzichtet. Nach einer erfolgreichen Add/Edit/Delete-Aktion werden die Daten vom Server neu geladen (Re-Fetch).
- **Inline-Bestätigungen**: Für Lösch-Aktionen ist eine Inline-Bestätigung (wie bei den Portfolio-Transaktionen) anstelle des nativen `confirm()`-Dialogs zu verwenden.
- **CSS-Klassen für Sichtbarkeit**: Das Ein- und Ausblenden von Elementen erfolgt konsistent über `d-none` (Bootstrap). Für Animationen: `show('slide')`/`hide('slide')` (jQuery). **Kein Mix** aus `d-none` und `slideUp/slideDown` — bei Übergängen: erst `removeClass('d-none').hide()`, dann `.slideDown()`.
- **Spinner-Pattern**: Save-Spinner als `<div class="d-none ...-spinner">`, Buttons mit `addClass('d-none')` verstecken während Save läuft (`_onBeginSave`/`_onFinishSave`). Preis-Lade-Spinner als eigenes `<div>` neben dem Preis-Feld, Feld mit `.hide()`/`.show()` togglen.
- **Fehler-Anzeige**: Server-Fehler auf Feldern via `_reportErrorViaTooltip()` (Bootstrap Tooltip, auto-dispose nach 5s). Kein `alert()`, kein `confirm()`, keine inline Alert-Banner in Formularen.

## 4. Konventionen & Clean Code

- **CSS-Anpassungen**: Eigene CSS-Regeln oder Überschreibungen gehören ausschließlich in die `resources/css/custom.css`. Die `style.css` wird **nie** direkt bearbeitet. Modul-spezifisches CSS (Alerts, Portfolio-Overrides) wird in `custom.css` gruppiert nach Modul.
- **DOM-Selektoren** — zwei Patterns je nach Komponenten-Typ:
  - **Form-Komponenten** (`TransactionForm`, `AlertForm`): CSS-Klassen-Selektoren via jQuery getters (`get $instrumentName() { return this.$form.find('.instrument'); }`). HTML wird dynamisch via `get template()` erzeugt — nur ein `<div data-*-host></div>` Platzhalter in `index.html`.
  - **Table/Widget/Manager-Komponenten** (`AlertTable`, `AlertWidget`, `AlertManager`): `static get SEL_*()` Konstanten mit `data-*`-Attributen (z.B. `data-alerts-modal-list`).
  - **Keine Hardcoded Strings**: Selektoren dürfen nie hartcodiert in Methoden stehen.
  - **IDs nur für Bootstrap**: ID-Selektoren (`#my-element`) nur wenn von Bootstrap explizit benötigt (z.B. Modals).
- **Form-Pattern** (Referenz: `TransactionForm` in `portfolio-manager.js`):
  - `get template()` — dynamischer HTML-String, kein statisches HTML in `index.html`
  - Kein `<form>`-Tag — Save via `$saveButton.click()`, Cancel via `$cancelButton.click()`
  - `open({ onCancel, onSave, showMode })` — Callback-basiert, kein Hardcoding
  - `bindFromView()` — sammelt Formulardaten als Objekt
  - `_resetForm()` — setzt alle Felder zurück
  - Generische Validierung: `validateField()`, `validateRequiredField()`, `validatePositiveValueField()`, `markAsValid()`, `markAsInvalid()`, `markFieldsAsValid()`
  - `render($container)` / `show()` / `hide()` / `destroy()` Lifecycle
- **Event-Handling**: Die Event-Registrierung erfolgt konsistent mit jQuery. In Form-Komponenten: direkte `.click()` auf jQuery-Objekte. In Table/Manager: delegierte `.on()` Events auf Container.
- **Event-Driven Updates**: Komponenten sollen über Events kommunizieren, statt sich gegenseitig direkt aufzurufen. Ein `DataHub` oder ein globales Event-System (jQuery Events) kann hierfür genutzt werden.
- **Magic Strings vermeiden**: Hartgecodierte, wiederkehrende Strings (z.B. `'loading'`, `'loaded'`, `'GT'`) müssen durch konstante Objekte (Enums) ersetzt werden.
- **Strict Mode & JSDoc**: Alle neuen JavaScript-Dateien müssen mit `'use strict';` beginnen. Klassen, Methoden und deren Parameter sind mit JSDoc zu dokumentieren.
