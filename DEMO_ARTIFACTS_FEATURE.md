# Wave 4: Demo Artifacts Feature

## Overview

The **Demo Artifacts** section is your **starting point for demos** - a hierarchical view of all custom deployments with deep links to OpenShift's OOTB graphical topology views and individual resources.

## What You See

### Hierarchical Organization by Namespace

Each CP4I namespace (excluding system namespaces) shows:

```
📁 namespace-name
  [📊 View Topology] [🔗 View Namespace]

  🎉 Event Streams
    └─ instance-name (version, status)
        📊 Kafka Topics (organized by category):
          ├─ RAW: (ingest layer)
          ├─ ENRICHED: (processed data)
          ├─ CURATED: (final form)
          ├─ DLQ: (dead letter queue)
          └─ GENERAL: (other topics)

  🚀 Applications (custom pods)
    └─ Your deployed apps (excludes operator pods)

  🌐 Routes (external access)
    └─ URLs to access your applications
```

### Data Flow Visualization

Topics are shown in **processing order**:
1. **RAW** - Ingest layer (raw data coming in)
2. **ENRICHED** - Processed/transformed data
3. **CURATED** - Final form ready for consumption
4. **DLQ** - Dead letter queue for errors
5. **GENERAL** - Other topics

This shows the **data lineage** at a glance!

## Deep Links

### 1. Topology View (Graphical OOTB)
**Button**: `📊 View Topology`
**URL**: `{console}/topology/ns/{namespace}`

**Opens**: OpenShift Developer Perspective Topology View showing:
- Visual graph of all resources
- Application groupings
- Pod health status (green/yellow/red)
- Connections between services
- Quick actions (logs, terminal, scale, etc.)

**Perfect for demos**: Click once to show the entire namespace visually!

### 2. Namespace Overview
**Button**: `🔗 View Namespace`
**URL**: `{console}/k8s/cluster/projects/{namespace}`

**Opens**: Full namespace view with all resources organized by type

### 3. Individual Resources
**Link**: `[🔗 View]` next to each resource

**Opens**: Resource details page:
- Event Streams: Instance configuration, status, conditions
- Kafka Topics: Partitions, replicas, retention, config
- Pods: Logs, events, terminal, metrics
- Routes: Configuration, target service, TLS settings

### 4. Route URLs
**Direct links** to running applications (clickable URLs)

## Demo Workflow

### Perfect for Customer Demos:

**1. Start at Wave 1** - Show overall health
```
"Here's our CP4I environment running on OpenShift 4.16.52"
"3 capabilities installed: CP4I Platform, Event Streams, Event Processing"
"Everything healthy - 6 nodes, 47 pods running"
```

**2. Jump to Wave 4** - Show what you built
```
"Let me show you what we've deployed..."
[Scroll to Demo Artifacts]
"In the integration-platform namespace, we have:"
```

**3. Walk through the hierarchy**
```
"Event Streams instance es-platform with 5 topics"
"Notice the data flow: RAW → ENRICHED"
"We're ingesting claims and FHIR data (RAW topics)"
"Processing it through Event Processing (ENRICHED topics)"
"9 applications handling the processing"
"5 external routes for access"
```

**4. Click Topology View**
```
[Click 📊 View Topology button]
"And here's the visual representation..."
[OpenShift topology view opens showing the graph]
"You can see all the components and their relationships"
```

**5. Deep dive on any component**
```
[Click 🔗 View on a topic or pod]
"Let's look at the details of this topic..."
[Shows Kafka topic configuration]
```

**6. Show tools namespace**
```
[Scroll to tools section]
"And here's our demo Event Processing instance"
[Click 📊 View Topology for tools]
"Running the ep-demo and ea-flink-demo applications"
```

### Perfect for Troubleshooting:

**Quick path to any resource:**
1. Find it in Wave 4 (hierarchical view)
2. Click [🔗 View] to open in console
3. Check logs/events/status
4. One click from problem to solution!

## Technical Implementation

### Files Modified

- `src/html_renderer.py`:
  - Added `_render_wave4_demo_artifacts()` method
  - Added `_render_demo_artifacts_hierarchy()` method
  - Updated `render()` to include Wave 4

### Key Logic

**Namespace Filtering:**
```python
# Exclude system namespaces, show only demo namespaces
demo_namespaces = [ns for ns in cp4i_namespaces
                  if ns not in ['openshift-marketplace', 'ibm-common-services']]
```

