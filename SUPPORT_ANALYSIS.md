# CP4I Mission Console - Support & Troubleshooting Analysis

Comprehensive analysis of IBM Support data collection requirements vs Mission Console capabilities, based on:
- **11 real ACE PMRs** from CustomerName (Dec 2024)
- **IBM MustGather documentation** for CP4I components
- **Current Mission Console features**

---

## 📋 **IBM MustGather Requirements**

### **ACE (App Connect Enterprise) MustGather**

IBM Support typically requests:

| Data Item | Description | How Collected | Mission Console Status |
|-----------|-------------|---------------|----------------------|
| **Local Error Logs** | Unix syslog or Windows Event Log | Manual export | ❌ Not collected |
| **ACE Data Collector** | Configuration/topology snapshot | Run script manually | ❌ Not collected |
| **Toolkit Workspace** | Integration projects | Manual export | ❌ Not applicable |
| **User-Level Traces** | Application flow tracing | Enable in server.conf.yaml | ❌ Not collected |
| **Service-Level Traces** | Product diagnostics | Enable in server.conf.yaml | ❌ Not collected |
| **Global Cache Diagnostics** | WXS/EGC troubleshooting | Specific MustGather | ❌ Not collected |
| **Performance Data** | CPU/Memory/Thread dumps | Specific MustGather | ❌ Not collected |

### **Event Streams (Kafka) MustGather**

IBM Support typically requests:

| Data Item | Description | How Collected | Mission Console Status |
|-----------|-------------|---------------|----------------------|
| **Pod Logs** | All Event Streams pod logs | `ibm-events-must-gather` script | ⚠️ Partial (can add) |
| **Kafka Topic Config** | Topic settings, retention, etc | `oc get kafkatopic` | ✅ **Collected** |
| **Kafka CR Status** | EventStreams CR status | `oc get eventstreams` | ✅ **Collected** |
| **Operator Logs** | Event Streams operator logs | kubectl logs | ❌ Not collected |
| **Schema Registry** | Schema data if enabled | API calls | ❌ Not collected |
| **Geo-Replication** | Mirror Maker 2 status | CRD status | ❌ Not collected |

### **CP4I Platform MustGather**

| Data Item | Description | How Collected | Mission Console Status |
|-----------|-------------|---------------|----------------------|
| **Platform Navigator Logs** | PN operator and pods | Manual collection | ❌ Not collected |
| **OpenShift Cluster Logs** | Standard OCP diagnostics | `oc adm must-gather` | ❌ Not collected |
| **Cloud Pak Foundational Services** | Common services logs | Specific collection | ❌ Not collected |
| **Air-Gapped Environment Data** | Disconnected environment diagnostics | Special script | ❌ Not applicable |

---

## 🔥 **What the 11 PMRs Actually Showed**

### **Top Data Requests from Support (CustomerName PMRs)**

From analyzing the 11 ACE PMRs, IBM Support most frequently requested:

| Requested Data | Frequency | Example PMR | Mission Console Can Provide? |
|----------------|-----------|-------------|----------------------------|
| **Java version details** | 6 of 11 | TS020307479, TS020661140 | 🟡 **EASY WIN** - Container image inventory |
| **java.security file** | 3 of 11 | TS020307479 | 🟡 **EASY WIN** - Extract from ConfigMap |
| **server.conf.yaml** | 3 of 11 | TS020338441 | 🟡 **EASY WIN** - Extract from ConfigMap |
| **JSSE/Service traces** | 3 of 11 | TS020307479, TS020338441 | ❌ Requires enabling first |
| **Startup logs** | 2 of 11 | TS020338441 | 🟡 **CAN ADD** - Pod logs |
| **ACE Data Collector** | 2 of 11 | TS020373736 | ❌ Complex, separate script |
| **ulimit settings** | 2 of 11 | TS020746116 | 🟡 **CAN ADD** - Extract from nodes |
| **Storage/tmpdir details** | 2 of 11 | TS020240149, TS020744578 | 🟡 **CAN ADD** - PVC + df output |
| **Backend service logs** | 1 of 11 | TS020373736 | ❌ External system |
| **Timeline of changes** | ALL | (implicit in all cases) | ✅ **WE DO THIS!** |

---

## 💡 **Mission Console Current State**

### **What We Already Collect (Auto-Included in Snapshot)**

✅ **Cluster Info:**
- OpenShift version
- Node count, capacity, status
- API URL, console URL

✅ **Operators:**
- All installed operators
- Versions, phases, namespaces
- CP4I operators highlighted

