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

    # Step 2: Render dashboard
    print("Step 2: Rendering dashboard...")
    print("-" * 70)
    dashboard_file = render_dashboard(str(snapshot_file))

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
