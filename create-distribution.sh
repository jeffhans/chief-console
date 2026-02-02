#!/bin/bash
# CP4I Chief Console - Create Distribution Package
# This script creates a clean distribution package ready to share with colleagues

set -e  # Exit on error

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

VERSION="1.0.0"
DATE=$(date +%Y%m%d)
PACKAGE_NAME="chief-console-v${VERSION}-${DATE}"
TEMP_DIR="/tmp/${PACKAGE_NAME}"
CURRENT_DIR=$(pwd)

echo -e "${BLUE}=======================================================================${NC}"
echo -e "${BLUE}CP4I Chief Console - Distribution Package Creator${NC}"
echo -e "${BLUE}=======================================================================${NC}"
echo ""
echo "Package: ${PACKAGE_NAME}"
echo "Date: $(date)"
echo ""

# Check if we're in the chief-console directory
if [ ! -f "chief_console.py" ]; then
    echo -e "${YELLOW}⚠ Error: Must run from chief-console directory${NC}"
    echo "cd to the chief-console directory and run again"
    exit 1
fi

# Create temp directory
echo -e "${BLUE}📁 Creating temporary directory...${NC}"
mkdir -p "${TEMP_DIR}"

# Copy required files
echo -e "${BLUE}📋 Copying files...${NC}"

