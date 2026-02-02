# Naming Conventions for CP4I Demo Artifacts

## Overview

This document establishes naming conventions and labeling standards for CP4I demo artifacts to ensure:
- **Easy identification** in CP4I and OpenShift consoles
- **Clear purpose** from the name alone
- **Consistent organization** across all resources
- **Better searchability** and filtering
- **Professional appearance** for customer demonstrations

## General Principles

### The 3 C's of Good Naming
1. **Clear** - Immediately understandable
2. **Consistent** - Same pattern across all resources
3. **Concise** - As short as possible while remaining descriptive

### Naming Pattern Structure
```
<domain>-<component>-<function>-<environment>
```

**Example:**
- `healthcare-claims-processor-demo`
- `finance-transaction-enricher-prod`
- `retail-inventory-tracker-test`

---

## Resource-Specific Conventions

### 1. Namespaces / Projects

**Pattern:** `<domain>-<purpose>`

**Examples:**
```
✅ GOOD:
- healthcare-integration      (Production workloads)
- healthcare-demo             (Demo/POC)
- finance-realtime            (Production)
- retail-analytics-demo       (Demo)

❌ BAD:
- integration-platform        (Too generic)
- tools                       (Unclear purpose)
- my-project                  (Unprofessional)
- test123                     (Meaningless)
```

**Best Practice:**
- Use domain prefix (healthcare, finance, retail, etc.)
- Add purpose suffix (integration, demo, analytics, etc.)
- Keep under 25 characters
- Use lowercase with hyphens

---

### 2. Kafka Topics

**Pattern:** `<domain>.<entity>.<stage>`

**Stages:** `raw` → `enriched` → `curated` → `analytics`

**Examples:**
```
✅ GOOD:
- healthcare.claims.raw                    (Raw ingestion)
- healthcare.claims.enriched               (After validation)
- healthcare.claims.curated                (Final form)
- healthcare.patient.fhir.raw              (FHIR patient data)
- healthcare.patient.fhir.enriched         (Validated FHIR)
- finance.transactions.raw                 (Raw transactions)
- finance.transactions.fraud-checked       (After fraud check)
- retail.orders.real-time                  (Live orders)

Special Topics:
- healthcare.claims.dlq                    (Dead letter queue)
- healthcare.claims.error                  (Error handling)
- healthcare.claims.audit                  (Audit trail)

❌ BAD:
- topic1                     (Meaningless)
- claims                     (Missing domain and stage)
- RAW_CLAIMS                 (Inconsistent casing)
- claims_transactions_raw    (Use dots, not underscores)
```

**Best Practice:**
- Use dot-notation for hierarchy
- Include data lineage stage (raw/enriched/curated)
- Keep total length under 50 characters
- Lowercase only
- Use descriptive entity names

---

### 3. Event Streams Instances

**Pattern:** `<domain>-eventstreams-<environment>`

**Examples:**
```
✅ GOOD:
- healthcare-eventstreams-prod
- healthcare-eventstreams-demo
- finance-eventstreams-prod
- retail-eventstreams-dev

❌ BAD:
- es-platform              (Too cryptic)
- eventstreams1           (Numbered instances)
- kafka-cluster           (Not product-specific)
```

**Best Practice:**
- Include "eventstreams" in the name
- Add environment suffix
- Max 30 characters

---

### 4. Applications / Pods

**Pattern:** `<domain>-<function>-<component>-<env>`

**Examples:**
```
✅ GOOD:
- healthcare-claims-processor-demo
- healthcare-fhir-validator-demo
- healthcare-claims-enricher-prod
- healthcare-patient-matcher-demo
- finance-fraud-detector-prod
- retail-inventory-sync-demo

Event Processing Specific:
- healthcare-ep-claims-flow-demo          (EP flow)
- healthcare-ep-fhir-processor-demo       (EP processor)
- finance-ep-fraud-detection-demo         (EP fraud detection)

Analytics Specific:
- healthcare-analytics-dashboard-demo     (Analytics UI)
- finance-analytics-realtime-demo         (Real-time analytics)

❌ BAD:
- ep-demo                  (Too generic)
- app1                     (Meaningless)
- my-processor             (Unprofessional)
- claims-processor         (Missing domain)
```

**Best Practice:**
- Start with domain
- Describe the function clearly
- Add component type (processor, validator, enricher, etc.)
- End with environment
- Max 40 characters

---

### 5. Routes

**Pattern:** `<app-name>-ui` or `<app-name>-api`

