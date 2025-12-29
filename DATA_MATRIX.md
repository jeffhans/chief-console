# CP4I Data Availability Matrix

A comprehensive comparison of what data is available where, and opportunities for Mission Console to provide unique insights.

**Legend:**
- ✅ Easily accessible
- ⚠️ Available but hard to find/interpret
- ❌ Not available
- 🔍 CLI/API only

---

## 🏗️ **CLUSTER INFRASTRUCTURE**

| Data Point | OpenShift Console | Platform Navigator | Mission Console | CLI Only? | Notes |
|------------|-------------------|-------------------|-----------------|-----------|-------|
| **Cluster version** | ✅ | ❌ | ✅ | | |
| **Node count** | ✅ | ❌ | ✅ | | |
| **Node status (Ready/NotReady)** | ✅ | ❌ | ✅ | | |
| **Node roles (master/worker)** | ✅ | ❌ | ✅ | | |
| **CPU capacity per node** | ✅ | ❌ | ✅ | | |
| **Memory capacity per node** | ✅ | ❌ | ✅ | | |
| **Max pods per node** | ⚠️ | ❌ | ❌ | 🔍 | Hidden in node details |
| **Allocatable vs Total resources** | ⚠️ | ❌ | ❌ | 🔍 | System reserved resources |
| **Node taints/tolerations** | ⚠️ | ❌ | ❌ | 🔍 | Affects pod scheduling |
| **Total cluster storage (PVs)** | ⚠️ | ❌ | ❌ | 🔍 | Hard to aggregate |
| **Storage class details** | ✅ | ❌ | ❌ | | |

**🎯 Opportunity:** Aggregated cluster capacity view with allocatable vs used

---

## 🔧 **OPERATORS & CAPABILITIES**

| Data Point | OpenShift Console | Platform Navigator | Mission Console | CLI Only? | Notes |
|------------|-------------------|-------------------|-----------------|-----------|-------|
| **Installed operators** | ✅ | ❌ | ✅ | | |
| **Operator versions** | ✅ | ❌ | ✅ | | |
| **Operator phase (Succeeded/Failed)** | ✅ | ❌ | ✅ | | |
| **CP4I capabilities** | ❌ | ✅ | ✅ | | Platform Nav shows instances |
| **Operator install timestamp** | ⚠️ | ❌ | ✅ | | creationTimestamp |
| **Replaces chain (upgrade path)** | ⚠️ | ❌ | ❌ | 🔍 | Shows upgrade history |
| **Operator dependencies** | ❌ | ❌ | ❌ | 🔍 | Which operators require others |
| **Operator resource usage** | ⚠️ | ❌ | ❌ | 🔍 | CPU/mem per operator |
| **Failed operator reason** | ⚠️ | ❌ | ✅ | | In CSV status |

**🎯 Opportunity:** Operator upgrade history and dependency mapping

---

## 📦 **PODS & WORKLOADS**

| Data Point | OpenShift Console | Platform Navigator | Mission Console | CLI Only? | Notes |
|------------|-------------------|-------------------|-----------------|-----------|-------|
| **Pod count** | ✅ | ⚠️ | ✅ | | Platform Nav shows per capability |
| **Pod status** | ✅ | ⚠️ | ✅ | | |
| **Restart count** | ✅ | ❌ | ✅ | | |
| **Pod age** | ✅ | ❌ | ❌ | | |
| **Container image versions** | ✅ | ❌ | ❌ | | Critical for auditing |
| **Resource requests** | ✅ | ❌ | ❌ | | What pod asked for |
| **Resource limits** | ✅ | ❌ | ❌ | | Max pod can use |
| **Actual resource usage** | ✅ (metrics) | ❌ | ❌ | | Requires metrics API |
| **Pod placement (which node)** | ✅ | ❌ | ❌ | | Scheduling info |
| **Quality of Service (QoS) class** | ⚠️ | ❌ | ❌ | 🔍 | Guaranteed/Burstable/BestEffort |
| **Pod disruption budgets** | ⚠️ | ❌ | ❌ | 🔍 | HA configuration |

