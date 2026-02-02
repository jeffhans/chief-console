# CP4I Mission Console - Getting Started Guide

Welcome! This guide will help you set up and run the CP4I Mission Console on your TechZone OpenShift cluster.

---

## 📋 What Is This?

The **CP4I Mission Console** is a lightweight dashboard that gives you insights into your Cloud Pak for Integration (CP4I) deployment:

- 📊 **Executive Summary** - Cluster health at a glance
- 🔧 **CP4I Capabilities** - What's installed and running
- 🎯 **Demo Artifacts** - Your custom applications organized hierarchically
- 💰 **Licensing Cost Map** - VPC usage and license consumption
- 🎯 **Workload Health** - Just your business applications (no infrastructure noise)
- 🚦 **Criticality Tiers** - What's critical vs optional
- 📊 **Resource Utilization** - CPU/Memory consumption
- 🏗️ **Infrastructure** - Nodes, operators, pods
- 🔄 **What Changed** - Detect changes since last run
- 📑 **Excel Export** - Customer-friendly spreadsheet for licensing collaboration

**Features:**
- 🎯 **Cluster-Aware** - Automatically organizes outputs by cluster (multi-cluster support!)
- 🚀 **Auto-Open** - Dashboard automatically opens in your browser
- 📊 **Excel Export** - Generate detailed licensing/sizing spreadsheets
- 🔄 **Automated Monitoring** - Continuous monitoring with configurable intervals

**Time to value:** ~5 minutes from clone to dashboard

---

## ✅ Prerequisites

### Required Software

1. **Python 3.8+**
   ```bash
   python3 --version  # Should show 3.8 or higher
   ```

2. **OpenShift CLI (`oc`)**
   ```bash
   oc version  # Should show client version
   ```

3. **Git** (to clone the repo)
   ```bash
   git version
   ```

### Required Access

1. **OpenShift Cluster Access**
   - You must be logged into your cluster via `oc login`
   - You need read access to:
     - Cluster info (nodes, namespaces)
     - Pods and routes in CP4I namespaces
     - Operators
     - Custom resources (EventStreams, EventProcessing, etc.)

2. **Permissions Needed**
   - Typically **cluster-reader** role is sufficient
   - Or **view** role in CP4I namespaces

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Clone the Repository

```bash
cd ~/Documents  # or wherever you keep projects
git clone <repository-url> chief-console
cd chief-console
```

**Don't have the repo URL?** Ask the person who shared this with you!

### Step 2: Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

**Expected output:** Should install `pyyaml`, `openpyxl` (for Excel export), and other dependencies.

### Step 3: Login to Your OpenShift Cluster

```bash
# Get your login command from the OpenShift Console
# Top-right corner → Your Name → Copy Login Command

oc login --token=sha256~XXXXX --server=https://api.your-cluster.com:6443
```

**Verify you're logged in:**
```bash
oc whoami
oc get nodes  # Should list your cluster nodes
```

### Step 4: Run the Mission Console

```bash
python3 chief_console.py
```

**Expected output:**
```
======================================================================
CP4I MISSION CONSOLE
======================================================================

📍 Cluster: your-cluster-name
   Server: https://api.your-cluster.com:6443
   User: kube:admin

💾 Output directory: output/your-cluster.com/

Step 1: Collecting cluster data...
...
Step 2: Detecting changes...
...
Step 3: Categorizing resources...
  ✓ Categorized 58 pods
  ✓ Total VPC: 3.12
...
Step 4: Rendering dashboard...
...
Step 5: Exporting to Excel...

📊 Generating Excel export...
✓ Excel file created: output/your-cluster.com/chief-console-20260104-182322.xlsx

======================================================================
MISSION CONSOLE READY
======================================================================

Dashboard: output/your-cluster.com/dashboard.html
Snapshot:  output/your-cluster.com/snapshots/snapshot-20260104-182322.json
Excel:     output/your-cluster.com/chief-console-20260104-182322.xlsx

🚀 Opening dashboard in browser...
   ✓ Dashboard opened: /path/to/output/your-cluster.com/dashboard.html

📊 Excel file location:
   /path/to/output/your-cluster.com/chief-console-20260104-182322.xlsx
```

**🎉 You're done!** The dashboard automatically opens in your browser!

---

## 📁 What Got Created?

After your first run, you'll see a **cluster-specific directory structure**:

```
chief-console/
├── output/
│   └── your-cluster.com/                    ← Cluster-specific directory
│       ├── dashboard.html                   ← Your dashboard (auto-opens!)
│       ├── chief-console-TIMESTAMP.xlsx   ← Excel export
│       └── snapshots/
│           └── snapshot-TIMESTAMP.json      ← Historical snapshots
├── src/                                     ← Python code (don't need to modify)
├── demo_metadata.yaml                       ← Customize display names here
├── resource_categories.yaml                 ← Customize categorization rules
├── chief_console.py                       ← Main entry point
└── monitor.py                               ← Automated monitoring (optional)
```