**Examples:**
```
✅ GOOD:
- healthcare-claims-processor-ui
- healthcare-claims-processor-api
- healthcare-ep-dashboard-ui
- finance-fraud-detector-api

For Event Streams:
- healthcare-eventstreams-ui
- healthcare-eventstreams-admin-api
- healthcare-eventstreams-producer-api

❌ BAD:
- route1                   (Meaningless)
- ui                       (Too generic)
- my-app-route             (Redundant "-route")
```

**Best Practice:**
- Match the application name
- Add `-ui` or `-api` suffix
- Keep route name = app name + interface type

---

### 6. ConfigMaps and Secrets

**Pattern:** `<app-name>-config` or `<app-name>-secret`

**Examples:**
```
✅ GOOD:
- healthcare-claims-processor-config
- healthcare-claims-processor-secret
- healthcare-eventstreams-admin-secret
- finance-fraud-detector-api-config

❌ BAD:
- config                   (Too generic)
- secret1                  (Meaningless)
- my-secret                (Unprofessional)
```

---

### 7. Persistent Volume Claims

**Pattern:** `<app-name>-data` or `<app-name>-logs`

**Examples:**
```
✅ GOOD:
- healthcare-claims-processor-data
- healthcare-analytics-dashboard-data
- healthcare-eventstreams-kafka-data
- finance-fraud-detector-logs

❌ BAD:
- pvc1                     (Meaningless)
- data                     (Too generic)
```

---

## Kubernetes Labels

### Required Labels (Apply to ALL Resources)

```yaml
metadata:
  labels:
    # Standard Kubernetes Labels
    app.kubernetes.io/name: healthcare-claims-processor
    app.kubernetes.io/instance: healthcare-claims-processor-demo
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/component: processor
    app.kubernetes.io/part-of: healthcare-integration
    app.kubernetes.io/managed-by: cp4i

    # Custom Labels
    domain: healthcare
    environment: demo
    data-classification: phi  # phi, pii, public, internal
    owner: demo-team
    purpose: demonstration
```

### Label Categories

#### 1. Domain Labels
```yaml
domain: healthcare | finance | retail | manufacturing
subdomain: claims | patient | provider | transactions
```

#### 2. Environment Labels
```yaml
environment: prod | demo | dev | test | staging
```

#### 3. Component Labels
```yaml
app.kubernetes.io/component: processor | validator | enricher | ui | api | database
```

#### 4. Data Classification Labels
```yaml
data-classification: phi | pii | public | internal | confidential
```

#### 5. Ownership Labels
```yaml
owner: demo-team | platform-team | integration-team
cost-center: "1234"
project: healthcare-integration-2025
```

#### 6. Demo-Specific Labels
```yaml
demo: "true"
demo-scenario: claims-processing | patient-matching | fraud-detection
demo-order: "1" | "2" | "3"  # For demo flow sequencing
```

---

## Kubernetes Annotations

### Recommended Annotations

```yaml
metadata:
  annotations:
    # Description
    description: "Processes healthcare insurance claims in real-time"

    # Business Context
    business-purpose: "Claims processing automation"
    business-owner: "Claims Processing Team"

    # Demo Metadata
    demo.purpose: "Demonstrate real-time claims validation"
    demo.audience: "Healthcare customers"
    demo.talking-points: "HIPAA compliance, real-time validation, error handling"

    # Documentation
    documentation: "https://wiki.company.com/healthcare-claims"
    runbook: "https://wiki.company.com/runbooks/claims-processor"

    # Contact Info
    contact.email: "demo-team@company.com"
    contact.slack: "#healthcare-demos"

    # Monitoring
    monitoring.dashboard: "https://grafana.company.com/d/claims-processor"
    monitoring.alerts: "true"
```

---

## Complete Examples

### Example 1: Healthcare Claims Processing Application

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: healthcare-claims-processor-demo
  namespace: healthcare-demo
  labels:
    # Standard K8s Labels
    app.kubernetes.io/name: healthcare-claims-processor
    app.kubernetes.io/instance: healthcare-claims-processor-demo
    app.kubernetes.io/version: "1.2.0"
    app.kubernetes.io/component: processor
    app.kubernetes.io/part-of: healthcare-integration
    app.kubernetes.io/managed-by: cp4i

    # Custom Labels
    domain: healthcare
    subdomain: claims
    environment: demo
    data-classification: phi
    owner: demo-team
    demo: "true"
    demo-scenario: claims-processing

  annotations:
    description: "Real-time healthcare insurance claims processor with validation"
    business-purpose: "Automate claims validation and fraud detection"
    business-owner: "Claims Processing Team"
    demo.purpose: "Demonstrate HIPAA-compliant real-time claims processing"
    demo.talking-points: "Real-time validation, fraud detection, FHIR integration"
    contact.email: "demo-team@company.com"

spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: healthcare-claims-processor
      app.kubernetes.io/instance: healthcare-claims-processor-demo
  template:
    metadata:
      labels:
        app.kubernetes.io/name: healthcare-claims-processor
        app.kubernetes.io/instance: healthcare-claims-processor-demo
        domain: healthcare
        environment: demo
```

### Example 2: Kafka Topic

```yaml
apiVersion: eventstreams.ibm.com/v1beta2
kind: KafkaTopic
metadata:
  name: healthcare.claims.raw
  namespace: healthcare-demo
  labels:
    app.kubernetes.io/part-of: healthcare-integration
    domain: healthcare
    entity: claims
    stage: raw
    data-classification: phi
    owner: integration-team

  annotations:
    description: "Raw insurance claims from billing systems"
    business-purpose: "Claims processing ingest layer"
    data-retention: "7 days"
    data-format: "HL7 v2.5"
    schema-registry: "healthcare-claims-raw-schema"

spec:
  partitions: 10
  replicas: 3
  config:
    retention.ms: "604800000"  # 7 days
```

### Example 3: Route

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: healthcare-claims-processor-ui
  namespace: healthcare-demo
  labels:
    app.kubernetes.io/name: healthcare-claims-processor
    app.kubernetes.io/component: ui
    domain: healthcare
    environment: demo

  annotations:
    description: "Web UI for healthcare claims processing demo"
    demo.url: "https://healthcare-claims-processor-ui.apps.cluster.com"
    demo.credentials: "See secret: healthcare-claims-processor-ui-creds"

spec:
  to:
    kind: Service
    name: healthcare-claims-processor-ui
  tls:
    termination: edge
```

---

## Implementation Guide

### Step 1: Plan Your Naming

Before creating resources, fill out this template:

```
Domain:           healthcare
Use Case:         Claims Processing
Environment:      demo
Components:
  - Processor
  - Validator
  - Enricher
  - UI Dashboard

Kafka Topics:
  - healthcare.claims.raw
  - healthcare.claims.validated
  - healthcare.claims.enriched
  - healthcare.claims.curated

Applications:
  - healthcare-claims-processor-demo
  - healthcare-claims-validator-demo
  - healthcare-claims-enricher-demo
  - healthcare-claims-dashboard-demo

Routes:
  - healthcare-claims-processor-api
  - healthcare-claims-dashboard-ui
```

### Step 2: Apply Labels Using CLI

```bash
# Label a pod
oc label pod healthcare-claims-processor-demo \
  domain=healthcare \
  environment=demo \
  data-classification=phi \
  demo=true

# Label a topic
oc label kafkatopic healthcare.claims.raw \
  domain=healthcare \
  entity=claims \
  stage=raw \
  data-classification=phi

# Label multiple resources
oc label deployment,service -l app.kubernetes.io/name=healthcare-claims-processor \
  domain=healthcare \
  environment=demo
```

### Step 3: Apply Annotations Using CLI

```bash
# Annotate a deployment
oc annotate deployment healthcare-claims-processor-demo \
  description="Real-time healthcare claims processor" \
  business-purpose="Claims validation automation" \
  demo.talking-points="HIPAA compliance, real-time processing"

# Annotate multiple resources
oc annotate deployment,service -l app.kubernetes.io/name=healthcare-claims-processor \
  business-owner="Claims Processing Team"
```

### Step 4: Query Resources by Labels

```bash
# Find all healthcare resources
oc get all -l domain=healthcare

# Find all demo resources
oc get all -l demo=true

# Find all PHI-classified resources
oc get all -l data-classification=phi

# Find resources in a specific demo scenario
oc get all -l demo-scenario=claims-processing

# Complex queries
oc get all -l domain=healthcare,environment=demo,app.kubernetes.io/component=processor
```

---

## Visual Organization in Consoles

### OpenShift Topology View

With proper labels, resources auto-group in the topology:

```
Application: healthcare-integration
├─ healthcare-claims-processor
│  ├─ Deployment: healthcare-claims-processor-demo
│  ├─ Service: healthcare-claims-processor-demo
│  └─ Route: healthcare-claims-processor-api
├─ healthcare-claims-validator
└─ healthcare-claims-dashboard
```

### CP4I Platform Navigator

Resources appear organized by:
- **Domain** (healthcare, finance, retail)
- **Component** (processors, validators, dashboards)
- **Environment** (prod, demo, dev)

---

## Naming Checklist

Before creating a new resource, verify:

