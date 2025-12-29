#!/usr/bin/env python3
"""
CP4I Mission Console - Main Entry Point

Collects cluster data and generates dashboard in one command.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from collector_ocp import OCPCollector
from html_renderer import render_dashboard
from diff_engine import compare_snapshots, find_latest_snapshots
import json


def main():
    """Run collection and render dashboard"""
    print("=" * 70)
    print("CP4I MISSION CONSOLE")
    print("=" * 70)
    print()

    # Step 1: Collect data
    print("Step 1: Collecting cluster data...")
    print("-" * 70)
    collector = OCPCollector()
    snapshot = collector.collect_all()

    # Save snapshot
    output_dir = Path("output/snapshots")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    snapshot_file = output_dir / f"snapshot-{timestamp}.json"

    with open(snapshot_file, 'w') as f:
        json.dump(snapshot, f, indent=2)

    print(f"\nSnapshot saved: {snapshot_file}")
    print()

    # Step 2: Detect changes
    print("Step 2: Detecting changes...")
    print("-" * 70)
    diff_data = None

    # Find previous snapshot
    previous_snapshots = find_latest_snapshots(count=2)

    if len(previous_snapshots) >= 2:
        # We have a previous snapshot to compare with
        previous_snapshot = previous_snapshots[1]  # Second most recent (before current)
        print(f"Comparing with: {Path(previous_snapshot).name}")

        try:
            diff_data = compare_snapshots(previous_snapshot, str(snapshot_file))

            # Print summary
            if diff_data:
                changes = diff_data.get('changes', {})
                critical_count = len(changes.get('critical', []))
                important_count = len(changes.get('important', []))

                if critical_count > 0:
                    print(f"  🔴 {critical_count} critical change(s)")
                if important_count > 0:
                    print(f"  🟡 {important_count} important change(s)")
                if critical_count == 0 and important_count == 0:
                    print("  ✅ No significant changes detected")
        except Exception as e:
            print(f"  ⚠️  Change detection failed: {e}")
    else:
        print("  ℹ️  No previous snapshot found (first run)")

    print()

    # Step 3: Render dashboard
    print("Step 3: Rendering dashboard...")
    print("-" * 70)
    dashboard_file = render_dashboard(str(snapshot_file), diff=diff_data)

    print()
    print("=" * 70)
    print("MISSION CONSOLE READY")
    print("=" * 70)
    print()
    print(f"Dashboard: {dashboard_file}")
    print(f"Snapshot:  {snapshot_file}")
    print()
    print("Open dashboard:")
    print(f"  file://{Path(dashboard_file).absolute()}")
    print()
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