**🎯 Opportunity:** Container image inventory and QoS class visibility

---

## 🎯 **EVENT STREAMS (KAFKA)**

| Data Point | Event Streams UI | OpenShift Console | Mission Console | CLI Only? | Notes |
|------------|------------------|-------------------|-----------------|-----------|-------|
| **Cluster instances** | ✅ | ⚠️ | ✅ | | |
| **Cluster status** | ✅ | ⚠️ | ✅ | | |
| **Kafka version** | ✅ | ❌ | ❌ | | |
| **Broker count** | ✅ | ❌ | ✅ | | We show pods |
| **Topic count** | ✅ | ❌ | ✅ | | |
| **Topic names** | ✅ | ❌ | ✅ | | |
| **Topic partitions** | ✅ | ❌ | ✅ | | |
| **Topic replicas** | ✅ | ❌ | ✅ | | |
| **Topic retention (days)** | ⚠️ | ❌ | ❌ | 🔍 | **YOUR EXAMPLE!** retention.ms → days |
| **Topic compression type** | ⚠️ | ❌ | ❌ | 🔍 | producer/lz4/snappy/gzip/zstd |
| **Topic segment size** | ⚠️ | ❌ | ❌ | 🔍 | Affects performance |
| **Topic cleanup policy** | ⚠️ | ❌ | ❌ | 🔍 | delete vs compact |
| **Consumer groups** | ✅ | ❌ | ⚠️ | | We try, not reliable |
| **Consumer lag** | ✅ | ❌ | ❌ | | **CRITICAL METRIC** |
| **Topic size (bytes)** | ✅ | ❌ | ❌ | | Disk usage per topic |
| **Messages per second** | ✅ | ❌ | ❌ | | Throughput metrics |
| **Under-replicated partitions** | ✅ | ❌ | ❌ | | Health indicator |
| **Topic ACLs** | ✅ | ❌ | ❌ | | Security/permissions |
| **Schema registry** | ✅ | ❌ | ❌ | | If enabled |
| **Geo-replication status** | ✅ | ❌ | ❌ | | Mirror Maker 2 |

**🎯 Opportunity:** Topic retention in human-readable days, compression types, cleanup policies

---

## 🌐 **NETWORKING & ROUTES**

| Data Point | OpenShift Console | Platform Navigator | Mission Console | CLI Only? | Notes |
|------------|-------------------|-------------------|-----------------|-----------|-------|
| **Routes** | ✅ | ✅ | ✅ | | Platform Nav shows capability UIs |
| **Route URLs** | ✅ | ✅ | ✅ | | |
| **TLS/certificate status** | ✅ | ❌ | ❌ | | |
| **Certificate expiration** | ⚠️ | ❌ | ❌ | 🔍 | **CRITICAL for prod** |
| **Ingress controllers** | ✅ | ❌ | ❌ | | |
| **Services** | ✅ | ❌ | ❌ | | ClusterIP, LoadBalancer, etc |
| **Network policies** | ⚠️ | ❌ | ❌ | 🔍 | Firewall rules |
| **Service mesh (if installed)** | ⚠️ | ❌ | ❌ | | Istio/Maistra |

**🎯 Opportunity:** Certificate expiration tracking and alerting

---

## 💾 **STORAGE**

| Data Point | OpenShift Console | Platform Navigator | Mission Console | CLI Only? | Notes |
|------------|-------------------|-------------------|-----------------|-----------|-------|
| **PVC count** | ✅ | ❌ | ❌ | | |
| **PVC size** | ✅ | ❌ | ❌ | | |
| **PVC status (Bound/Pending)** | ✅ | ❌ | ❌ | | |
| **Storage class** | ✅ | ❌ | ❌ | | |
| **Total storage used** | ⚠️ | ❌ | ❌ | 🔍 | Need to aggregate PVCs |
| **Storage by workload** | ❌ | ❌ | ❌ | 🔍 | Kafka vs Postgres vs etc |
| **Actual usage vs requested** | ⚠️ | ❌ | ❌ | 🔍 | Requires exec into pods |
| **Storage growth rate** | ❌ | ❌ | ❌ | 🔍 | Trend over time |