✅ **Pods:**
- Status, restart counts
- Namespaces, labels
- Resource requests (partial)

✅ **Routes:**
- URLs for all services
- Platform Navigator, Event Streams UI, etc.

✅ **Kafka/Event Streams:**
- EventStreams instances
- Topics, partitions, replicas
- Consumer groups (best-effort)

✅ **Change Detection:**
- Snapshot comparison
- What changed since last run
- Timeline reconstruction

✅ **Namespaces:**
- All namespaces
- CP4I namespace detection

---

## 🎯 **Gap Analysis: What Support Needs vs What We Provide**

### **🔴 CRITICAL GAPS (Prevent Case Resolution)**

| Support Need | Current Status | Impact | Solution |
|-------------|----------------|---------|----------|
| **Pod Logs** | ❌ Not collected | Support asks in EVERY case | Add to support bundle |
| **ConfigMaps** | ❌ Not collected | Java settings, server config needed | Extract key ConfigMaps |
| **Events** | ❌ Not collected | Why pods crashed/restarted | `oc get events` |
| **Container Images** | ❌ Not collected | Java version confusion | Extract from pod specs |

### **🟡 HIGH-VALUE GAPS (Speed Up Resolution)**

| Support Need | Current Status | Impact | Solution |
|-------------|----------------|---------|----------|
| **Storage Details** | ⚠️ Partial (PVC sizes) | /tmp issues, disk space | Add tmpdir usage, storage by component |
| **Resource Limits** | ⚠️ Partial | OOM kills, resource contention | Full requests/limits/actual usage |
| **ulimit Settings** | ❌ Not collected | NPROC failures (TS020746116) | Extract from node config |
| **Java Version** | ❌ Not collected | 6 of 11 PMRs! | Parse from image or logs |
| **Operator Logs** | ❌ Not collected | Operator failures | Add to support bundle |

### **🟢 NICE-TO-HAVE (Reduce Back-and-Forth)**

| Support Need | Current Status | Impact | Solution |
|-------------|----------------|---------|----------|
| **Network Policies** | ❌ Not collected | Connectivity issues | `oc get networkpolicy` |
| **Secrets Count** | ❌ Not collected | Certificate issues | Count (not content!) |
| **Service Accounts** | ❌ Not collected | Permission issues | List SAs and roles |

---

## 🚀 **Support Bundle Feature Specification**

### **Goal:** One-command data collection that eliminates 80% of support back-and-forth

```bash
python3 chief_console.py --support-bundle
```

**Creates:** `support-bundle-YYYYMMDD-HHMMSS.tar.gz`

### **Bundle Contents (Proposed)**

#### **📊 Tier 1: Always Include (Core Diagnostics)**

```
support-bundle-20251228-220000/
├── README.txt                          # What's included, how to read
├── dashboard.html                      # Visual snapshot (current)
├── snapshots/
│   ├── snapshot-latest.json           # Current state
│   ├── snapshot-previous-1.json       # T-1 (if exists)
│   └── snapshot-previous-2.json       # T-2 (if exists)
├── cluster/
│   ├── cluster-info.txt               # Version, nodes, capacity
│   ├── nodes.yaml                     # All node details
│   ├── operators.yaml                 # All operators
│   ├── namespaces.yaml                # All namespaces
│   └── events.txt                     # Last 1 hour of events
├── cp4i/
│   ├── platform-navigator.yaml        # PN instance
│   ├── eventstreams.yaml              # ES instances
│   ├── operators-cp4i.yaml            # CP4I operators only
│   └── routes.yaml                    # CP4I routes
└── metadata/
    ├── collection-timestamp.txt
    ├── environment-name.txt
    └── chief-console-version.txt
```

#### **🔥 Tier 2: Add for Failed Pods (Auto-Detect)**

For any pod with status != Running or restartCount > 0:

```
├── logs/
│   ├── failed-pods/
│   │   ├── namespace-podname-container.log     # Last 1000 lines
│   │   ├── namespace-podname-previous.log      # Previous container (if crashed)
│   │   └── namespace-podname-describe.yaml     # Full pod description
│   └── operator-logs/
│       ├── cp4i-operator.log
│       ├── eventstreams-operator.log
│       └── [other-operators].log
```

#### **⚡ Tier 3: Configuration Files (Sanitized)**

Extract key ConfigMaps (with secret values redacted):

