# CP4I Chief Console

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenShift](https://img.shields.io/badge/OpenShift-4.x-red.svg)](https://www.openshift.com/)

> A dashboard-first monitoring tool for IBM Cloud Pak for Integration (CP4I) environments

## Project Objective

Build a **reusable, dashboard-centric prototype** that summarizes a CP4I (Cloud Pak for Integration) environment using **Entity Activity Profiles**.

The prototype is driven by a **desktop Python script** that collects data from an OpenShift / CP4I instance (via local `oc` context), generates structured summaries, and renders a **single HTML "Chief Console" dashboard**.

This is intentionally **dashboard-first** and **out-of-cluster** to survive TechZone churn and accelerate iteration. In-cluster operators and long-lived services are explicitly out of scope for v1.

---

## Guiding Principles

- Dashboard first, plumbing later
- Entity-appropriate metrics (not raw counts)
- Summarize → then drill
- Discovery over configuration
- Demo-safe, explainable outputs
- Reusable across ephemeral CP4I environments

---

## Core Concept: Entity Activity Profiles

### Definition

An **Entity Activity Profile** is a concise, time-aware summary of how an entity behaves, using metrics appropriate to that entity's role.

This avoids brittle, low-level metrics (e.g., "message counts") and enables consistent summarization across heterogeneous integration components.

### Supported Entity Types (v1)

- Cluster
- Namespace
- Integration Capability (CP4I component)
- Workload / Runtime
- Kafka Topic
- Kafka Consumer Group
- Pipeline / Enrichment Flow (logical, inferred)

Each entity type has its own profile schema.

---

## High-Level Prototype Architecture

```
[ Local Python Collector ]
          |
          v
[ Snapshot JSON (raw + normalized) ]
          |
          v
[ Activity Profile Generator ]
          |
          v
[ Static HTML Dashboard ]
```

Optional:
- Snapshot history & diffing ("what changed")
- Lightweight local web server for auto-refresh

---

## Data Collection Scope (v1)

### OpenShift / CP4I (via `oc` CLI)

- Cluster info
- Nodes (capacity, allocatable resources)
- Pods (status, restarts)
- Operators / CSVs (installed CP4I capabilities)
- Routes (for deep links)
- Events (recent change signals)
- Resource hotspots (`oc adm top`)

### Kafka / Event Streams (best effort)

- Topics
- Partitions / replication
- Offset-derived activity indicators
- Consumer groups and lag (if available)

> Kafka metrics may be partial in TechZone.
> The dashboard **must degrade gracefully** and clearly indicate unavailable data.

---

## Dashboard Design: "Meaningful Waves"

### Wave 1 - Executive Summary

- Overall environment status (Green / Yellow / Red)
- Key health drivers
- Capacity posture
- Licensing / entitlement posture
- "What changed recently"
- Last refresh timestamp + refresh action

### Wave 2 - CP4I Workloads

- Installed CP4I capabilities
- Operator and runtime health
- Resource hotspots
- Deep links to OpenShift Console and CP4I Platform UI

### Wave 3 - Kafka / BTDS Focus

- Topic activity table (entity activity profiles)
- Consumer group activity
- Logical pipeline / lineage visualization
- Activity summaries (not raw counts)

### Wave 4 - Governance & Licensing

- CP4I footprint summary
- Observed OpenShift core usage
- License Service presence and freshness
- Narrative-ready entitlement posture summary

---

## Python Implementation Plan

### Modules

- `env_manager.py` - Manages multiple environment profiles and credentials (PDF import, switching)
- `collector_ocp.py` - Collects OpenShift and CP4I data via `oc`
- `collector_kafka.py` - Collects Kafka topic and consumer signals (best effort)
- `snapshot_store.py` - Persists snapshots and snapshot history
- `profile_builder.py` - Converts raw data into entity activity profiles
- `diff_engine.py` - Detects meaningful changes between snapshots
- `html_renderer.py` - Renders the Chief Console dashboard
- `config.yaml` - User-editable configuration (namespaces, topic naming rules, refresh cadence)
- `environments.yaml` - Environment credentials and metadata (gitignored, use environments.example.yaml as template)

### Output Artifacts

- `/output/dashboard.html`
- `/output/snapshots/*.json`
- `/output/assets/*`

---

## Environment Management

### Managing Multiple CP4I Environments

The Chief Console supports managing multiple ephemeral CP4I environments (e.g., TechZone reservations) with credential storage and metadata tracking.

#### Quick Start

1. **Import from PDF** (TechZone login info):
   ```bash
   python src/env_manager.py import ~/Downloads/techzone-login.pdf my-demo-env
   ```

2. **List environments**:
   ```bash
   python src/env_manager.py list
   ```

3. **Get login command**:
   ```bash
   python src/env_manager.py login
   ```

4. **Switch active environment**:
   ```bash
   python src/env_manager.py activate another-env
   ```

#### Environment Profile Schema

Environments are stored in `environments.yaml` (gitignored for security). Each profile includes:

- **Metadata**: Name, creation date, expiration date, tags
- **Cluster details**: API URL, console URL, authentication (token/username/password)
- **Platform Navigator**: URL and credentials
- **Installed capabilities**: Event Streams, API Connect, App Connect, MQ, etc.
- **Source tracking**: PDF import metadata, import date

#### PDF Import

The tool can extract login credentials from TechZone/OpenShift PDF exports:

```bash
python src/env_manager.py import path/to/login.pdf
```

Extracted information:
- Cluster API URL
- Console URL
- Authentication token or username/password
- Platform Navigator URL (if present)

PDFs are archived in `output/env-imports/` for reference.

#### Manual Configuration

Copy `environments.example.yaml` to `environments.yaml` and edit:

```bash
cp environments.example.yaml environments.yaml
```

---

## Local Configuration Overrides

The Chief Console supports local configuration overrides for personal settings without modifying the base `config.yaml` file.

### Quick Start

1. **Create local config** (gitignored):
   ```bash
   cp config.local.yaml.example config.local.yaml
   ```

2. **Add your cluster mappings**:
   ```yaml
   cluster_aliases:
     "your-cluster-api.example.com":
       name: "My Demo Environment"
       id: "demo-123"
   ```

3. **Override any setting** from `config.yaml`:
   ```yaml
   dashboard:
     title: "My Custom Dashboard"
     auto_refresh_seconds: 60
   ```

The local config is automatically merged with the base config at runtime, with local settings taking precedence.

---

## Project Structure

```
chief-console/
├── src/                    # Python source modules
│   └── env_manager.py      # Environment management
├── templates/              # HTML templates
├── output/                 # Generated artifacts (gitignored)
│   ├── snapshots/
│   ├── assets/
│   └── env-imports/        # Archived PDF imports
├── config.yaml             # Base application configuration
├── config.local.yaml       # Local overrides (gitignored)
├── config.local.yaml.example  # Template for local config
├── environments.yaml       # Environment credentials (gitignored)
├── environments.example.yaml  # Template for environments.yaml
├── requirements.txt        # Python dependencies
└── README.md
```

---

## Explicit Non-Goals (v1)

- No operators
- No in-cluster services
- No write actions to the cluster
- No hard dependency on Prometheus
- No requirement for perfect Kafka metrics

---

## Success Criteria

- Dashboard renders cleanly from a single script run
- Works across multiple CP4I TechZone instances
- Handles missing or partial Kafka data gracefully
- Demo-ready without heavy explanation
- UI and data model are reusable for future in-cluster evolution

---

## Future Evolution (Acknowledged, Out of Scope)

- Operator-based deployment
- Continuous in-cluster collectors
- Trace-based lineage
- Capacity forecasting
- SLOs per integration capability

---

## Primary Outcome

A **portable CP4I Chief Console prototype** that proves:

- Entity-based summarization is the right abstraction
- "Activity Profiles" scale across integration technologies
- CP4I environments can be understood without UI hopping
- The concept can evolve cleanly from demo artifact to production pattern