**🎯 Opportunity:** Storage aggregation by CP4I component with growth trends

---

## 🔐 **SECURITY & COMPLIANCE**

| Data Point | OpenShift Console | Platform Navigator | Mission Console | CLI Only? | Notes |
|------------|-------------------|-------------------|-----------------|-----------|-------|
| **Service accounts** | ✅ | ❌ | ❌ | | |
| **Roles/RoleBindings** | ✅ | ❌ | ❌ | | |
| **ClusterRoles** | ✅ | ❌ | ❌ | | |
| **Security Context Constraints** | ✅ | ❌ | ❌ | | OpenShift-specific |
| **Pod Security Standards** | ⚠️ | ❌ | ❌ | | Restricted/Baseline/Privileged |
| **Secrets count** | ✅ | ❌ | ❌ | | |
| **ConfigMaps count** | ✅ | ❌ | ❌ | | |
| **Image vulnerabilities** | ⚠️ | ❌ | ❌ | | Requires scanning tools |
| **Compliance reports** | ❌ | ❌ | ❌ | | Requires compliance operator |

**🎯 Opportunity:** Security posture summary for CP4I components

---

## 📊 **CHANGE TRACKING**

| Data Point | OpenShift Console | Platform Navigator | Mission Console | CLI Only? | Notes |
|------------|-------------------|-------------------|-----------------|-----------|-------|
| **What changed recently** | ❌ | ❌ | ✅ | | **OUR UNIQUE VALUE!** |
| **Operator additions** | ❌ | ❌ | ✅ | | Change detection |
| **Pod restarts** | ⚠️ | ❌ | ✅ | | Need to track over time |
| **Configuration changes** | ❌ | ❌ | ❌ | | ConfigMap/Secret diffs |
| **Resource scaling events** | ⚠️ | ❌ | ❌ | | Pod count changes |
| **Snapshot comparison** | ❌ | ❌ | ✅ | | **OUR UNIQUE VALUE!** |
| **Environment drift** | ❌ | ❌ | ❌ | | Dev vs Prod differences |

**🎯 Opportunity:** Configuration drift detection between snapshots

---

## 🎭 **CP4I SPECIFIC CAPABILITIES**

### **API Connect** (if installed)

| Data Point | API Connect UI | OpenShift Console | Mission Console | CLI Only? |
|------------|---------------|-------------------|-----------------|-----------|
| API count | ✅ | ❌ | ❌ | |
| Product count | ✅ | ❌ | ❌ | |
| Gateway instances | ✅ | ⚠️ | ❌ | |
| Portal status | ✅ | ⚠️ | ❌ | |
| Analytics | ✅ | ❌ | ❌ | |

### **App Connect** (if installed)

| Data Point | App Connect UI | OpenShift Console | Mission Console | CLI Only? |
|------------|---------------|-------------------|-----------------|-----------|
| Integration servers | ✅ | ⚠️ | ❌ | |
| Flows | ✅ | ❌ | ❌ | |
| Connectors | ✅ | ❌ | ❌ | |

### **MQ** (if installed)

| Data Point | MQ Console | OpenShift Console | Mission Console | CLI Only? |
|------------|-----------|-------------------|-----------------|-----------|
| Queue managers | ✅ | ⚠️ | ❌ | |
| Queues | ✅ | ❌ | ❌ | |
| Queue depth | ✅ | ❌ | ❌ | |
| Channels | ✅ | ❌ | ❌ | |

**🎯 Opportunity:** Unified view across all CP4I capabilities

---

## 🏆 **MISSION CONSOLE UNIQUE VALUE PROPOSITIONS**

Based on the matrix above, here are the **highest-value additions**:

### **1. CLI-Only Data (Hidden Gold)**

These are available nowhere else in an easy-to-consume format:

