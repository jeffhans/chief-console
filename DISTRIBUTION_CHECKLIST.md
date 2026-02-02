# Mission Console - Distribution Checklist

Use this checklist when packaging the Mission Console for a colleague or new TechZone instance.

---

## 📦 What to Package

### ✅ Required Files (Always Include)

```
mission-console/
├── mission_console.py              ← Main entry point
├── monitor.py                      ← Automated monitoring script
├── requirements.txt                ← Python dependencies (pyyaml, openpyxl)
├── setup.sh                        ← Setup verification script
├── GETTING_STARTED.md             ← Start here!
├── src/
│   ├── collector_ocp.py           ← OpenShift data collector
│   ├── collector_kafka.py         ← Kafka/Event Streams collector
│   ├── diff_engine.py             ← Change detection
│   ├── html_renderer.py           ← Dashboard generator
│   ├── resource_categorizer.py    ← Resource categorization
│   ├── excel_exporter.py          ← Excel spreadsheet generator
│   └── cluster_utils.py           ← Cluster detection utilities
├── demo_metadata.yaml              ← Display names (customize)
└── resource_categories.yaml        ← Categorization rules (customize)
```

### ⚠️ Optional Files (Include if Customized)

```
├── ENVIRONMENT_TAXONOMY.md         ← Reference guide
├── NAMING_CONVENTIONS.md           ← Naming standards
├── LINKEDIN_POSTS.md               ← Marketing content
└── EMAIL_TEMPLATES_*.md            ← Email templates
```

### ❌ Never Include

```
├── output/                         ← Contains YOUR cluster data!
│   ├── your-cluster.com/          ← Cluster-specific directories
│   │   ├── dashboard.html
│   │   ├── mission-console-*.xlsx
│   │   └── snapshots/
│   └── another-cluster.com/
├── .git/                           ← Git history (optional to exclude)
├── __pycache__/                    ← Python cache
├── src/__pycache__/                ← Python cache in src
└── *.pyc                           ← Compiled Python
```

**⚠️ IMPORTANT:** The `output/` directory contains cluster-specific data including:
- Dashboards with your cluster configuration
- Excel files with licensing/sizing details
- Snapshots with complete cluster state
- **Remove entire `output/` directory before distributing!**

---

## 🚀 Quick Distribution Methods

### Method 1: Zip File (Recommended for Email/Sharing)

```bash
# From mission-console directory
cd ..

# Create clean copy
cp -r mission-console mission-console-distribution
cd mission-console-distribution

# Remove output and git
rm -rf output/
rm -rf .git
rm -rf src/__pycache__

# Create zip
cd ..
zip -r mission-console.zip mission-console-distribution/

# Clean up
rm -rf mission-console-distribution/

echo "✓ Created: mission-console.zip"
echo "Share this file + GETTING_STARTED.md"
```

### Method 2: Git Repository (Recommended for Teams)

```bash
# Initialize git repo
git init
git add .
git commit -m "Initial commit: CP4I Mission Console"

# Push to your internal Git server
git remote add origin <your-git-server-url>
git push -u origin main

# Share the clone command:
# git clone <your-git-server-url>
```

### Method 3: Shared Drive (Simplest)

1. Copy entire `mission-console/` folder to shared drive
2. Delete the `output/` folder first
3. Share the location with colleagues
4. They copy to their local machine

---

## 📋 Pre-Distribution Checklist

Before sharing, verify:

- [ ] Remove `output/` directory (contains your cluster data!)
- [ ] Remove `.git/` if you don't want to share git history
- [ ] Remove `__pycache__/` folders
- [ ] Verify `demo_metadata.yaml` doesn't contain sensitive info
- [ ] Update `GETTING_STARTED.md` with your team's contact info
- [ ] Test on a clean machine (if possible)
- [ ] Include a README or point to `GETTING_STARTED.md`

---

## 👥 Instructions for Recipient

Include these instructions in your email/message:

```
Hey [Colleague],

I'm sharing the CP4I Mission Console - a dashboard for visualizing
your OpenShift/CP4I environment.

Getting Started:
1. Unzip mission-console.zip
2. cd mission-console
3. Read GETTING_STARTED.md (comprehensive guide)
4. Run: ./setup.sh (verifies prerequisites)
5. Run: python3 mission_console.py

Prerequisites:
- Python 3.8+
- OpenShift CLI (oc)
- Access to an OpenShift cluster (must be logged in)

Time to first dashboard: ~5 minutes

Questions? Ping me!
```

---

## 🔒 Security Considerations

### Before Distribution

1. **Review `demo_metadata.yaml`**
   - Remove any sensitive descriptions
   - Remove internal team names if external sharing
   - Remove any IP addresses or URLs

2. **Review snapshots**
   - Ensure `output/` folder is deleted
   - Snapshots contain cluster configuration
   - Don't accidentally share your cluster state

3. **Review configuration**
   - `resource_categories.yaml` is safe to share
   - Contains only categorization rules, no cluster data

### For Recipients

