# CP4I Mission Console - Dashboard-First Prototype

## Project Objective

Build a **reusable, dashboard-centric prototype** that summarizes a CP4I (Cloud Pak for Integration) environment using **Entity Activity Profiles**.

The prototype is driven by a **desktop Python script** that collects data from an OpenShift / CP4I instance (via local `oc` context), generates structured summaries, and renders a **single HTML "Mission Console" dashboard**.

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

- `collector_ocp.py` - Collects OpenShift and CP4I data via `oc`
- `collector_kafka.py` - Collects Kafka topic and consumer signals (best effort)
- `snapshot_store.py` - Persists snapshots and snapshot history
- `profile_builder.py` - Converts raw data into entity activity profiles
- `diff_engine.py` - Detects meaningful changes between snapshots
- `html_renderer.py` - Renders the Mission Console dashboard
- `config.yaml` - User-editable configuration (namespaces, topic naming rules, refresh cadence)

### Output Artifacts

- `/output/dashboard.html`
- `/output/snapshots/*.json`
- `/output/assets/*`

---

## Project Structure

```
mission-console/
├── src/                    # Python source modules
├── templates/              # HTML templates
├── output/                 # Generated artifacts (gitignored)
│   ├── snapshots/
│   └── assets/
├── config.yaml            # Configuration file
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

A **portable CP4I Mission Console prototype** that proves:

- Entity-based summarization is the right abstraction
- "Activity Profiles" scale across integration technologies
- CP4I environments can be understood without UI hopping
- The concept can evolve cleanly from demo artifact to production pattern
