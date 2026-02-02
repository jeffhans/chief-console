# CP4I Chief Console - Roadmap & Enhancement Backlog

Living document tracking all proposed enhancements, organized by priority and status.

**Status Legend:**
- ✅ **DONE** - Implemented and working
- 🚧 **IN PROGRESS** - Currently being built
- 📋 **PLANNED** - Approved, not started
- 💡 **PROPOSED** - Good idea, needs discussion
- ❌ **REJECTED** - Decided not to do
- 🧊 **FROZEN** - Good idea, but not now

**Priority:**
- 🔥 **P0** - Critical, do now
- 🟡 **P1** - High value, do soon
- 🟢 **P2** - Nice to have, do eventually
- ⚪ **P3** - Low priority, maybe someday

**Effort:**
- 🟢 **S** (Small) - < 2 hours
- 🟡 **M** (Medium) - 2-8 hours
- 🔴 **L** (Large) - 1+ days
- ⚫ **XL** (Extra Large) - Multiple days

---

## ✅ **COMPLETED FEATURES**

### Core Foundation
- ✅ Environment management with TechZone PDF import
- ✅ OpenShift data collection via oc CLI
- ✅ Kafka/Event Streams data collection
- ✅ Self-contained HTML dashboard with "Meaningful Waves" design
- ✅ Change detection engine with categorization (Critical/Important/Informational)
- ✅ Automated monitoring with configurable intervals
- ✅ Operator deduplication (fixed display bug)
- ✅ Run time tracking and overlap prevention
- ✅ Snapshot-based comparison
- ✅ Out-of-cluster collection (laptop-based)

### Bug Fixes
- ✅ Fixed operator collection timeout (30s → 90s for large clusters)
- ✅ Fixed monitor overlap issue (enforces minimum gap between runs)

---

## 🔥 **P0 - CRITICAL (Do Now)**

### None currently

All critical features complete!

---

## 🟡 **P1 - HIGH VALUE (Do Soon)**

### 💡 **Kafka Topic Retention in Human-Readable Format**
- **Status:** 💡 PROPOSED
- **Effort:** 🟢 S (< 2 hours)
- **Value:** User's specific example - convert retention.ms to days
- **Details:**
  - Show "14.0 days" instead of "1209600000ms"
  - Add to topic table in dashboard
  - Highlight retention < 7 days or > 30 days
- **Data Source:** `oc get kafkatopic -o json` → `spec.config.retention.ms`
- **Location:** Wave 2 - CP4I Workloads → Event Streams section
- **Dependencies:** None

### 💡 **Total Storage by Component**
- **Status:** 💡 PROPOSED
- **Effort:** 🟡 M (4 hours)
- **Value:** Capacity planning, cost tracking
- **Details:**
  - Aggregate PVC sizes by component (Event Streams, Postgres, etc.)
  - Show total CP4I storage footprint
  - Percentage of cluster storage
  - Growth trends if multiple snapshots available
- **Data Source:** `oc get pvc -A -o json`
- **Location:** Wave 3 - Infrastructure → Storage section
- **Dependencies:** None

### 💡 **Certificate Expiration Tracking**
- **Status:** 💡 PROPOSED
- **Effort:** 🟡 M (4 hours)
- **Value:** Prevent production outages
- **Details:**
  - Extract cert expiration from routes
  - Check Kafka TLS certs
  - Warn if < 30 days to expiration
  - Critical alert if < 7 days
- **Data Source:** `oc get routes -o json` → `spec.tls.certificate`
- **Location:** Wave 1 - Executive Summary (warnings section)
- **Dependencies:** None

### 💡 **Cluster Capacity Summary Dashboard**
- **Status:** 💡 PROPOSED
- **Effort:** 🟡 M (6 hours)
- **Value:** Big picture view, capacity planning
- **Details:**
  - CPU: Total / Allocatable / Requested / Used
  - Memory: Total / Allocatable / Requested / Used
  - Storage: Total / Used / Available
  - Show what's reserved for system (Total - Allocatable)
  - Show headroom (Allocatable - Requested)
- **Data Source:** `oc get nodes -o json`, `oc get pods -A -o json`
- **Location:** Wave 1 - Executive Summary OR new Wave 0 "Cluster Overview"
- **Dependencies:** Need to query pod resource requests

### 💡 **Container Image Inventory**
- **Status:** 💡 PROPOSED
- **Effort:** 🟢 S (2 hours)
- **Value:** Security auditing, version tracking
- **Details:**
  - List all unique container images in use
  - Group by component (Event Streams, Platform Navigator, etc.)
  - Show image:tag for each pod
  - Highlight non-standard registries
