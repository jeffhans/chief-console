{\rtf1\ansi\ansicpg1252\cocoartf2867
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # CP4I Mission Console \'96 Dashboard-First Prototype\
\
## Project Objective\
\
Build a **reusable, dashboard-centric prototype** that summarizes a CP4I (Cloud Pak for Integration) environment using **Entity Activity Profiles**.  \
The prototype is driven by a **desktop Python script** that collects data from an OpenShift / CP4I instance (via local `oc` context), generates structured summaries, and renders a **single HTML \'93Mission Console\'94 dashboard**.\
\
This is intentionally **dashboard-first** and **out-of-cluster** to survive TechZone churn and accelerate iteration. In-cluster operators and long-lived services are explicitly out of scope for v1.\
\
---\
\
## Guiding Principles\
\
- Dashboard first, plumbing later  \
- Entity-appropriate metrics (not raw counts)  \
- Summarize \uc0\u8594  then drill  \
- Discovery over configuration  \
- Demo-safe, explainable outputs  \
- Reusable across ephemeral CP4I environments  \
\
---\
\
## Core Concept: Entity Activity Profiles\
\
### Definition\
\
An **Entity Activity Profile** is a concise, time-aware summary of how an entity behaves, using metrics appropriate to that entity\'92s role.\
\
This avoids brittle, low-level metrics (e.g., \'93message counts\'94) and enables consistent summarization across heterogeneous integration components.\
\
### Supported Entity Types (v1)\
\
- Cluster  \
- Namespace  \
- Integration Capability (CP4I component)  \
- Workload / Runtime  \
- Kafka Topic  \
- Kafka Consumer Group  \
- Pipeline / Enrichment Flow (logical, inferred)\
\
Each entity type has its own profile schema.\
\
---\
\
## High-Level Prototype Architecture\
\
[ Local Python Collector ]\
|\
v\
[ Snapshot JSON (raw + normalized) ]\
|\
v\
[ Activity Profile Generator ]\
|\
v\
[ Static HTML Dashboard ]\
\
yaml\
Copy code\
\
Optional:\
- Snapshot history & diffing (\'93what changed\'94)\
- Lightweight local web server for auto-refresh\
\
---\
\
## Data Collection Scope (v1)\
\
### OpenShift / CP4I (via `oc` CLI)\
\
- Cluster info\
- Nodes (capacity, allocatable resources)\
- Pods (status, restarts)\
- Operators / CSVs (installed CP4I capabilities)\
- Routes (for deep links)\
- Events (recent change signals)\
- Resource hotspots (`oc adm top`)\
\
### Kafka / Event Streams (best effort)\
\
- Topics\
- Partitions / replication\
- Offset-derived activity indicators\
- Consumer groups and lag (if available)\
\
> Kafka metrics may be partial in TechZone.  \
> The dashboard **must degrade gracefully** and clearly indicate unavailable data.\
\
---\
\
## Activity Profile Definitions (v1)\
\
### Kafka Topic \'96 Activity Profile\
\
- Throughput classification (low / medium / high)\
- Activity trend (steady / spiking / dropping)\
- Partitioning summary\
- Replication health\
- Consumption health (lag trend)\
- Recent change signals\
\
**Example narrative output:**  \
> \'93This topic is high-throughput, well-replicated, and actively consumed with stable lag.\'94\
\
---\
\
### Pipeline / Enrichment Flow \'96 Activity Profile (Inferred)\
\
- Source entities\
- Destination entities\
- Input vs output activity balance\
- Backpressure or error indicators (if observable)\
- Overall flow health\
\
Used to represent **raw \uc0\u8594  enriched \u8594  curated** flows in BTDS-style architectures.\
\
---\
\
### CP4I Capability \'96 Activity Profile\
\
- Deployment footprint (pods, namespaces)\
- Resource behavior trends\
- Stability indicators (restarts, readiness)\
- Change velocity (upgrades, rollouts)\
\
---\
\
### Cluster \'96 Activity Profile\
\
- Overall health status\
- Capacity headroom\
- Active issues\
- Recent changes\
\
---\
\
## Dashboard Design: \'93Meaningful Waves\'94\
\
### Wave 1 \'97 Executive Summary\
\
- Overall environment status (Green / Yellow / Red)\
- Key health drivers\
- Capacity posture\
- Licensing / entitlement posture\
- \'93What changed recently\'94\
- Last refresh timestamp + refresh action\
\
---\
\
### Wave 2 \'97 CP4I Workloads\
\
- Installed CP4I capabilities\
- Operator and runtime health\
- Resource hotspots\
- Deep links to:\
  - OpenShift Console (filtered views)\
  - CP4I Platform UI\
\
---\
\
### Wave 3 \'97 Kafka / BTDS Focus\
\
- Topic activity table (entity activity profiles)\
- Consumer group activity\
- Logical pipeline / lineage visualization\
- Activity summaries (not raw counts)\
\
---\
\
### Wave 4 \'97 Governance & Licensing\
\
- CP4I footprint summary\
- Observed OpenShift core usage\
- License Service presence and freshness\
- Narrative-ready entitlement posture summary\
\
---\
\
## Deep Linking Requirements\
\
Each dashboard tile should optionally link to:\
\
- OpenShift Console (namespace-, workload-, or operator-filtered)\
- CP4I Platform UI\
- Event Streams UI\
- Namespace or workload detail views\
\
Links should be dynamically discovered via Routes wherever possible.\
\
---\
\
## Python Implementation Plan\
\
### Modules\
\
- `collector_ocp.py`  \
  Collects OpenShift and CP4I data via `oc`\
\
- `collector_kafka.py`  \
  Collects Kafka topic and consumer signals (best effort)\
\
- `snapshot_store.py`  \
  Persists snapshots and snapshot history\
\
- `profile_builder.py`  \
  Converts raw data into entity activity profiles\
\
- `diff_engine.py`  \
  Detects meaningful changes between snapshots\
\
- `html_renderer.py`  \
  Renders the Mission Console dashboard\
\
- `config.yaml`  \
  User-editable configuration:\
  - namespaces\
  - topic naming rules\
  - refresh cadence\
\
---\
\
## Output Artifacts\
\
- `/output/dashboard.html`\
- `/output/snapshots/*.json`\
- `/output/assets/*`\
\
Optional:\
- Local HTTP server for auto-refresh\
\
---\
\
## AI Summary Layer (Optional v1, Recommended v2)\
\
Generate narrative sections from snapshots + diffs only:\
\
- \'93What matters right now\'94\
- \'93What changed since last refresh\'94\
- \'93Top risks\'94\
- \'93Suggested next clicks\'94\
\
AI must remain grounded in collected data and cite sources internally.\
\
---\
\
## Explicit Non-Goals (v1)\
\
- No operators\
- No in-cluster services\
- No write actions to the cluster\
- No hard dependency on Prometheus\
- No requirement for perfect Kafka metrics\
\
---\
\
## Success Criteria\
\
- Dashboard renders cleanly from a single script run\
- Works across multiple CP4I TechZone instances\
- Handles missing or partial Kafka data gracefully\
- Demo-ready without heavy explanation\
- UI and data model are reusable for future in-cluster evolution\
\
---\
\
## Future Evolution (Acknowledged, Out of Scope)\
\
- Operator-based deployment\
- Continuous in-cluster collectors\
- Trace-based lineage\
- Capacity forecasting\
- SLOs per integration capability\
\
---\
\
## Primary Outcome\
\
A **portable CP4I Mission Console prototype** that proves:\
\
- Entity-based summarization is the right abstraction\
- \'93Activity Profiles\'94 scale across integration technologies\
- CP4I environments can be understood without UI hopping\
- The concept can evolve cleanly from demo artifact to production pattern}