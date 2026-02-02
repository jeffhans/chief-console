#!/bin/bash
#
# Quick Start: Watch CP4I Installation
#
# This script starts automated monitoring with sensible defaults.
# Perfect for watching CP4I install in real-time.
#

echo "Starting CP4I Chief Console Monitoring..."
echo ""
echo "This will:"
echo "  - Run collection every 2 minutes"
echo "  - Auto-open dashboard when changes detected"
echo "  - Show progress in terminal"
echo ""
echo "Press Ctrl+C to stop anytime"
echo ""
echo "Starting in 3 seconds..."
sleep 3

python3 monitor.py --interval 120 --auto-open