- **Data Source:** `oc get pods -A -o json` → `spec.containers[].image`
- **Location:** Wave 3 - Infrastructure → new "Container Images" section
- **Dependencies:** None

---

## 🟢 **P2 - NICE TO HAVE (Do Eventually)**

### 💡 **Kafka Topic Compression Types**
- **Status:** 💡 PROPOSED
- **Effort:** 🟢 S (1 hour)
- **Value:** Performance insights
- **Details:**
  - Show compression.type for each topic
  - producer, lz4, snappy, gzip, zstd, none
  - Add to topic table
- **Data Source:** `oc get kafkatopic -o json` → `spec.config.compression.type`
- **Location:** Wave 2 - Event Streams topic table
- **Dependencies:** None

### 💡 **Kafka Topic Cleanup Policies**
- **Status:** 💡 PROPOSED
- **Effort:** 🟢 S (1 hour)
- **Value:** Understanding topic behavior
- **Details:**
  - Show cleanup.policy: "delete" or "compact"
  - Explain difference in dashboard tooltip
  - Highlight compacted topics (special use case)
- **Data Source:** `oc get kafkatopic -o json` → `spec.config.cleanup.policy`
- **Location:** Wave 2 - Event Streams topic table
- **Dependencies:** None

### 💡 **Environment Comparison View**
- **Status:** 💡 PROPOSED
- **Effort:** 🔴 L (2 days)
- **Value:** Configuration drift detection, dev/prod parity
- **Details:**
  - Load two snapshots side-by-side
  - Highlight differences:
    - Operator version drift
    - Configuration differences
    - Resource allocation differences
    - Missing components
  - Use cases: dev vs prod, before vs after upgrade
- **Data Source:** Two existing snapshot files
- **Location:** New comparison.html page or dashboard mode toggle
- **Dependencies:** Requires UI/UX design for comparison view

### 💡 **Storage Growth Trends**
- **Status:** 💡 PROPOSED
- **Effort:** 🟡 M (6 hours)
- **Value:** Capacity planning, disk usage alerts
- **Details:**
  - Track PVC size over multiple snapshots
  - Calculate daily/weekly growth rate
  - Project when storage will be full
  - Alert if growth rate > threshold
- **Data Source:** Historical snapshots
- **Location:** Wave 3 - Infrastructure → Storage section
- **Dependencies:** Requires multiple snapshots over time

### 💡 **Operator Upgrade History**
- **Status:** 💡 PROPOSED
- **Effort:** 🟡 M (4 hours)
- **Value:** Understanding upgrade path, troubleshooting
- **Details:**
  - Show "replaces" chain from CSV
  - Timeline of operator upgrades
  - Detect incomplete upgrades (operator stuck mid-upgrade)
- **Data Source:** `oc get csv -o json` → `spec.replaces`
- **Location:** Wave 2 - CP4I Workloads → Operators section
- **Dependencies:** None

### 💡 **Pod Quality of Service (QoS) Classes**
- **Status:** 💡 PROPOSED
- **Effort:** 🟢 S (2 hours)
- **Value:** Understanding pod eviction priority
- **Details:**
  - Show QoS class: Guaranteed, Burstable, BestEffort
  - Explain eviction order
  - Highlight BestEffort pods (will be killed first)
- **Data Source:** `oc get pods -o json` → `status.qosClass`
- **Location:** Wave 2 - CP4I Workloads → Pods section
- **Dependencies:** None

### 💡 **Network Policy Visualization**
- **Status:** 💡 PROPOSED
- **Effort:** 🔴 L (2 days)
- **Value:** Security understanding, troubleshooting connectivity
- **Details:**
  - Show network policies affecting CP4I namespaces
  - Visualize ingress/egress rules
  - Highlight deny-all policies
- **Data Source:** `oc get networkpolicy -A -o json`
- **Location:** Wave 3 - Infrastructure → new "Network" section
- **Dependencies:** Complex visualization needed

---

## 🌟 **P1 - ENHANCED CP4I CAPABILITIES**

### 💡 **API Connect Detection & Monitoring**
- **Status:** 💡 PROPOSED
- **Effort:** 🔴 L (1 day)
- **Value:** Complete CP4I capability coverage
- **Details:**
  - Detect API Connect instances
  - Count APIs, products, catalogs
  - Show gateway and portal status
  - Collect via CRDs (APIConnectCluster, etc.)
- **Data Source:** `oc get apiconnectcluster -A -o json`
- **Location:** Wave 2 - CP4I Workloads
- **Dependencies:** Need API Connect installed to test

