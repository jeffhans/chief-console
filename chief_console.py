#!/usr/bin/env python3
"""
CP4I Chief Console - Main Entry Point

Collects cluster data and generates dashboard in one command.
"""

import sys
from pathlib import Path
from datetime import datetime
import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from collector_ocp import OCPCollector
from html_renderer import render_dashboard
from diff_engine import compare_snapshots, find_latest_snapshots
from resource_categorizer import ResourceCategorizer
from excel_exporter import ExcelExporter
from cluster_utils import get_cluster_info, format_cluster_name
import json


def main():
    """Run collection and render dashboard"""
    print("=" * 70)
    print("CP4I CHIEF CONSOLE")
    print("=" * 70)
    print()

    # Detect current cluster
    cluster_info = get_cluster_info()

    if not cluster_info['logged_in']:
        print("❌ ERROR: Not logged into OpenShift cluster")
        print("   Run: oc login --server=... --token=...")
        print()
        return 1

    # Load config (aliases live here)
    config = {}
    config_path = Path(__file__).parent / "config.yaml"
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️  Could not read config.yaml: {e}")

    if not isinstance(config, dict):
        config = {}

    # Merge local config overrides (gitignored)
    local_config_path = Path(__file__).parent / "config.local.yaml"
    if local_config_path.exists():
        try:
            with open(local_config_path, "r") as f:
                local_config = yaml.safe_load(f) or {}
                if isinstance(local_config, dict):
                    # Deep merge cluster_aliases
                    if "cluster_aliases" in local_config:
                        if "cluster_aliases" not in config:
                            config["cluster_aliases"] = {}
                        if config["cluster_aliases"] is None:
                            config["cluster_aliases"] = {}
                        config["cluster_aliases"].update(local_config["cluster_aliases"])
                    # Merge other top-level keys
                    for key, value in local_config.items():
                        if key != "cluster_aliases":
                            config[key] = value
        except Exception as e:
            print(f"⚠️  Could not read config.local.yaml: {e}")

    cluster_id = cluster_info['cluster_id']
    aliases = config.get("cluster_aliases", {}) or {}
    alias_entry = aliases.get(cluster_id)

    cluster_alias_name = None
    cluster_alias_id = None
    if isinstance(alias_entry, dict):
        cluster_alias_name = alias_entry.get("name")
        cluster_alias_id = alias_entry.get("id")
    elif isinstance(alias_entry, str):
        cluster_alias_name = alias_entry

    cluster_display = cluster_alias_name or "CP4I Chief Console"

    print(f"📍 Cluster: {cluster_display}")
    print(f"   Server: {cluster_info['server']}")
    print(f"   User: {cluster_info['user']}")
    print()

    # Create cluster-specific output directory
    cluster_output_dir = Path("output") / cluster_id
    cluster_output_dir.mkdir(parents=True, exist_ok=True)

    print(f"💾 Output directory: output/{cluster_id}/")
    print()

    # Step 1: Collect data
    print("Step 1: Collecting cluster data...")
    print("-" * 70)
    collector = OCPCollector()
    snapshot = collector.collect_all()

    # Enrich snapshot with alias/display info for downstream consumers
    snapshot.setdefault('metadata', {})
    snapshot['metadata']['cluster_id'] = cluster_id
    snapshot['metadata']['cluster_display'] = cluster_display
    if cluster_alias_name:
        snapshot['metadata']['cluster_alias'] = cluster_alias_name
    if cluster_alias_id:
        snapshot['metadata']['cluster_alias_id'] = cluster_alias_id

    snapshot.setdefault('cluster', {})
    snapshot['cluster']['id'] = cluster_id
    snapshot['cluster']['display_name'] = cluster_display
    if cluster_alias_name:
        snapshot['cluster']['alias'] = cluster_alias_name
    if cluster_alias_id:
        snapshot['cluster']['alias_id'] = cluster_alias_id

    # Save snapshot in cluster-specific directory
    snapshot_dir = cluster_output_dir / "snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    snapshot_file = snapshot_dir / f"snapshot-{timestamp}.json"

    with open(snapshot_file, 'w') as f:
        json.dump(snapshot, f, indent=2)

    print(f"\nSnapshot saved: {snapshot_file}")
    print()

    # Step 2: Detect changes
    print("Step 2: Detecting changes...")
    print("-" * 70)
    diff_data = None

    # Find previous snapshot in this cluster's directory
    previous_snapshots = find_latest_snapshots(snapshot_dir=str(snapshot_dir), count=2)

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

    # Step 3: Categorize resources
    print("Step 3: Categorizing resources...")
    print("-" * 70)
    try:
        categorizer = ResourceCategorizer()
        resource_summary = categorizer.generate_summary(snapshot.get('pods', []))
        print(f"  ✓ Categorized {len(snapshot.get('pods', []))} pods")
        print(f"  ✓ Total VPC: {resource_summary.get('licensing', {}).get('total_vpc', 0):.2f}")
    except Exception as e:
        print(f"  ⚠️  Resource categorization failed: {e}")
        resource_summary = None

    print()

    # Step 4: Render dashboard
    print("Step 4: Rendering dashboard...")
    print("-" * 70)
    dashboard_path = cluster_output_dir / "dashboard.html"
    dashboard_file = render_dashboard(str(snapshot_file), output_path=str(dashboard_path), diff=diff_data)

    print()

    # Step 5: Export to Excel
    print("Step 5: Exporting to Excel...")
    print("-" * 70)
    excel_file = None
    try:
        excel_output = cluster_output_dir / f"chief-console-{timestamp}.xlsx"
        exporter = ExcelExporter(snapshot, resource_summary)
        excel_file = exporter.export(str(excel_output))
    except ImportError:
        print("  ⚠️  Excel export skipped: openpyxl not installed")
        print("  Install with: pip3 install openpyxl")
    except Exception as e:
        import traceback
        print(f"  ⚠️  Excel export failed: {e}")
        traceback.print_exc()

    print()
    print("=" * 70)
    print("CHIEF CONSOLE READY")
    print("=" * 70)
    print()
    print(f"Dashboard: {dashboard_file}")
    print(f"Snapshot:  {snapshot_file}")
    if excel_file:
        print(f"Excel:     {excel_file}")
    print()

    # Auto-open dashboard in browser
    import platform
    import subprocess

    try:
        dashboard_abs_path = Path(dashboard_file).absolute()
        print(f"🚀 Opening dashboard in browser...")

        if platform.system() == "Darwin":  # macOS
            subprocess.run(["open", str(dashboard_abs_path)], check=False)
        elif platform.system() == "Windows":
            subprocess.run(["start", str(dashboard_abs_path)], shell=True, check=False)
        else:  # Linux
            subprocess.run(["xdg-open", str(dashboard_abs_path)], check=False)

        print(f"   ✓ Dashboard opened: {dashboard_abs_path}")
    except Exception as e:
        print(f"   ⚠️  Could not auto-open dashboard: {e}")
        print(f"   Open manually: file://{Path(dashboard_file).absolute()}")

    if excel_file:
        print(f"\n📊 Excel file location:")
        print(f"   {Path(excel_file).absolute()}")

    print()
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
