# 🚀 Deployment Checklist

Dieses Dokument definiert den verbindlichen Standard für **Deployment-Dokumentation**. Jedes Feature, das Infrastruktur-Änderungen erfordert, muss ein `<feature>_deployment.md` im `docs/`-Verzeichnis des Projekts erstellen.

---

## 📋 Wann ist ein Deployment-Dokument Pflicht?

Ein `_deployment.md` ist **Pflicht**, sobald mindestens eine der folgenden Bedingungen zutrifft:

| Kategorie | Beispiel |
|-----------|----------|
| Neue Cloud-Komponenten | Service Bus, Redis Cache, Storage Account, Lambda/Functions |
| Neue Berechtigungen (IAM) | Managed Identity Rollen, Access Policies |
| Neue Environment-Variablen | Feature Flags, Konfigurationswerte |
| Neue Secrets | API Keys, Connection Strings (KeyVault Referenzen) |
| Datenbank-Änderungen | Neue Tabellen, Spalten, Constraints, Indizes |
| Neue Pods/Services | Standalone Consumer, Worker, CronJob |
| Externe Abhängigkeiten | Neue NuGet/PyPI/npm Packages mit nativen Dependencies |
| Konfigurationsänderungen | Kubernetes Manifests, Helm Values, Docker Compose |
| DNS/Networking | Neue Endpoints, Ingress-Regeln, Firewall-Freischaltungen |

---

## 📄 Dateikonvention

```
docs/<feature>_deployment.md
```

Beispiel: `docs/alert_deployment.md`

---

## 📐 Pflicht-Sektionen

Jedes Deployment-Dokument muss die folgenden Sektionen enthalten. Nicht zutreffende Sektionen werden mit "Entfällt" markiert, nicht gelöscht.

### 1. Übersicht

Kurzbeschreibung: Welches Feature wird deployed und welche Infrastruktur-Änderungen sind nötig?

```markdown
## Übersicht

Feature: Kursalarme (Price Alerts)
Branch: feature/alerts
Betroffene Umgebungen: DEV, PROD
```

### 2. Cloud-Komponenten (Azure/AWS/GCP)

Neue oder geänderte Cloud-Ressourcen mit den exakten CLI-Befehlen zur Erstellung.

```markdown
## Cloud-Komponenten

### Service Bus (Beispiel)

| Ressource | Typ | Name | Namespace |
|-----------|-----|------|-----------|
| Topic | Service Bus Topic | `portfolio_events` | `sb-prod` |

**Erstellen:**

\```bash
az servicebus topic create ...
\```
```

### 3. IAM / Role Assignments

Neue Berechtigungen (RBAC), die für Managed Identities oder User/Groups vergeben werden müssen.

```markdown
## IAM / Role Assignments

| Principal (Wer?) | Rolle (Was?) | Scope (Wo?) | Begründung |
|------------------|--------------|-------------|------------|
| `mi-app-aks` | `Data Sender` | Topic `portfolio_events` | Pod muss Events senden dürfen |
```

### 4. Environment-Variablen

Alle neuen oder geänderten Umgebungsvariablen mit Beschreibung und Quelle.

```markdown
## Environment-Variablen

| Variable | Beschreibung | Pflicht | Quelle | Beispiel |
|----------|-------------|---------|--------|----------|
| `SERVICE_BUS_TOPIC` | Topic-Name | Nein | Konfiguration | `portfolio_events` |
```

### 5. Secrets / KeyVault

**Wichtig:** Niemals echte Secrets (Passwörter, Keys) in dieses Dokument schreiben! Nur Referenzen oder KeyVault-Namen.

```markdown
## Secrets

| Secret Name (KeyVault) | Env-Variable im Pod | Typ | Rotation |
|------------------------|---------------------|-----|----------|
| `SendGridApiKey` | `SERVICE_EMAIL_API_KEY` | API Key | Manuell (1x Jahr) |
```

### 6. Datenbank-Änderungen (SQL)

Alle DDL-Statements, die manuell oder per Migration auf der Datenbank ausgeführt werden müssen. **Reihenfolge beachten!**

