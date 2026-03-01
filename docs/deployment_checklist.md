# 🚀 Deployment Checklist

Dieses Dokument definiert den verbindlichen Standard für **Deployment-Dokumentation**. Jedes Feature, das Infrastruktur-Änderungen erfordert, muss ein `<feature>_deployment.md` im `docs/`-Verzeichnis des Projekts erstellen.

---

## 📋 Wann ist ein Deployment-Dokument Pflicht?

Ein `_deployment.md` ist **Pflicht**, sobald mindestens eine der folgenden Bedingungen zutrifft:

| Kategorie | Beispiel |
|-----------|----------|
| Neue Azure-Komponenten | Service Bus Topic/Subscription, Redis Cache, Storage Account |
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

### 2. Azure-Komponenten

Neue oder geänderte Azure-Ressourcen mit den exakten CLI-Befehlen zur Erstellung.

```markdown
## Azure-Komponenten

### Service Bus

| Ressource | Typ | Name | Namespace |
|-----------|-----|------|-----------|
| Topic | Service Bus Topic | `portfolio_events` | `sb-stockbuddy-prod` |
| Subscription | Topic Subscription | `AlertsCleanupSub` | auf Topic `portfolio_events` |

**Erstellen:**

\```bash
az servicebus topic create \
  --resource-group $RESOURCE_GROUP \
  --namespace-name $NAMESPACE \
  --name portfolio_events

az servicebus topic subscription create \
  --resource-group $RESOURCE_GROUP \
  --namespace-name $NAMESPACE \
  --topic-name portfolio_events \
  --name AlertsCleanupSub
\```
```

### 3. IAM / Role Assignments

Neue Berechtigungen (RBAC), die für Managed Identities oder User/Groups vergeben werden müssen.

```markdown
## IAM / Role Assignments

| Principal (Wer?) | Rolle (Was?) | Scope (Wo?) | Begründung |
|------------------|--------------|-------------|------------|
| `mi-stockbuddy-aks` | `Azure Service Bus Data Sender` | Topic `portfolio_events` | Pod muss Events senden dürfen |

**Zuweisen:**

\```bash
az role assignment create \
  --assignee $MI_OBJECT_ID \
  --role "Azure Service Bus Data Sender" \
  --scope $TOPIC_RESOURCE_ID
\```
```

### 4. Environment-Variablen

Alle neuen oder geänderten Umgebungsvariablen mit Beschreibung und Quelle.

```markdown
## Environment-Variablen

| Variable | Beschreibung | Pflicht | Quelle | Beispiel |
|----------|-------------|---------|--------|----------|
| `SERVICE_BUS_PORTFOLIO_EVENTS_TOPIC` | Topic-Name für Portfolio-Events | Nein (Default: `portfolio_events`) | Konfiguration | `portfolio_events` |
| `SERVICE_BUS_PORTFOLIO_EVENTS_SUBSCRIPTION` | Subscription-Name | Nein (Default: `AlertsCleanupSub`) | Konfiguration | `AlertsCleanupSub` |
```

### 5. Secrets / KeyVault

**Wichtig:** Niemals echte Secrets (Passwörter, Keys) in dieses Dokument schreiben! Nur Referenzen oder KeyVault-Namen.

```markdown
## Secrets

| Secret Name (KeyVault) | Env-Variable im Pod | Typ | Rotation |
|------------------------|---------------------|-----|----------|
| `SendGridApiKey` | `SERVICE_EMAIL_API_KEY` | API Key | Manuell (1x Jahr) |
| `SbConnectionString` | `SERVICE_BUS_CONNECTION_STRING` | Connection String | Auto |
```

### 6. Datenbank-Änderungen (SQL)

Alle DDL-Statements, die manuell oder per Migration auf der Datenbank ausgeführt werden müssen. **Reihenfolge beachten!**