**✨ Multi-Cluster Support:** Each cluster gets its own directory! Switch between clusters freely:
```
output/
├── cluster-a.techzone.ibm.com/
│   ├── dashboard.html
│   ├── chief-console-*.xlsx
│   └── snapshots/
├── cluster-b.techzone.ibm.com/
│   ├── dashboard.html
│   ├── chief-console-*.xlsx
│   └── snapshots/
└── prod-cluster.example.com/
    ├── dashboard.html
    ├── chief-console-*.xlsx
    └── snapshots/
```

---

## 🎨 Customizing for Your Environment

### 1. Add Display Names for Your Resources

Edit `demo_metadata.yaml` to add business-friendly names:

```yaml
# Kafka Topics
topics:
  my.custom.topic:
    display_name: "Customer Orders"
    description: "Real-time customer order events"
    business_purpose: "Order processing pipeline"
    owner: "Order Management Team"

# Applications
applications:
  my-app-.*:  # Regex pattern
    display_name: "My Custom Application"
    description: "Does something awesome"
    business_purpose: "Delivers business value"
    owner: "My Team"

# Routes
routes:
  my-app-route:
    display_name: "My App UI"
    description: "User interface for my application"
```

### 2. Adjust Resource Categorization

Edit `resource_categories.yaml` to customize:

**Mark pods as business workloads:**
```yaml
workloads:
  business_workload_patterns:
    - "my-app-.*"
    - "customer-.*"
    - "order-.*"
```

**Adjust criticality:**
```yaml
criticality:
  critical:
    patterns:
      - "my-critical-app.*"
```

**Mark as CP4I licensed (for VPC calculation):**
```yaml
licensing:
  cp4i_licensed:
    patterns:
      - "my-cp4i-component.*"
```

---

## 🔄 Running Regularly

### One-Time Run
```bash
python3 chief_console.py
```

### Automated Monitoring (Recommended!)

Use the **monitor script** for continuous monitoring:

```bash
# Run every 2 minutes (default)
python3 monitor.py

# Run every 5 minutes
python3 monitor.py --interval 300

# Run every 2 minutes and auto-open dashboard
python3 monitor.py --auto-open

# Run 10 times then stop
python3 monitor.py --max-runs 10

# Quick monitoring (every 30 seconds, 20 times)
python3 monitor.py --interval 30 --max-runs 20
```

**Monitor Output:**
```
======================================================================
CP4I MISSION CONSOLE - AUTOMATED MONITORING
======================================================================
📍 Cluster: your-cluster-name
   Server: https://api.your-cluster.com:6443
   User: kube:admin

Monitoring interval: 120 seconds (2 minutes)
Auto-open dashboard: Yes
Max runs: Unlimited

Press Ctrl+C to stop monitoring
======================================================================

RUN #1 - 2026-01-04 18:44:13
======================================================================
✅ No significant changes detected
✅ Collection #1 complete
   📊 Dashboard opened: /path/to/output/your-cluster.com/dashboard.html

⏱️  Collection took 48.9s
⏳ Next run in 71 seconds...
```

**Features:**
- 🎯 **Cluster-Aware** - Monitors the current cluster automatically
- 🔄 **Smart Interval** - Accounts for collection time (interval = time between starts)
- 📊 **Change Detection** - Highlights critical and important changes
- 🚀 **Auto-Open** - Optionally opens dashboard after each run
- ⏱️  **Duration Tracking** - Shows collection time and warns if too slow

### Scheduled Run (cron - alternative to monitor)

**macOS/Linux (cron):**
```bash
# Edit crontab
crontab -e

# Add this line to run every hour
0 * * * * cd /path/to/chief-console && /usr/bin/python3 chief_console.py
```

**View previous snapshots:**
```bash
# List snapshots for current cluster
ls -ltr output/your-cluster.com/snapshots/

# List all clusters
ls -d output/*/
```

Each snapshot is a complete point-in-time capture of your cluster state. Snapshots are organized by cluster automatically!

---

## 🐛 Troubleshooting

### Problem: "oc: command not found"

**Solution:** Install the OpenShift CLI
```bash
# macOS
brew install openshift-cli

# Linux - download from:
# https://mirror.openshift.com/pub/openshift-v4/clients/ocp/
```

### Problem: "Error: You must be logged in to the server"

**Solution:** Login to your cluster
```bash
oc login --token=... --server=...
```

### Problem: "No CP4I namespaces found"

**Possible causes:**
1. CP4I not installed on this cluster
2. Namespaces don't have CP4I labels
3. You don't have permission to see them

**Check:**
```bash
oc get namespaces --show-labels | grep -i cp4i
oc get namespaces | grep -i integration
```