- [ ] Name follows domain-component-function-environment pattern
- [ ] Name is lowercase with hyphens only
- [ ] Name is under 40 characters (or appropriate limit for resource type)
- [ ] Name is self-explanatory (no need to check documentation)
- [ ] All required labels are applied
- [ ] Description annotation is added
- [ ] Business-purpose annotation is added
- [ ] Demo-specific labels/annotations are added (if applicable)
- [ ] Name matches the display name in demo_metadata.yaml

---

## Migration Guide

### Renaming Existing Resources

For resources already deployed:

1. **Update demo_metadata.yaml first** with new display names
2. **Create new resources** with proper naming
3. **Gradually migrate** traffic/data to new resources
4. **Delete old resources** after validation

### Quick Migration Script

```bash
#!/bin/bash
# Migrate old resource to new naming convention

OLD_NAME="ep-demo"
NEW_NAME="healthcare-ep-claims-flow-demo"
NAMESPACE="tools"

# Create new deployment from old
oc get deployment $OLD_NAME -n $NAMESPACE -o yaml | \
  sed "s/$OLD_NAME/$NEW_NAME/g" | \
  oc apply -f -

# Copy labels and annotations
oc label deployment $NEW_NAME -n $NAMESPACE \
  domain=healthcare \
  environment=demo \
  demo=true

oc annotate deployment $NEW_NAME -n $NAMESPACE \
  description="Event Processing demo for healthcare claims"

# Scale down old deployment
oc scale deployment $OLD_NAME -n $NAMESPACE --replicas=0

# After validation, delete old
oc delete deployment $OLD_NAME -n $NAMESPACE
```

---

## Domain-Specific Examples

### Healthcare Domain
```
Namespaces:
- healthcare-integration
- healthcare-demo

Topics:
- healthcare.claims.raw
- healthcare.claims.validated
- healthcare.patient.fhir.raw
- healthcare.patient.fhir.enriched
- healthcare.provider.directory.curated

Apps:
- healthcare-claims-processor-demo
- healthcare-fhir-validator-demo
- healthcare-patient-matcher-demo
- healthcare-analytics-dashboard-demo
```

### Finance Domain
```
Namespaces:
- finance-realtime
- finance-demo

Topics:
- finance.transactions.raw
- finance.transactions.fraud-checked
- finance.transactions.settled
- finance.market-data.real-time
- finance.portfolio.analytics

Apps:
- finance-fraud-detector-demo
- finance-transaction-enricher-demo
- finance-settlement-processor-demo
- finance-risk-calculator-demo
```

### Retail Domain
```
Namespaces:
- retail-integration
- retail-demo

Topics:
- retail.orders.real-time
- retail.orders.validated
- retail.inventory.updates
- retail.customer.events
- retail.loyalty.points

Apps:
- retail-order-processor-demo
- retail-inventory-sync-demo
- retail-recommendation-engine-demo
- retail-analytics-dashboard-demo
```

---

## Best Practices Summary

### DO ✅
- Use domain-specific prefixes
- Keep names descriptive and self-explanatory
- Apply all recommended labels
- Add business context in annotations
- Follow the established pattern consistently
- Keep names under character limits
- Use lowercase with hyphens

### DON'T ❌
- Use generic names (app1, test, demo)
- Use abbreviations unless industry-standard
- Mix naming styles (camelCase, snake_case, kebab-case)
- Exceed recommended character limits
- Skip labels and annotations
- Use numbers as differentiators (app1, app2)
- Use special characters except hyphens and dots

---

## Tools and Automation

### Auto-Generate Names Script

```bash
#!/bin/bash
# generate-name.sh - Generate compliant resource name

DOMAIN=$1
COMPONENT=$2
FUNCTION=$3
ENV=$4

echo "${DOMAIN}-${COMPONENT}-${FUNCTION}-${ENV}"
```

**Usage:**
```bash
./generate-name.sh healthcare claims processor demo
# Output: healthcare-claims-processor-demo
```

### Validation Script

```bash
#!/bin/bash
# validate-naming.sh - Validate resource naming

NAME=$1

# Check length
if [ ${#NAME} -gt 40 ]; then
  echo "❌ Name too long (max 40 chars)"
  exit 1
fi

# Check format (lowercase, hyphens only)
if [[ ! $NAME =~ ^[a-z0-9-]+$ ]]; then
  echo "❌ Invalid characters (use lowercase and hyphens only)"
  exit 1
fi

# Check pattern (domain-component-function-env)
if [[ ! $NAME =~ ^[a-z]+-[a-z]+-[a-z]+-[a-z]+$ ]]; then
  echo "⚠️  Warning: Doesn't match standard pattern"
fi

echo "✅ Name is valid: $NAME"
```

---

**Document Version:** 1.0.0
**Last Updated:** December 31, 2025
**Owner:** Demo Team
**Status:** ✅ Active Standard