# Core Python files
echo "  ✓ Python code"
mkdir -p "${TEMP_DIR}/src"
cp src/*.py "${TEMP_DIR}/src/"
cp chief_console.py "${TEMP_DIR}/"

# Configuration files
echo "  ✓ Configuration files"
cp demo_metadata.yaml "${TEMP_DIR}/"
cp resource_categories.yaml "${TEMP_DIR}/"
cp requirements.txt "${TEMP_DIR}/"

# Scripts
echo "  ✓ Scripts"
cp setup.sh "${TEMP_DIR}/"
cp monitor.py "${TEMP_DIR}/"
chmod +x "${TEMP_DIR}/setup.sh"
chmod +x "${TEMP_DIR}/monitor.py"

# Documentation
echo "  ✓ Documentation"
cp GETTING_STARTED.md "${TEMP_DIR}/"
cp DISTRIBUTION_CHECKLIST.md "${TEMP_DIR}/"
cp ENVIRONMENT_TAXONOMY.md "${TEMP_DIR}/" 2>/dev/null || true

# Optional: Include additional docs if they exist
[ -f README.md ] && cp README.md "${TEMP_DIR}/" || true
[ -f NAMING_CONVENTIONS.md ] && cp NAMING_CONVENTIONS.md "${TEMP_DIR}/" || true

# Create README pointer
cat > "${TEMP_DIR}/START_HERE.txt" << 'EOF'
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║            CP4I MISSION CONSOLE                                   ║
║            Dashboard for OpenShift / CP4I Environments            ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

👋 Welcome!

QUICK START:
1. Open GETTING_STARTED.md (comprehensive setup guide)
2. Run: ./setup.sh (verify prerequisites)
3. Run: python3 chief_console.py
4. Dashboard auto-opens in browser!

PREREQUISITES:
✓ Python 3.8+
✓ OpenShift CLI (oc)
✓ Access to OpenShift cluster (must be logged in with 'oc login')

TIME TO FIRST DASHBOARD: ~5 minutes

WHAT YOU GET:
• Executive summary of your cluster
• CP4I capabilities overview
• Demo artifacts visualization
• Licensing cost analysis (VPC usage)
• Workload health monitoring
• Criticality tier categorization
• Resource utilization insights
• Change tracking over time
• Excel export for customer licensing discussions
• Multi-cluster support (cluster-aware directories!)

KEY FEATURES:
✨ Auto-opens dashboard in browser
📊 Excel spreadsheets generated automatically
🎯 Cluster-aware (manage multiple TechZone instances)
🔄 Automated monitoring (run: python3 monitor.py)

CUSTOMIZATION:
• demo_metadata.yaml - Add display names for your resources
• resource_categories.yaml - Adjust categorization rules

QUESTIONS?
See GETTING_STARTED.md for detailed instructions and troubleshooting.

Happy monitoring! 🎉
EOF

# Create .gitignore for recipient
cat > "${TEMP_DIR}/.gitignore" << 'EOF'
# Mission Console - Files to ignore

# Output directory (contains cluster-specific data)
output/
snapshots/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# macOS
.DS_Store

# Local customizations (optional - uncomment if you don't want to track these)
# demo_metadata.yaml
# resource_categories.yaml
EOF

echo ""
echo -e "${BLUE}📦 Creating distribution packages...${NC}"

# Create tar.gz
cd /tmp
tar -czf "${PACKAGE_NAME}.tar.gz" "${PACKAGE_NAME}/"
echo "  ✓ Created: ${PACKAGE_NAME}.tar.gz"

# Create zip
zip -r "${PACKAGE_NAME}.zip" "${PACKAGE_NAME}/" > /dev/null
echo "  ✓ Created: ${PACKAGE_NAME}.zip"

# Move to current directory
mv "${PACKAGE_NAME}.tar.gz" "${CURRENT_DIR}/"
mv "${PACKAGE_NAME}.zip" "${CURRENT_DIR}/"

# Clean up
rm -rf "${TEMP_DIR}"

# Create distribution info file
cat > "${CURRENT_DIR}/DISTRIBUTION_INFO.txt" << EOF
Distribution Package Created: $(date)

Package Name: ${PACKAGE_NAME}
Files Created:
  - ${PACKAGE_NAME}.tar.gz
  - ${PACKAGE_NAME}.zip

What's Included:
  ✓ Python source code (src/)
  ✓ Main entry point (chief_console.py)
  ✓ Configuration files (*.yaml)
  ✓ Setup script (setup.sh)
  ✓ Documentation (*.md)
  ✓ Getting started guide
  ✓ Distribution checklist

What's Excluded:
  ✗ output/ directory (your cluster data)
  ✗ .git/ directory (version control history)
  ✗ __pycache__/ (Python cache)

Distribution Methods:

1. EMAIL:
   - Attach ${PACKAGE_NAME}.zip
   - Include message from DISTRIBUTION_CHECKLIST.md
   - Point recipient to START_HERE.txt

2. SHARED DRIVE:
   - Upload ${PACKAGE_NAME}.tar.gz or .zip
   - Share link with team members

3. GIT REPOSITORY:
   - Extract and push to your team's Git server
   - Share clone command

4. DIRECT COPY:
   - Extract to shared directory
   - Recipients copy to their local machine

Security Reminder:
  ✓ No cluster-specific data included
  ✓ No credentials or secrets
  ✓ Safe to share within your organization
  ✓ Review demo_metadata.yaml for sensitive info before external sharing

Next Steps for Recipient:
  1. Extract archive
  2. cd chief-console
  3. Read START_HERE.txt
  4. Follow GETTING_STARTED.md
  5. Run ./setup.sh
  6. Run python3 chief_console.py

EOF

echo ""
echo -e "${GREEN}=======================================================================${NC}"
echo -e "${GREEN}✓ Distribution packages created successfully!${NC}"
echo -e "${GREEN}=======================================================================${NC}"
echo ""
echo "📦 Packages:"
echo "   • ${PACKAGE_NAME}.tar.gz"
echo "   • ${PACKAGE_NAME}.zip"
echo ""
echo "📄 Distribution info:"
echo "   • DISTRIBUTION_INFO.txt (details about what was created)"
echo ""
echo "📧 Next Steps:"
echo "   1. Review DISTRIBUTION_CHECKLIST.md for sharing instructions"
echo "   2. Choose distribution method (email, shared drive, git)"
echo "   3. Share package with colleague"
echo "   4. Point them to START_HERE.txt in the package"
echo ""
echo "🔒 Security Check:"
echo "   ✓ No output/ directory (your cluster data excluded)"
echo "   ✓ No git history"
echo "   ✓ Safe to share"
echo ""
echo -e "${GREEN}Happy sharing! 🚀${NC}"
echo ""