**Fix:** Edit the namespace detection in `src/collector_ocp.py` or manually specify namespaces.

### Problem: "Warning: Could not initialize resource categorizer"

**Solution:** This is usually fine - the basic dashboard still works. The error means:
- `resource_categories.yaml` is missing or malformed
- Run: `python3 -c "import yaml; yaml.safe_load(open('resource_categories.yaml'))"`

### Problem: "No changes detected" (always shows 0 changes)

**This is normal!** Change detection only works after you have 2+ snapshots:
1. First run: Creates baseline snapshot (no changes shown)
2. Second run: Compares to first run (shows changes)
3. Third run: Compares to second run (shows new changes)

**To see changes:**
```bash
# Run once
python3 chief_console.py

# Make some changes to your cluster (deploy something, restart a pod)

# Run again
python3 chief_console.py
```

### Problem: Dashboard shows empty sections

**Possible causes:**
1. No CP4I installed → Empty CP4I section (expected)
2. No Event Streams → Empty topics section (expected)
3. No custom apps → Empty workloads section (expected)

**This is fine!** The dashboard gracefully degrades. You'll only see sections with data.

---

## 🔒 Security & Permissions

### What Permissions Does This Need?

The mission console is **read-only**. It never modifies your cluster.

**Minimum required:**
```bash
# Cluster-level read access (preferred)
oc adm policy add-cluster-role-to-user cluster-reader <your-user>

# OR namespace-level read access
oc adm policy add-role-to-user view <your-user> -n integration-platform
oc adm policy add-role-to-user view <your-user> -n tools
```

### Is My Data Shared?

**No.** Everything runs locally:
- No data sent to external services
- No telemetry or analytics
- Snapshots stored on your local machine only

### Can I Share Snapshots?

**Yes, but be careful:**
- Snapshots contain cluster configuration details
- May include sensitive information (pod names, routes, etc.)
- Review before sharing outside your team

---

## 📊 Understanding the Dashboard

### Wave 1: Executive Summary
**What it shows:** Cluster health, namespace count, pod status
**Use for:** Quick health check, executive reporting

### Wave 2: CP4I Capabilities
**What it shows:** Installed CP4I components (Event Streams, App Connect, etc.)
**Use for:** Understanding what's deployed

### Wave 4: Demo Artifacts
**What it shows:** Your custom applications, organized hierarchically
**Use for:** Demo starting point, understanding data flows

### Wave 5: Licensing Cost Map 💰
**What it shows:** VPC consumption, licensed vs free components
**Use for:** Cost optimization, license management

### Wave 6: Workload Health 🎯
**What it shows:** ONLY business workloads (filters out infrastructure)
**Use for:** Focusing on what matters, workload health

### Wave 7: Criticality Tiers 🚦
**What it shows:** Critical vs Important vs Optional components
**Use for:** Outage prioritization, cost cutting, DR planning

### Wave 8: Resource Utilization 📊
**What it shows:** CPU/Memory consumption, top consumers
**Use for:** Right-sizing, capacity planning

### Wave 3: Infrastructure
**What it shows:** Nodes, operators, detailed pod lists
**Use for:** Deep troubleshooting, platform health

---

## 🎓 Advanced Usage

### Excel Export for Customer Collaboration 📊

The mission console automatically generates an Excel spreadsheet with **5 sheets** perfect for licensing discussions:

**What's Included:**
1. **Executive Summary** - Cluster overview, VPC total, workload counts
2. **Licensing Analysis** - CP4I components grouped by capability with VPC breakdown
3. **Infrastructure Sizing** - Node capacity, resource allocation percentages
4. **Workload Inventory** - Business workloads only (filters out infrastructure)
5. **Detailed Pod List** - Complete inventory with color-coded licensing categories

**Location:**
```bash
# Excel files are in your cluster directory
ls -lh output/your-cluster.com/chief-console-*.xlsx

# Latest Excel file
ls -t output/your-cluster.com/chief-console-*.xlsx | head -1
```

**Share with Customers:**
```bash
# Email the latest Excel file to customers for licensing discussions
open output/your-cluster.com/chief-console-20260104-182322.xlsx
```

**Excel Features:**
- ✅ Professional formatting with color-coded licensing (red = CP4I licensed)
- ✅ Sortable/filterable tables
- ✅ VPC contribution highlighted
- ✅ Timestamp in filename for version control
- ✅ Safe to share (no credentials, just resource info)

### Multi-Cluster Workflow

Switch between clusters seamlessly:

```bash
# Work with Cluster A
oc login cluster-a.techzone.ibm.com
python3 chief_console.py
# ✓ Creates: output/cluster-a.techzone.ibm.com/

# Switch to Cluster B
oc login cluster-b.techzone.ibm.com
python3 chief_console.py
# ✓ Creates: output/cluster-b.techzone.ibm.com/

# Both dashboards preserved! Compare side-by-side.
open output/cluster-a.techzone.ibm.com/dashboard.html
open output/cluster-b.techzone.ibm.com/dashboard.html
```