- **Kafka topic retention in days** (not milliseconds)
- **Topic compression types** (producer/lz4/snappy/gzip/zstd)
- **Topic cleanup policies** (delete vs compact)
- **Max pods per node** (capacity planning)
- **Allocatable vs total resources** (system overhead visibility)
- **Certificate expiration dates** (prevent outages)
- **Total storage by component** (Event Streams: 150GB, Postgres: 20GB, etc.)
- **Operator upgrade history** (what replaced what)
- **Container image inventory** (what's actually running)
- **QoS classes** (pod priority/eviction behavior)

### **2. Aggregation Across Components**

Hard to see the big picture in individual UIs:

- **Total CP4I storage usage** (sum all PVCs for CP4I namespaces)
- **Storage growth trends** (compare snapshots over days/weeks)
- **Resource requests vs limits summary** (over/under provisioned?)
- **Cross-capability view** (Event Streams + API Connect + App Connect in one table)

### **3. Change Detection (Our Superpower)**

Nobody else does this well:

- **Configuration drift** (dev vs prod snapshot comparison)
- **What changed in last N minutes** (already doing this!)
- **Installation progress tracking** (from zero to fully installed)
- **Upgrade tracking** (operator version changes over time)

### **4. External/Portable**

Value from being outside the cluster:

- **Self-contained HTML snapshots** (email/archive cluster state)
- **Environment comparison** (side-by-side dev/test/prod)
- **Pre-Platform-Navigator dashboard** (during install)
- **Lightweight/no infrastructure** (just oc CLI)

---

## 🎯 **RECOMMENDED NEXT STEPS**

### **Phase 1: Quick Wins (CLI-Only Data)**

Add these high-value, easy-to-collect data points:

1. **Kafka topic retention in human-readable format**
   - `retention.ms → days`
   - Show in topic table: "14 days" not "1209600000ms"

2. **Total storage by component**
   - Aggregate PVCs: Event Streams, Postgres, etc.
   - Show trends if multiple snapshots

3. **Certificate expiration tracking**
   - Check route TLS certs
   - Warn if < 30 days to expiration

4. **Container image inventory**
   - What images are actually running
   - Group by component (all Event Streams images)

### **Phase 2: Aggregation Views**

5. **Cluster capacity summary**
   - Total CPU/Memory: Capacity / Allocatable / Requested / Used
   - Storage: Total / Used / Available

6. **CP4I resource footprint**
   - CPU/Memory/Storage used by all CP4I components
   - Percentage of cluster capacity

### **Phase 3: Enhanced Change Detection**

7. **Configuration drift detection**
   - Compare ConfigMaps/Secrets between snapshots
   - Highlight changed values

8. **Environment comparison**
   - Load two snapshots (dev vs prod)
   - Show differences side-by-side

---

## 📋 **Data Collection Priorities**

| Priority | Data Point | Reason | Difficulty |
|----------|-----------|--------|------------|
| 🔥 **HIGH** | Topic retention (days) | Your example, easy win | Easy |
| 🔥 **HIGH** | Total storage by component | Capacity planning | Easy |
| 🔥 **HIGH** | Certificate expiration | Prevent outages | Medium |
| 🔥 **HIGH** | Container image inventory | Security/auditing | Easy |
| 🟡 **MEDIUM** | Cluster capacity summary | Overview dashboard | Easy |
| 🟡 **MEDIUM** | Topic compression types | Performance insights | Easy |
| 🟡 **MEDIUM** | QoS classes | Pod priority understanding | Medium |
| 🟢 **LOW** | Consumer lag | Event Streams UI shows this | Hard |
| 🟢 **LOW** | Metrics (CPU/mem usage) | Grafana does this better | Hard |

---

## 🤔 **Questions to Guide Direction**

1. **Primary use case:** Installation tracking or ongoing monitoring?
2. **Target audience:** Yourself, team, customers, demos?
3. **Update frequency:** Real-time (seconds) or periodic (minutes/hours)?
4. **Most painful gap:** What do you find yourself checking manually most often?
5. **Environment lifecycle:** How long do TechZone environments last?

---

**Your input:** What jumps out as most valuable to you?