```markdown
## Datenbank-Änderungen

**Reihenfolge:** Statements müssen in der angegebenen Reihenfolge ausgeführt werden.

| # | Typ | Tabelle | Statement | Rollback |
|---|-----|---------|-----------|----------|
| 1 | ALTER TABLE | UserAlertConfig | `ALTER TABLE UserAlertConfig ADD deleted_at DATETIME NULL;` | `ALTER TABLE UserAlertConfig DROP COLUMN deleted_at;` |
| 2 | CREATE INDEX | UserAlertConfig | `CREATE INDEX ix_alert_deleted ON UserAlertConfig(deleted_at);` | `DROP INDEX ix_alert_deleted ON UserAlertConfig;` |

**Hinweis:** Kein Alembic — Statements manuell auf DEV und PROD ausführen.
```

### 7. Kubernetes / Pods

Neue oder geänderte Deployments, Services, CronJobs.

```markdown
## Kubernetes / Pods

### Neue Deployments

| Name | Image | Replicas | Command | Ressourcen |
|------|-------|----------|---------|------------|
| `portfolio-consumer` | `stockbuddy:latest` | 1 | `python -m stock_buddy.alerts.portfolio_transaction_consumer` | 256Mi / 0.25 CPU |

### Manifest-Änderungen

| Datei | Änderung |
|-------|----------|
| `manifests/consumer-deployment.yaml` | Neues Deployment hinzufügen |
| `manifests/configmap.yaml` | Neue Env-Vars ergänzen |
```

### 8. Deployment-Reihenfolge

Die exakte Reihenfolge, in der die Schritte ausgeführt werden müssen.

```markdown
## Deployment-Reihenfolge

| # | Schritt | Umgebung | Befehl / Aktion | Verifizierung |
|---|---------|----------|-----------------|---------------|
| 1 | Azure-Komponenten erstellen | Azure Portal / CLI | `az servicebus topic create ...` | Topic im Portal sichtbar |
| 2 | IAM Rollen zuweisen | Azure CLI | `az role assignment create ...` | `az role assignment list` |
| 3 | SQL-Migration ausführen | DEV DB | `ALTER TABLE ...` | Spalte in SSMS sichtbar |
| 4 | Secrets in KeyVault anlegen | Azure Portal | Secret erstellen | Secret vorhanden |
| 5 | Environment-Variablen setzen | K8s ConfigMap | `kubectl apply -f configmap.yaml` | `kubectl describe configmap` |
| 6 | Application deployen | AKS | CI/CD Pipeline | Pod Running, Health-Check OK |
```

### 9. Rollback-Plan

Schritte zum Rückgängigmachen bei Fehlern.

```markdown
## Rollback-Plan

| # | Schritt | Befehl / Aktion |
|---|---------|-----------------|
| 1 | Consumer Pod stoppen | `kubectl scale deployment portfolio-consumer --replicas=0` |
| 2 | SQL-Rollback | `ALTER TABLE UserAlertConfig DROP COLUMN deleted_at;` |
| 3 | Vorherige App-Version deployen | CI/CD: Rollback auf Tag `v1.x.x` |
| 4 | Azure-Komponenten entfernen (optional) | `az servicebus topic delete ...` |
```

### 10. Verifizierung / Smoke Tests

Manuelle oder automatisierte Tests, die nach dem Deployment durchgeführt werden.

```markdown
## Verifizierung

| # | Test | Erwartetes Ergebnis |
|---|------|---------------------|
| 1 | `curl -X DELETE /alerts/{id}` | 204, deleted_at gesetzt in DB |
| 2 | Consumer-Logs prüfen | "Hard-deleted alert ..." im Log |
| 3 | `PATCH /settings/strategies/` mit `dynamic_alerts_active: false` | Event auf Service Bus |
```

---

## ✅ Abnahme-Checkliste

Vor dem Merge in Main müssen alle zutreffenden Punkte abgehakt sein:

- [ ] Alle neuen Azure-Komponenten dokumentiert (mit CLI-Befehlen)?
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