```
├── configs/
│   ├── ace/
│   │   ├── server.conf.yaml           # ACE server config
│   │   ├── java.security              # Java security settings
│   │   └── jvm-options.txt            # JVM arguments
│   ├── kafka/
│   │   ├── kafka-topics.yaml          # All topic configs
│   │   ├── kafka-users.yaml           # Users (sanitized)
│   │   └── cluster-config.yaml        # ES cluster config
│   └── platform/
│       └── platform-navigator.yaml
```

#### **📈 Tier 4: Resource & Health Details**

```
├── resources/
│   ├── storage/
│   │   ├── pvc-summary.txt            # All PVCs with sizes
│   │   ├── storage-by-component.txt   # Aggregated usage
│   │   └── pv-details.yaml            # PV details
│   ├── limits/
│   │   ├── resource-requests.txt      # Pod requests/limits
│   │   ├── node-capacity.txt          # Node capacity summary
│   │   └── ulimits.txt                # Node ulimit settings (if available)
│   └── images/
│       ├── container-images.txt       # All images in use
│       └── java-versions.txt          # Detected Java versions
```

#### **🔍 Tier 5: Change History**

```
├── changes/
│   ├── change-summary.txt             # High-level changes
│   ├── change-timeline.txt            # Timeline view
│   ├── critical-changes.txt           # Critical changes only
│   └── diff-latest.json               # Full diff data
```

---

## 📊 **Coverage Analysis: Support Bundle vs MustGather**

### **ACE MustGather Coverage**

| MustGather Requirement | Support Bundle Coverage | Gap? |
|------------------------|------------------------|------|
| Local Error Logs | ✅ Pod logs included | |
| ACE Data Collector | ⚠️ Partial (pod/config data, not full collector) | Need custom script integration |
| Toolkit Workspace | ❌ Not applicable (runtime focus) | |
| User-Level Traces | ❌ Must be enabled separately | Document how to enable |
| Service-Level Traces | ❌ Must be enabled separately | Document how to enable |
| Java Settings | ✅ java.security, JVM args | |
| Server Config | ✅ server.conf.yaml | |

**Coverage:** ~60% of typical requests

### **Event Streams MustGather Coverage**

| MustGather Requirement | Support Bundle Coverage | Gap? |
|------------------------|------------------------|------|
| Pod Logs | ✅ All ES pod logs | |
| Kafka Topic Config | ✅ Full topic CRDs | |
| Kafka CR Status | ✅ EventStreams CRs | |
| Operator Logs | ✅ ES operator logs | |
| Schema Registry | ⚠️ CRD only, not data | |
| Geo-Replication | ✅ Mirror Maker CRDs | |

**Coverage:** ~85% of typical requests

### **CP4I Platform MustGather Coverage**

| MustGather Requirement | Support Bundle Coverage | Gap? |
|------------------------|------------------------|------|
| Platform Navigator Logs | ✅ PN pod logs | |
| OpenShift Cluster Logs | ⚠️ Partial (events, not full must-gather) | |
| Cloud Pak Foundational Services | ⚠️ Partial (operators, not full logs) | |
| Operator Logs | ✅ All operator logs | |

**Coverage:** ~70% of typical requests

### **Overall Coverage Estimate**

**Before Mission Console Support Bundle:** 0% (customer manually collects everything)

**With Mission Console Support Bundle:** ~70% of data requested in first message

**Impact:**
- Eliminates 2-3 rounds of "send us X" requests
- Gets critical data to support immediately
- Reduces time-to-resolution by days

---

## 🏆 **Quick Wins: Highest-Impact Additions**

Based on PMR frequency and MustGather requirements:

### **🔥 P0: Build Now (4-6 hours total)**

1. **Pod Logs Collection** (2 hours)
   - Last 1000 lines from failed pods
   - Previous container logs if crashed
   - `oc logs` for detected failures

2. **ConfigMap Extraction** (2 hours)
   - java.security
   - server.conf.yaml
   - Sanitize secrets (redact passwords, tokens)

3. **Container Image Inventory** (1 hour)
   - Extract from pod specs
   - Parse Java version from image tags or logs

4. **Events Collection** (1 hour)
   - `oc get events --all-namespaces`
   - Last 1 hour of events
   - Filter to CP4I namespaces

### **🟡 P1: Add Next (8-10 hours total)**

5. **Operator Logs** (2 hours)
   - All CP4I operator logs
   - Last 1000 lines

6. **Storage Details** (3 hours)
   - PVC summaries
   - Storage by component
   - Tmpdir usage (if accessible)

7. **Resource Limits Summary** (2 hours)
   - Requests vs Limits table
   - Node capacity summary
   - Identify over/under-provisioned pods