Remind them:
- This tool is **read-only** (never modifies cluster)
- Snapshots contain cluster configuration (don't share publicly)
- Dashboard HTML files can be shared with team members

---

## 🧪 Test on New TechZone Instance

Before distributing, test on a fresh TechZone instance:

### Setup Test Instance

1. Provision new TechZone cluster
2. SSH or open terminal
3. Install prerequisites:
   ```bash
   # Python (if not installed)
   python3 --version

   # OpenShift CLI
   curl -L https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux.tar.gz | tar -xz
   sudo mv oc kubectl /usr/local/bin/
   ```

4. Copy mission console:
   ```bash
   # Via scp, wget, or copy-paste
   scp -r mission-console user@techzone-instance:~/
   ```

5. Run setup:
   ```bash
   cd mission-console
   ./setup.sh
   ```

6. Login to cluster:
   ```bash
   oc login --token=... --server=...
   ```

7. Run console:
   ```bash
   python3 mission_console.py
   ```

8. Verify output:
   ```bash
   ls output/dashboard.html
   ```

### Common Issues on New Instances

**Issue: Python not found**
```bash
# Install Python 3
yum install python3  # RHEL/CentOS
apt-get install python3  # Ubuntu/Debian
```

**Issue: pip not found**
```bash
python3 -m ensurepip
# OR
curl https://bootstrap.pypa.io/get-pip.py | python3
```

**Issue: No display for opening HTML**
```bash
# Copy dashboard to local machine
scp user@techzone-instance:~/mission-console/output/dashboard.html ./
open dashboard.html
```

---

## 📚 What to Include in Distribution Email

### Subject Line
```
CP4I Mission Console - Dashboard for Your TechZone Instance
```

### Email Template

```
Hi [Name],

I'm sharing the CP4I Mission Console - a tool I've been using to
visualize and monitor our Cloud Pak for Integration environments.

What It Does:
• Executive dashboard of your OpenShift/CP4I cluster
• Licensing cost analysis (VPC consumption with Excel export!)
• Workload health monitoring
• Change tracking over time
• Resource utilization insights
• Multi-cluster support (automatically organizes by cluster)
• Automated monitoring with configurable intervals

Time to Value: ~5 minutes from download to dashboard

Key Features:
✨ Auto-opens dashboard in browser
📊 Generates Excel spreadsheets for customer licensing discussions
🎯 Cluster-aware (manage multiple TechZone instances)
🔄 Automated monitoring script included

Getting Started:
1. Download the attached mission-console.zip
2. Unzip and read GETTING_STARTED.md
3. Run: python3 mission_console.py
4. Open: output/dashboard.html

Prerequisites:
✓ Python 3.8+
✓ OpenShift CLI (oc)
✓ Access to an OpenShift cluster

Documentation:
• GETTING_STARTED.md - Step-by-step setup guide
• ENVIRONMENT_TAXONOMY.md - Understanding your environment
• setup.sh - Automated prerequisite checker

Customization:
• demo_metadata.yaml - Add display names for your resources
• resource_categories.yaml - Adjust categorization rules

Questions or issues? Let me know!

Cheers,
[Your Name]
```

---

## 🎁 Bonus: Create Installation Package

For frequent distribution, create a setup package:

```bash
#!/bin/bash
# create-distribution.sh

VERSION="1.0.0"
DATE=$(date +%Y%m%d)
PACKAGE="mission-console-v${VERSION}-${DATE}"

echo "Creating distribution package: ${PACKAGE}"

# Create temp directory
mkdir -p /tmp/${PACKAGE}

# Copy files
cp -r src /tmp/${PACKAGE}/
cp mission_console.py /tmp/${PACKAGE}/
cp requirements.txt /tmp/${PACKAGE}/
cp setup.sh /tmp/${PACKAGE}/
cp *.yaml /tmp/${PACKAGE}/
cp GETTING_STARTED.md /tmp/${PACKAGE}/
cp README.md /tmp/${PACKAGE}/ 2>/dev/null || true

# Create archive
cd /tmp
tar -czf ${PACKAGE}.tar.gz ${PACKAGE}/
zip -r ${PACKAGE}.zip ${PACKAGE}/

# Move to current directory
mv ${PACKAGE}.tar.gz ~/Downloads/
mv ${PACKAGE}.zip ~/Downloads/

# Clean up
rm -rf /tmp/${PACKAGE}

echo "✓ Created distribution packages:"
echo "  ~/Downloads/${PACKAGE}.tar.gz"
echo "  ~/Downloads/${PACKAGE}.zip"
```

Make it executable:
```bash
chmod +x create-distribution.sh
```

Run it:
```bash
./create-distribution.sh
```

---

## ✅ Final Checklist

Before sending to colleague:

- [ ] Tested on clean TechZone instance
- [ ] All files included
- [ ] No sensitive data in files
- [ ] `output/` folder removed
- [ ] `GETTING_STARTED.md` reviewed
- [ ] Contact information updated
- [ ] Prerequisites documented
- [ ] Distribution package created
- [ ] Email drafted with clear instructions
- [ ] Confirmed recipient has cluster access

---

## 🎉 You're Ready to Share!

Your colleague should be able to:
1. Download/clone the mission console
2. Run `./setup.sh` to verify prerequisites
3. Run `python3 mission_console.py`
4. Get a working dashboard in ~5 minutes

Good luck! 🚀