### 💡 **App Connect Detection & Monitoring**
- **Status:** 💡 PROPOSED
- **Effort:** 🔴 L (1 day)
- **Value:** Complete CP4I capability coverage
- **Details:**
  - Detect Integration Servers
  - Show flows and connectors
  - Integration runtime status
- **Data Source:** `oc get integrationserver -A -o json`
- **Location:** Wave 2 - CP4I Workloads
- **Dependencies:** Need App Connect installed to test

### 💡 **MQ Detection & Monitoring**
- **Status:** 💡 PROPOSED
- **Effort:** 🔴 L (1 day)
- **Value:** Complete CP4I capability coverage
- **Details:**
  - Detect Queue Managers
  - Show queues and channels
  - Queue depth metrics
- **Data Source:** `oc get queuemanager -A -o json`
- **Location:** Wave 2 - CP4I Workloads
- **Dependencies:** Need MQ installed to test

### 💡 **Asset Repository Tracking**
- **Status:** 💡 PROPOSED
- **Effort:** 🟡 M (4 hours)
- **Value:** Track integration assets
- **Details:**
  - Detect Asset Repository instances
  - Show asset counts by type
  - Version tracking
- **Data Source:** `oc get assetrepository -A -o json`
- **Location:** Wave 2 - CP4I Workloads
- **Dependencies:** Need Asset Repo installed to test

---

## 🔔 **P2 - ALERTING & NOTIFICATIONS**

### 💡 **Slack Webhook Integration**
- **Status:** 💡 PROPOSED
- **Effort:** 🟡 M (4 hours)
- **Value:** Real-time alerts for teams
- **Details:**
  - Post to Slack when critical changes detected
  - Configurable webhook URL in config.yaml
  - Message includes summary and dashboard link
  - Throttling to avoid spam
- **Data Source:** Diff engine output
- **Location:** monitor.py enhancement
- **Dependencies:** None

### 💡 **Email Alerts**
- **Status:** 💡 PROPOSED
- **Effort:** 🟡 M (6 hours)
- **Value:** Alerts for critical issues
- **Details:**
  - Send email on critical changes
  - SMTP configuration
  - HTML email with summary
  - Attach dashboard HTML
- **Data Source:** Diff engine output
- **Location:** monitor.py enhancement
- **Dependencies:** SMTP configuration

### 💡 **Custom Alert Rules**
- **Status:** 💡 PROPOSED
- **Effort:** 🔴 L (2 days)
- **Value:** Flexible alerting for specific conditions
- **Details:**
  - YAML-based alert rules
  - Examples:
    - Alert if pod restarts > 5
    - Alert if storage > 80% full
    - Alert if operator stuck in Pending
  - Multiple notification channels
- **Data Source:** Snapshot data + rules engine
- **Location:** New alerting engine
- **Dependencies:** Significant design work

---

## 📊 **P2 - HISTORICAL TRENDS & METRICS**

### 💡 **Historical Trend Graphs**
- **Status:** 💡 PROPOSED
- **Effort:** ⚫ XL (3+ days)
- **Value:** Visualize changes over time
- **Details:**
  - Graph pod counts over time
  - Graph storage growth
  - Graph pod restart counts
  - Requires chart library (Chart.js or similar)
  - Load multiple snapshots
- **Data Source:** Multiple snapshots
- **Location:** New "Trends" section or wave
- **Dependencies:** Charting library, multiple snapshots

### 💡 **Resource Usage Metrics**
- **Status:** 💡 PROPOSED
- **Effort:** 🔴 L (2 days)
- **Value:** Performance monitoring
- **Details:**
  - Actual CPU/Memory usage (not just requests)
  - Requires metrics API
  - May overlap too much with Prometheus/Grafana
- **Data Source:** `oc adm top nodes`, `oc adm top pods`
- **Location:** Wave 3 - Infrastructure
- **Dependencies:** Metrics API must be available
- **Risk:** May be redundant with existing tools

### 💡 **Consumer Lag Tracking**
- **Status:** 💡 PROPOSED
- **Effort:** 🔴 L (1 day)
- **Value:** Critical for Kafka monitoring
- **Details:**
  - Show lag for each consumer group
  - Highlight groups with high lag
  - Trend over time
- **Data Source:** Complex - need to query Kafka directly or use Event Streams API
- **Location:** Wave 2 - Event Streams
- **Dependencies:** Event Streams API access
- **Risk:** Event Streams UI already shows this well

---

## 🌐 **P2 - MULTI-ENVIRONMENT FEATURES**

### 💡 **Multi-Environment Dashboard**
- **Status:** 💡 PROPOSED
- **Effort:** ⚫ XL (3+ days)
- **Value:** Manage dev/test/prod from one place
- **Details:**
  - Switch between environments
  - Side-by-side comparison
  - Aggregate view (all environments at once)
  - Environment status overview