8. **Change Timeline Export** (2 hours)
   - Human-readable timeline
   - Critical changes highlighted
   - Timeline.txt file

### **🟢 P2: Nice to Have (Later)**

9. **ulimit Settings**
   - Extract from node config
   - Show NPROC, NOFILE

10. **Network Policies**
    - Show policies affecting CP4I

11. **Service Account Details**
    - List SAs and role bindings

---

## 💬 **Real PMR Scenarios: Before vs After**

### **Scenario 1: SSL/TLS Handshake Failure (TS020307479)**

**Without Mission Console:**
```
Day 1: Customer: "SSL errors"
Day 1: Support: "Send us java.security file"
Day 2: Customer: "How do I get that?"
Day 2: Support: "Run these commands..."
Day 3: Customer: *sends file*
Day 3: Support: "What Java version?"
Day 4: Customer: *checks* "Java 8"
Day 4: Support: "Send us JSSE traces"
Day 5: Customer: "How do I enable those?"
...
```

**With Mission Console:**
```
Day 1: Customer: "SSL errors"
Day 1: Customer: *attaches support-bundle.tar.gz*
Day 1: Support: *opens bundle*
       - Sees: Java 8 (from image inventory)
       - Sees: java.security file with RSAPSS disabled
       - Sees: Events showing SSL errors at 2:15pm
       - Sees: Change detection shows java.security modified at 2:10pm
Day 1: Support: "The java.security change at 2:10pm likely caused this..."
```

**Time saved:** 4 days

---

### **Scenario 2: Global Cache Outage (TS020746116)**

**Without Mission Console:**
```
Day 1: Customer: "500k claims backed up, WXS failing"
Day 1: Support: "When did this start?"
Day 1: Customer: "Not sure"
Day 2: Support: "Send pod logs for WXS"
Day 3: Customer: *sends logs*
Day 3: Support: "Check ulimits"
Day 4: Customer: "How?"
Day 4: Support: "SSH to nodes, run ulimit -a"
Day 5: Customer: "NPROC is 1024"
Day 5: Support: "That's too low, raise to 32768"
...
```

**With Mission Console:**
```
Day 1: Customer: "500k claims backed up"
Day 1: Customer: *attaches support-bundle.tar.gz*
Day 1: Support: *opens bundle*
       - Timeline shows: WXS pods started restarting at 2:15pm
       - Events show: NPROC ulimit failures
       - Resource limits show: NPROC: 1024 (too low)
       - Change detection: No config changes, pods just hit limit
Day 1: Support: "Raise NPROC to 32768, restart WXS pods"
```

**Time saved:** 4 days

---

## 🎯 **Recommendation: Build Support Bundle MVP**

### **Scope: 2-Day Sprint**

**Day 1: Core Collection (6 hours)**
- Pod logs (failed pods only)
- ConfigMaps (java.security, server.conf.yaml)
- Events (last hour)
- Container images

**Day 2: Packaging & Testing (6 hours)**
- tar.gz creation
- README generation
- Sanitization (redact secrets)
- Test on real cluster

### **Deliverable:**

```bash
python3 chief_console.py --support-bundle

# Output:
# ✅ Collecting cluster data...
# ✅ Collecting pod logs (3 failed pods)...
# ✅ Extracting ConfigMaps...
# ✅ Gathering events...
# ✅ Creating support bundle...
#
# 📦 Support bundle created: support-bundle-20251228-220000.tar.gz
# 📏 Size: 15.3 MB
#
# Contents:
#   - Dashboard HTML
#   - 3 snapshots (change history)
#   - 8 pod logs
#   - 12 ConfigMaps
#   - 500 events
#   - 45 container images
#
# Attach this file to your support case!
```

### **Success Metrics:**

- **Coverage:** ~70% of MustGather data in one file
- **Time Savings:** Eliminate 2-3 support request rounds
- **File Size:** < 50 MB (attachable to support cases)
- **Effort:** ~12 hours development

---

## 📝 **Next Steps**

1. **User Approval:** Confirm support bundle approach
2. **Build MVP:** 2-day focused sprint
3. **Test on Real Cases:** Try with next PMR
4. **Iterate:** Add more based on feedback
5. **Document:** Update MONITORING.md with support bundle usage

---

**Priority:** 🔥 **HIGHEST** - Directly addresses real pain from 11 PMRs
**ROI:** Massive - Days saved per support case
**Complexity:** Medium - Mostly orchestrating existing oc commands
**Risk:** Low - Read-only data collection
