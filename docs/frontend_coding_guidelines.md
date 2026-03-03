# Frontend Coding Guidelines

Dieses Dokument definiert die Coding-Standards und Best Practices für die Frontend-Entwicklung in diesem Projekt. Ziel ist es, einen konsistenten, wartbaren und qualitativ hochwertigen Code zu gewährleisten.

## 1. Architektur & Code-Struktur

- **Klassen-Dekomposition**: Große "Manager"-Klassen (Gott-Klassen) sind zu vermeiden. Jede Klasse sollte eine klare, abgegrenzte Zuständigkeit haben (Single Responsibility Principle).
  - **Beispiel**: Ein `AlertManager` wird aufgeteilt in `AlertTable`, `AlertWidget`, `AlertForm`. Der Manager selbst dient nur zur Orchestrierung.
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
- **CSS-Klassen für Sichtbarkeit**: Das Ein- und Ausblenden von Elementen erfolgt konsistent über das Hinzufügen/Entfernen von CSS-Klassen (z.B. Bootstrap `d-none`). Direkte jQuery-Methoden wie `.hide()`, `.show()` oder `.toggle()` sind zu vermeiden, es sei denn, sie werden für Animationen (`slide`) genutzt.

## 4. Konventionen & Clean Code

- **CSS-Anpassungen**: Eigene CSS-Regeln oder Überschreibungen gehören ausschließlich in die `resources/css/custom.css`. Die `style.css` wird nicht direkt bearbeitet.
- **DOM-Selektoren**:
  - **Keine Hardcoded Strings**: CSS-Selektoren dürfen nicht hartcodiert in Methoden verwendet werden. Stattdessen sind sie über Properties (Getter) am Anfang der Klasse zu definieren.
  - **`data-*`-Attribute für JS-Hooks**: Für die Selektion von Elementen per JavaScript sind `data-*`-Attribute zu verwenden (z.B. `data-alert-table`). ID-Selektoren (`#my-element`) sind nur erlaubt, wenn sie von einem Framework (z.B. Bootstrap für Modals) explizit benötigt werden.
- **Event-Handling**: Die Event-Registrierung erfolgt konsistent mit jQuery (`.on()`, `.click()`, etc.), um einen Mix aus nativer und jQuery-Schreibweise zu vermeiden.
- **Event-Driven Updates**: Komponenten sollen über Events kommunizieren, statt sich gegenseitig direkt aufzurufen. Ein `DataHub` oder ein globales Event-System (jQuery Events) kann hierfür genutzt werden. Eine Komponente feuert ein Event (z.B. `alerts:updated`), andere lauschen darauf und aktualisieren sich bei Bedarf selbst.
- **Magic Strings vermeiden**: Hartgecodierte, wiederkehrende Strings (z.B. `'loading'`, `'loaded'`, `'GT'`) müssen durch konstante Objekte (Enums) ersetzt werden.
- **Strict Mode & JSDoc**: Alle neuen JavaScript-Dateien müssen mit `'use strict';` beginnen. Klassen, Methoden und deren Parameter sind mit JSDoc zu dokumentieren, um die Code-Qualität und die Unterstützung durch die IDE zu verbessern.