### Compare Two Snapshots

```bash
# View all snapshots for current cluster
ls output/your-cluster.com/snapshots/

# Compare specific snapshots manually
python3 -c "
import json
with open('output/your-cluster.com/snapshots/snapshot-20260101-120000.json') as f:
    snap1 = json.load(f)
with open('output/your-cluster.com/snapshots/snapshot-20260101-130000.json') as f:
    snap2 = json.load(f)
# Your comparison logic here
"
```

### Export Snapshot Data

```bash
# Pretty-print a snapshot
cat output/your-cluster.com/snapshots/snapshot-YYYYMMDD-HHMMSS.json | python3 -m json.tool

# Extract specific data (e.g., all pod names)
cat output/your-cluster.com/snapshots/snapshot-YYYYMMDD-HHMMSS.json | \
  python3 -c "import sys, json; pods = json.load(sys.stdin)['pods']; print('\n'.join(p['name'] for p in pods))"
```

### Customize HTML Styling

The dashboard is a single self-contained HTML file. Edit `src/html_renderer.py` to customize:
- Colors (search for `#0f62fe` for IBM blue)
- Layout (modify the CSS in `_render_styles()`)
- Content (modify the wave rendering methods)

---

## 📞 Getting Help

### Common Questions

**Q: How often should I run this?**
A: Depends on your needs:
- **Before demos:** Run once to get fresh dashboard
- **Change tracking:** Run daily or weekly
- **Continuous monitoring:** Run hourly via cron

**Q: Can I run this in a container?**
A: Yes! Create a Dockerfile:
```dockerfile
FROM python:3.9-slim
RUN apt-get update && apt-get install -y curl
RUN curl -L https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux.tar.gz | tar -xz -C /usr/local/bin
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
CMD ["python3", "chief_console.py"]
```

**Q: Can I customize the waves?**
A: Absolutely! Edit `src/html_renderer.py`. Each wave is a separate method (e.g., `_render_wave5_licensing()`).

**Q: What if my cluster has no CP4I?**
A: The dashboard still works! You'll see:
- Cluster infrastructure (nodes, namespaces)
- All pods and operators
- Resource utilization
- Criticality tiers

The CP4I-specific sections will be empty (which is expected).

---

## 🎁 Sharing with Others

### Package for Distribution

```bash
# Create a clean copy (without snapshots/output)
cd ~/Documents
cp -r chief-console chief-console-clean
cd chief-console-clean
rm -rf output/
rm -rf .git  # Optional: remove git history

# Create a zip
cd ..
zip -r chief-console.zip chief-console-clean

# Share chief-console.zip + this README
```

### What to Include

When sharing with colleagues, include:
1. ✅ This `GETTING_STARTED.md` file
2. ✅ The entire `chief-console/` directory
3. ✅ A sample `demo_metadata.yaml` (if you've customized it)
4. ❌ **DO NOT** include `output/` folder (contains your cluster data!)

---

## 📚 Additional Resources

### Files You Can Customize
- `demo_metadata.yaml` - Display names and descriptions
- `resource_categories.yaml` - Categorization rules

### Files You Shouldn't Modify (Unless You Know What You're Doing)
- `src/*.py` - Python source code
- `chief_console.py` - Main entry point

### Documentation
- `ENVIRONMENT_TAXONOMY.md` - Understand your environment
- `NAMING_CONVENTIONS.md` - Naming standards for demo resources
- `LINKEDIN_POSTS.md` - Example marketing content
- `EMAIL_TEMPLATES_SUPPORT_CUSTOMER_DAY.md` - Email templates

---

## 🚀 You're Ready!

Quick checklist:
- [ ] Python 3.8+ installed
- [ ] `oc` CLI installed
- [ ] Logged into OpenShift cluster
- [ ] Ran `pip3 install -r requirements.txt`
- [ ] Ran `python3 chief_console.py`
- [ ] Dashboard opened in browser

**Having issues?** See the Troubleshooting section above.

**Want to customize?** Start with `demo_metadata.yaml` to add display names for your resources.

**Questions?** Contact the person who shared this with you.

---

## 🎉 What's Next?

Now that you have the dashboard running:

1. **Customize display names** - Edit `demo_metadata.yaml` to add business context
2. **Run it regularly** - Set up a cron job to track changes over time
3. **Share with your team** - Export and share the HTML dashboard
4. **Use for demos** - Wave 4 (Demo Artifacts) is designed as a demo starting point
5. **Optimize costs** - Use Wave 5 (Licensing) to understand VPC consumption

**Happy monitoring!** 🎊
