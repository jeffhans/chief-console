#!/usr/bin/env python3
"""
Test script for enhanced 'What Changed' visualization
Generates a dashboard with the latest snapshot and diff data
"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from html_renderer import render_dashboard
from diff_engine import compare_snapshots, find_latest_snapshots


def main():
    print("=" * 70)
    print("TESTING ENHANCED 'WHAT CHANGED' VISUALIZATION")
    print("=" * 70)
    print()

    # Find latest snapshots
    snapshots = find_latest_snapshots(count=2)

    if len(snapshots) < 2:
        print("❌ Need at least 2 snapshots to test. Please run mission_console.py first.")
        return 1

    current = snapshots[0]
    previous = snapshots[1]

    print(f"Current:  {Path(current).name}")
    print(f"Previous: {Path(previous).name}")
    print()

    # Generate diff
    print("Generating diff...")
    diff_data = compare_snapshots(previous, current)

    changes = diff_data.get('changes', {})
    print(f"  Critical:      {len(changes.get('critical', []))}")
    print(f"  Important:     {len(changes.get('important', []))}")
    print(f"  Informational: {len(changes.get('informational', []))}")
    print()

    # Render dashboard with diff
    print("Rendering enhanced dashboard...")
    output_file = render_dashboard(current, diff=diff_data)

    print()
    print("=" * 70)
    print("✅ ENHANCED DASHBOARD GENERATED")
    print("=" * 70)
    print()
    print(f"Dashboard: {output_file}")
    print()
    print("Open in browser:")
    print(f"  file://{Path(output_file).absolute()}")
    print()
    print("Features to check:")
    print("  • Hierarchical change organization (by namespace)")
    print("  • Deep links to OpenShift Console ([🔗 View] links)")
    print("  • Critical changes grouped by type")
    print("  • Important changes grouped by namespace → type")
    print("  • Links to pods, operators, topics, routes, etc.")
    print()
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