**Pod Filtering:**
```python
# Show only demo/custom pods (exclude operator infrastructure)
demo_pods = [p for p in ns_pods if not any(x in p.get('name', '').lower()
            for x in ['operator', 'zookeeper', 'kafka-', 'strimzi'])]
```

**Topic Categorization:**
```python
# Group topics by category and show in processing order
for category in ['raw', 'enriched', 'curated', 'dlq', 'general']:
    if category in topics_by_category:
        # Show topics in this category
```

**Topology Link:**
```python
topology_link = f"{console_url}/topology/ns/{namespace}"
```

## Wave Order

The dashboard now has **4 waves**:

1. **Wave 1: Executive Summary** - Health, status, "What Changed"
2. **Wave 2: CP4I Workloads** - Installed capabilities (operators)
3. **Wave 4: Demo Artifacts** - Your custom deployments ← **NEW!**
4. **Wave 3: Infrastructure** - Nodes, capacity, namespaces

**Note**: Wave 4 comes before Wave 3 because it's more relevant for demos than infrastructure details.

## Use Cases

### ✅ Demo Preparation
- Quick overview of what's deployed
- Verify all components are running
- Get URLs for live demos
- Plan your demo flow

### ✅ Customer Presentations
- Show the big picture first (Wave 1)
- Walk through what you built (Wave 4)
- Click Topology for visual impact
- Deep dive on specific components

### ✅ Troubleshooting
- Find resources quickly (hierarchical view)
- One click to logs/events
- See relationships between components
- Topology view shows connections

### ✅ Documentation
- Print/PDF the dashboard
- Shows current state of deployment
- Includes all URLs and versions
- Data flow visualization

### ✅ Handoff to Operations
- Clear view of what was deployed
- All access URLs in one place
- Topology links for visual understanding
- Easy to navigate and explore

## Example: Healthcare Integration Demo

**Your current deployment:**

```
📁 integration-platform

  🎉 Event Streams: es-platform
    📊 Kafka Topics:
      RAW:
        - provider.fhir.raw (3 partitions)
          → Ingesting FHIR patient/provider data
        - claims.transactions.raw (3 partitions)
          → Ingesting insurance claims

      ENRICHED:
        - provider.fhir.enriched (3 partitions)
          → Processed/validated FHIR data

      GENERAL:
        - claims.transactions.encrypted (3 partitions)
        - claims.transactions.decrypted (3 partitions)
          → Secure claims processing

  🚀 Applications: (9 running)
    - Event Streams pods processing data
    - CP4I Navigator for management

  🌐 Routes: (5 external)
    - Event Streams UI
    - CP4I Navigator
    - Admin/Registry APIs

📁 tools

  🚀 Applications:
    - ep-demo (Event Processing demo)
    - ea-flink-demo (Event Analytics demo)

  🌐 Routes:
    - ep-demo UI
```

**Demo script:**
1. "We're ingesting healthcare data from two sources: FHIR providers and insurance claims"
2. "Raw data flows through Event Streams topics"
3. "Event Processing enriches and validates the FHIR data"
4. "Claims are encrypted/decrypted for security compliance"
5. [Click Topology] "Here's the visual representation of the data flow"
6. [Click topic link] "Let's look at the raw FHIR topic configuration"

## Benefits

✅ **One-click access** to graphical topology views
✅ **Hierarchical organization** shows relationships
✅ **Data flow visualization** (RAW → ENRICHED → CURATED)
✅ **Perfect demo starting point** - everything in one place
✅ **Deep links** to every resource
✅ **Excludes infrastructure** - focuses on what you built
✅ **Multiple namespaces** supported
✅ **Live URLs** to running applications

## Future Enhancements

Potential improvements:
- [ ] Add Event Processing flows/instances
- [ ] Show API Connect APIs
- [ ] Include MQ queue managers
- [ ] Add App Connect flows
- [ ] Show resource utilization (CPU/Memory)
- [ ] Add health indicators per component
- [ ] Include recent changes for each resource
- [ ] Add "Copy demo script" button
- [ ] Export as presentation format
- [ ] Add search/filter for large deployments

---

**Created**: December 31, 2025
**Status**: ✅ Complete and Ready
**Version**: 1.0.0