```markdown
## Datenbank-Änderungen

**Reihenfolge:** Statements müssen in der angegebenen Reihenfolge ausgeführt werden.

| # | Typ | Tabelle | Statement | Rollback |
|---|-----|---------|-----------|----------|
| 1 | ALTER TABLE | UserConfig | `ALTER TABLE UserConfig ADD deleted_at DATETIME NULL;` | `ALTER TABLE UserConfig DROP COLUMN deleted_at;` |
```

### 7. Kubernetes / Pods / Docker

Neue oder geänderte Deployments, Services, CronJobs.

```markdown
## Kubernetes / Pods

### Neue Deployments

| Name | Image | Replicas | Command | Ressourcen |
|------|-------|----------|---------|------------|
| `consumer` | `app:latest` | 1 | `python -m app.consumer` | 256Mi / 0.25 CPU |
```

### 8. Deployment-Reihenfolge

Die exakte Reihenfolge, in der die Schritte ausgeführt werden müssen.

```markdown
## Deployment-Reihenfolge

| # | Schritt | Umgebung | Befehl / Aktion | Verifizierung |
|---|---------|----------|-----------------|---------------|
| 1 | Cloud-Komponenten erstellen | Portal / CLI | `az servicebus topic create ...` | Topic im Portal sichtbar |
| 2 | IAM Rollen zuweisen | CLI | `az role assignment create ...` | `az role assignment list` |
| 3 | SQL-Migration ausführen | DEV DB | `ALTER TABLE ...` | Spalte in SSMS sichtbar |
| 4 | Secrets anlegen | Portal | Secret erstellen | Secret vorhanden |
| 5 | App deployen | CI/CD | Pipeline | Pod Running, Health-Check OK |
```

### 9. Rollback-Plan

Schritte zum Rückgängigmachen bei Fehlern.

```markdown
## Rollback-Plan

| # | Schritt | Befehl / Aktion |
|---|---------|-----------------|
| 1 | Pod stoppen | `kubectl scale deployment ... --replicas=0` |
| 2 | SQL-Rollback | `ALTER TABLE ... DROP COLUMN ...;` |
| 3 | Vorherige App-Version deployen | CI/CD: Rollback auf Tag `v1.x.x` |
```

### 10. Verifizierung / Smoke Tests

Manuelle oder automatisierte Tests, die nach dem Deployment durchgeführt werden.

```markdown
## Verifizierung

| # | Test | Erwartetes Ergebnis |
|---|------|---------------------|
| 1 | `curl -X DELETE /api/{id}` | 204, deleted_at gesetzt in DB |
| 2 | Logs prüfen | "Hard-deleted ..." im Log |
```

---

## ✅ Abnahme-Checkliste

Vor dem Merge in Main müssen alle zutreffenden Punkte abgehakt sein:

- [ ] Alle neuen Cloud-Komponenten dokumentiert (mit CLI-Befehlen)?
- [ ] Alle IAM-Rollen und Berechtigungen definiert?
- [ ] Alle neuen Environment-Variablen gelistet?
- [ ] Alle Secrets referenziert (keine Klartext-Secrets)?
- [ ] Alle SQL-Änderungen als Statements dokumentiert (mit Rollback)?
- [ ] Alle neuen Pods/Services dokumentiert (mit Manifest-Pfaden)?
- [ ] Deployment-Reihenfolge definiert (mit Verifizierungsschritten)?
- [ ] Rollback-Plan vorhanden?
- [ ] Smoke Tests definiert?

---

## 🔗 Integration in den Feature-Workflow

Dieses Dokument erweitert Phase 1 (Spezifikation) des Feature Development Workflows. Das Deployment-Dokument wird **parallel zum Implementierungsplan** erstellt und in Phase 4 (Code-Review) verifiziert.

| Phase | Aktion |
|-------|--------|
| **Phase 1** | `_deployment.md` erstellen (Infrastruktur-Anforderungen identifizieren) |
| **Phase 2** | `_deployment.md` aktualisieren (konkrete Werte aus Implementierung eintragen) |
| **Phase 4** | Deployment-Checkliste als Teil des Code-Reviews abhaken |
