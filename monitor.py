#!/usr/bin/env python3
"""
CP4I Mission Console - Automated Monitoring

Runs the mission console periodically and optionally opens the dashboard.
Highlights changes in the terminal for easy tracking.
"""

import sys
import time
import subprocess
import os
from pathlib import Path
from datetime import datetime
import argparse
import yaml

# Add src to path for cluster utils
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from cluster_utils import get_cluster_info, format_cluster_name


class MissionConsoleMonitor:
    """Automated monitoring for Mission Console"""

    def __init__(self, interval: int = 120, auto_open: bool = False, max_runs: int = 0, min_gap: int = 10):
        """
        Initialize monitor

        Args:
            interval: Seconds between run STARTS (default: 120 = 2 minutes)
            auto_open: Automatically open dashboard in browser after each run
            max_runs: Maximum number of runs (0 = infinite)
            min_gap: Minimum seconds between runs, even if collection is slow (default: 10)
        """
        self.interval = interval
        self.auto_open = auto_open
        self.max_runs = max_runs
        self.min_gap = min_gap
        self.run_count = 0
        self.last_critical = 0
        self.last_important = 0
        self.run_durations = []  # Track run times for statistics

        # Get cluster info
        self.cluster_info = get_cluster_info()
        self.cluster_id = self.cluster_info.get('cluster_id')
        self.cluster_name = format_cluster_name(self.cluster_id) if self.cluster_id else 'Unknown'

        # Load aliases from config.yaml
        self.cluster_alias = None
        self.cluster_alias_id = None
        config_path = Path(__file__).parent / "config.yaml"
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f) or {}
                aliases = config.get("cluster_aliases", {}) or {}
                alias_entry = aliases.get(self.cluster_id)
                if isinstance(alias_entry, dict):
                    self.cluster_alias = alias_entry.get("name")
                    self.cluster_alias_id = alias_entry.get("id")
                elif isinstance(alias_entry, str):
                    self.cluster_alias = alias_entry
            except Exception:
                pass

    def run(self):
        """Run the monitoring loop"""
        print("=" * 70)
        print("CP4I MISSION CONSOLE - AUTOMATED MONITORING")
        print("=" * 70)

        # Display cluster info
        if self.cluster_info.get('logged_in'):
            if self.cluster_alias:
                print(f"📍 Name: {self.cluster_alias}")
            if self.cluster_alias_id:
                print(f"   ID: {self.cluster_alias_id}")
            print(f"📍 Cluster ID: {self.cluster_info.get('server').replace('https://api.','').split(':')[0] if self.cluster_info.get('server') else self.cluster_name}")
            print(f"   Server: {self.cluster_info.get('server')}")
            print(f"   User: {self.cluster_info.get('user')}")
        else:
            print("❌ ERROR: Not logged into OpenShift cluster")
            print("   Run: oc login --server=... --token=...")
            return

        print()
        print(f"Monitoring interval: {self.interval} seconds ({self.interval//60} minutes)")
        print(f"Auto-open dashboard: {'Yes' if self.auto_open else 'No'}")
        print(f"Max runs: {'Unlimited' if self.max_runs == 0 else self.max_runs}")
        print()
        print("Press Ctrl+C to stop monitoring")
        print("=" * 70)
        print()

        try:
            while True:
                self.run_count += 1

                if self.max_runs > 0 and self.run_count > self.max_runs:
                    print(f"\nReached max runs ({self.max_runs}). Stopping.")
                    break

                print(f"\n{'='*70}")
                print(f"RUN #{self.run_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*70}\n")

                # Track run duration
                run_start = time.time()

                # Run mission console
                self._run_console()

                # Open dashboard if requested
                if self.auto_open:
                    self._open_dashboard()

                # Calculate duration
                run_duration = time.time() - run_start
                self.run_durations.append(run_duration)

                # Display duration and statistics
                self._show_run_stats(run_duration)

                # Wait for next run
                if self.max_runs == 0 or self.run_count < self.max_runs:
                    self._wait_for_next_run(run_duration)

        except KeyboardInterrupt:
            print("\n\n" + "=" * 70)
            print("MONITORING STOPPED")
            print("=" * 70)
            print(f"Total runs: {self.run_count}")
            print(f"Last run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()

    def _run_console(self):
        """Run the mission console and capture output"""
        try:
            # Run mission console
            result = subprocess.run(
                [sys.executable, "chief_console.py"],
                capture_output=True,
                text=True,
                timeout=120
            )

            # Parse output for change detection info
            output = result.stdout

            # Look for change detection results
            critical_changes = 0
            important_changes = 0

            for line in output.split('\n'):
                if '🔴' in line and 'critical' in line.lower():
                    try:
                        critical_changes = int(line.split()[1])
                    except:
                        pass
                elif '🟡' in line and 'important' in line.lower():
                    try:
                        important_changes = int(line.split()[1])
                    except:
                        pass

            # Display summary
            if critical_changes > 0:
                print(f"🔴 CRITICAL: {critical_changes} change(s) detected!")
                if critical_changes > self.last_critical:
                    print(f"   ⚠️  +{critical_changes - self.last_critical} new critical issues!")
                self.last_critical = critical_changes
            elif important_changes > 0:
                print(f"🟡 IMPORTANT: {important_changes} change(s) detected")
                if important_changes > self.last_important:
                    print(f"   📊 +{important_changes - self.last_important} new changes")
                self.last_important = important_changes
            else:
                print("✅ No significant changes detected")
                self.last_critical = 0
                self.last_important = 0

            # Show collection summary
            for line in output.split('\n'):
                if 'Collection complete!' in line:
                    print(f"   {line.strip()}")
                elif any(keyword in line for keyword in ['CP4I namespaces', 'Total operators', 'CP4I operators']):
                    print(f"   {line.strip()}")

            print(f"\n✅ Collection #{self.run_count} complete")

        except subprocess.TimeoutExpired:
            print(f"⚠️  Collection #{self.run_count} timed out (>2 minutes)")
        except Exception as e:
            print(f"❌ Error during collection #{self.run_count}: {e}")

    def _open_dashboard(self):
        """Open dashboard in browser (cluster-aware)"""
        # Use cluster-specific dashboard path
        if self.cluster_id:
            dashboard_path = Path("output") / self.cluster_id / "dashboard.html"
        else:
            dashboard_path = Path("output/dashboard.html")

        dashboard_path = dashboard_path.absolute()

        if dashboard_path.exists():
            try:
                if sys.platform == "darwin":  # macOS
                    subprocess.run(["open", str(dashboard_path)], check=False)
                elif sys.platform == "linux":
                    subprocess.run(["xdg-open", str(dashboard_path)], check=False)
                elif sys.platform == "win32":
                    subprocess.run(["start", str(dashboard_path)], shell=True, check=False)
                print(f"   📊 Dashboard opened: {dashboard_path}")
            except Exception as e:
                print(f"   ⚠️  Could not open dashboard: {e}")
        else:
            print(f"   ⚠️  Dashboard not found: {dashboard_path}")

    def _show_run_stats(self, run_duration: float):
        """Display run duration and statistics"""
        print(f"\n⏱️  Collection took {run_duration:.1f}s")

        # Warn if run is taking too long relative to interval
        if run_duration > self.interval * 0.8:
            print(f"   ⚠️  Warning: Collection took {(run_duration/self.interval)*100:.0f}% of interval!")
            print(f"   Consider increasing --interval to avoid hammering the cluster")

        # Show average if we have multiple runs
        if len(self.run_durations) > 1:
            avg_duration = sum(self.run_durations) / len(self.run_durations)
            print(f"   📊 Average: {avg_duration:.1f}s over {len(self.run_durations)} runs")

    def _wait_for_next_run(self, run_duration: float):
        """
        Wait for next run with countdown, accounting for actual run time

        Args:
            run_duration: How long the collection took in seconds
        """
        # Calculate actual wait time: interval - run_duration, but at least min_gap
        wait_time = max(self.interval - run_duration, self.min_gap)

        if wait_time < self.min_gap:
            print(f"\n⚠️  Run took {run_duration:.1f}s, enforcing minimum {self.min_gap}s gap")

        print(f"\n⏳ Next run in {wait_time:.0f} seconds...")

        # Show countdown for last 10 seconds
        remaining = wait_time

        while remaining > 0:
            if remaining <= 10:
                print(f"\r   {remaining:.0f}s...", end="", flush=True)
            time.sleep(1)
            remaining -= 1

        print("\r" + " " * 20 + "\r", end="")  # Clear countdown


def main():
    parser = argparse.ArgumentParser(
        description="CP4I Mission Console - Automated Monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
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
        """
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=120,
        help='Interval between runs in seconds (default: 120 = 2 minutes)'
    )

    parser.add_argument(
        '--auto-open',
        action='store_true',
        help='Automatically open dashboard in browser after each run'
    )

    parser.add_argument(
        '--max-runs',
        type=int,
        default=0,
        help='Maximum number of runs (0 = unlimited, default: 0)'
    )

    parser.add_argument(
        '--min-gap',
        type=int,
        default=10,
        help='Minimum seconds between runs, even if collection is slow (default: 10)'
    )

    args = parser.parse_args()

    # Validate interval
    if args.interval < 10:
        print("⚠️  Warning: Interval less than 10 seconds may overload the cluster")
        print("   Recommended minimum: 30 seconds")
        print()

    monitor = MissionConsoleMonitor(
        interval=args.interval,
        auto_open=args.auto_open,
        max_runs=args.max_runs,
        min_gap=args.min_gap
    )

    monitor.run()


if __name__ == "__main__":
    main()