- **Data Source:** Multiple environment configs
- **Location:** New dashboard mode
- **Dependencies:** Significant UI work

### 💡 **Environment Health Score**
- **Status:** 💡 PROPOSED
- **Effort:** 🟡 M (6 hours)
- **Value:** Quick health assessment
- **Details:**
  - Calculate health score (0-100)
  - Based on: failed pods, operator status, storage usage, cert expiration
  - Color-coded: Green/Yellow/Red
  - Trend over time
- **Data Source:** Snapshot data
- **Location:** Wave 1 - Executive Summary
- **Dependencies:** Need to define scoring algorithm

---

## 📚 **P3 - DOCUMENTATION & POLISH**

### 💡 **Architecture Documentation**
- **Status:** 💡 PROPOSED
- **Effort:** 🟡 M (4 hours)
- **Value:** Onboarding, understanding
- **Details:**
  - System architecture diagram
  - Data flow diagram
  - Component descriptions
  - Design decisions
- **Location:** ARCHITECTURE.md
- **Dependencies:** None

### 💡 **Troubleshooting Guide**
- **Status:** 💡 PROPOSED
- **Effort:** 🟡 M (4 hours)
- **Value:** Self-service support
- **Details:**
  - Common issues and solutions
  - Error message explanations
  - Debug mode instructions
  - FAQ section
- **Location:** TROUBLESHOOTING.md
- **Dependencies:** None

### 💡 **Video Walkthrough**
- **Status:** 💡 PROPOSED
- **Effort:** 🔴 L (1 day)
- **Value:** Demo, training, marketing
- **Details:**
  - Screen recording of installation → dashboard
  - Narrated walkthrough
  - Show monitoring in action
  - Use cases demonstration
- **Location:** YouTube/Vimeo + README link
- **Dependencies:** Video editing tools

### 💡 **Dashboard Export Capabilities**
- **Status:** 💡 PROPOSED
- **Effort:** 🟢 S (2 hours)
- **Value:** Reporting, sharing
- **Details:**
  - Export to PDF
  - Export to Markdown report
  - Export raw data to CSV/JSON
- **Location:** Dashboard enhancement
- **Dependencies:** PDF generation library

---

## ❌ **REJECTED IDEAS**

### ❌ **Real-Time Metrics (CPU/Memory Usage)**
- **Reason:** Prometheus/Grafana does this better
- **Alternative:** Link to Grafana dashboards from our dashboard

### ❌ **In-Cluster Deployment**
- **Reason:** Goes against "external/lightweight" core value
- **Alternative:** Keep it laptop-based, add webhook notifications instead

### ❌ **Advanced Kafka Message Browsing**
- **Reason:** Event Streams UI already does this well
- **Alternative:** Link to Event Streams UI for deep Kafka work

---

## 🧊 **FROZEN (Good Ideas, But Not Now)**

### 🧊 **Configuration Management (GitOps)**
- **Status:** 🧊 FROZEN
- **Reason:** Scope creep, overlaps with GitOps tools (ArgoCD, Flux)
- **Revisit:** If users request it

### 🧊 **Automated Remediation**
- **Status:** 🧊 FROZEN
- **Reason:** Too risky, outside core mission
- **Revisit:** After alerting is mature

### 🧊 **Multi-Cluster Support**
- **Status:** 🧊 FROZEN
- **Reason:** Adds significant complexity
- **Revisit:** After multi-environment is working well

---

## 🎯 **DECISION FRAMEWORK**

When evaluating new features, ask:

1. **Unique Value?** Can existing tools do this already?
2. **CLI-Only Data?** Is this hard to get elsewhere?
3. **Aligns with Core Mission?** Installation tracking? Change detection? External/lightweight?
4. **Effort vs Value?** Is the ROI worth it?
5. **Dependencies?** What do we need to build first?

**Core Mission Reminder:**
- 🎯 Installation progress tracking
- 🎯 Change detection & snapshot comparison
- 🎯 External/self-contained (no cluster resources)
- 🎯 CP4I-focused discovery
- 🎯 Lightweight alternative to heavy monitoring

---

## 📝 **NEXT SESSION PLANNING**

**Quick Wins to Consider:**
1. Kafka topic retention in days (2 hours)
2. Container image inventory (2 hours)
3. Total storage by component (4 hours)

**Total: ~8 hours of high-value work**

Would complete 3 high-value features from P1 backlog!

---

**Last Updated:** 2025-12-28
**Next Review:** TBD based on user priorities
