#!/bin/bash
# CP4I Mission Console - Setup Script
# This script verifies prerequisites and sets up the environment

set -e  # Exit on error

echo "======================================================================="
echo "CP4I Mission Console - Setup Verification"
echo "======================================================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track if any errors occurred
ERRORS=0

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
        ERRORS=$((ERRORS + 1))
    fi
}

echo "Checking prerequisites..."
echo ""

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        print_status 0 "Python 3.8+ found ($PYTHON_VERSION)"
    else
        print_status 1 "Python 3.8+ required (found $PYTHON_VERSION)"
    fi
else
    print_status 1 "Python 3 not found"
fi

# Check oc CLI
if command_exists oc; then
    OC_VERSION=$(oc version --client 2>&1 | grep -i client | head -1)
    print_status 0 "OpenShift CLI (oc) found"
    echo "   $OC_VERSION"
else
    print_status 1 "OpenShift CLI (oc) not found"
    echo "   Install: https://mirror.openshift.com/pub/openshift-v4/clients/ocp/"
fi

# Check if logged into OpenShift
if command_exists oc; then
    if oc whoami >/dev/null 2>&1; then
        USER=$(oc whoami 2>&1)
        SERVER=$(oc whoami --show-server 2>&1)
        print_status 0 "Logged into OpenShift as: $USER"
        echo "   Server: $SERVER"
    else
        print_status 1 "Not logged into OpenShift cluster"
        echo "   Run: oc login --token=... --server=..."
    fi
fi

# Check git (optional)
if command_exists git; then
    print_status 0 "Git found (optional)"
else
    echo -e "${YELLOW}⚠${NC} Git not found (optional, only needed for cloning repo)"
fi

echo ""
echo "Checking Python dependencies..."
echo ""

# Check if pip is available
if command_exists pip3; then
    print_status 0 "pip3 found"

    # Try to import required modules
    if python3 -c "import yaml" 2>/dev/null; then
        print_status 0 "pyyaml installed"
    else
        print_status 1 "pyyaml not installed"
        echo "   Run: pip3 install -r requirements.txt"
    fi

    if python3 -c "import openpyxl" 2>/dev/null; then
        print_status 0 "openpyxl installed (for Excel export)"
    else
        print_status 1 "openpyxl not installed"
        echo "   Run: pip3 install -r requirements.txt"
        echo "   Note: Excel export will be skipped without openpyxl"
    fi
else
    print_status 1 "pip3 not found"
fi

echo ""
echo "Checking file structure..."
echo ""

# Check required files
FILES=(
    "chief_console.py"
    "monitor.py"
    "src/collector_ocp.py"
    "src/html_renderer.py"
    "src/resource_categorizer.py"
    "src/excel_exporter.py"
    "src/cluster_utils.py"
    "demo_metadata.yaml"
    "resource_categories.yaml"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        print_status 0 "$file"
    else
        print_status 1 "$file missing"
    fi
done

echo ""
echo "======================================================================="

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! You're ready to run the mission console.${NC}"
    echo ""
    echo "Next step:"
    echo "  python3 chief_console.py"
    echo ""
    exit 0
else
    echo -e "${RED}✗ $ERRORS issue(s) found. Please fix the errors above.${NC}"
    echo ""
    echo "See GETTING_STARTED.md for detailed setup instructions."
    echo ""
    exit 1
fi
