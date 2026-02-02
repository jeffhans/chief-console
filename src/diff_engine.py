"""
Snapshot Diff Engine for CP4I Chief Console

Compares snapshots over time to detect changes and generate insights.
Categorizes changes by importance and type.
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path


class SnapshotDiff:
    """Represents differences between two snapshots"""

    def __init__(self, previous: Dict[str, Any], current: Dict[str, Any]):
        self.previous = previous
        self.current = current
        self.changes = {
            'additions': [],
            'deletions': [],
            'modifications': [],
            'critical': [],
            'important': [],
            'informational': []
        }

    def compare(self) -> Dict[str, Any]:
        """Run complete comparison and return categorized changes"""
        # Compare different aspects
        self._compare_operators()
        self._compare_pods()
        self._compare_namespaces()
        self._compare_nodes()
        self._compare_kafka()
        self._compare_routes()

        # Categorize by priority
        self._categorize_changes()

        # Generate summary
        summary = self._generate_summary()

        return {
            'metadata': {
                'previous_timestamp': self.previous.get('metadata', {}).get('collection_timestamp'),
                'current_timestamp': self.current.get('metadata', {}).get('collection_timestamp'),
                'time_elapsed': self._calculate_elapsed_time(),
            },
            'changes': self.changes,
            'summary': summary,
        }

    def _compare_operators(self):
        """Compare operators between snapshots"""
        prev_ops = {op['name']: op for op in self.previous.get('operators', {}).get('all', [])}
        curr_ops = {op['name']: op for op in self.current.get('operators', {}).get('all', [])}

        # New operators
        for name, op in curr_ops.items():
            if name not in prev_ops:
                self.changes['additions'].append({
                    'type': 'operator',
                    'action': 'added',
                    'name': op.get('display_name', name),
                    'namespace': op.get('namespace'),
                    'version': op.get('version'),
                    'phase': op.get('phase'),
                    'is_cp4i': op.get('is_cp4i', False)
                })

        # Removed operators
        for name, op in prev_ops.items():
            if name not in curr_ops:
                self.changes['deletions'].append({
                    'type': 'operator',
                    'action': 'removed',
                    'name': op.get('display_name', name),
                    'namespace': op.get('namespace')
                })

        # Modified operators
        for name in set(prev_ops.keys()) & set(curr_ops.keys()):
            prev = prev_ops[name]
            curr = curr_ops[name]

            if prev.get('phase') != curr.get('phase'):
                self.changes['modifications'].append({
                    'type': 'operator',
                    'action': 'status_changed',
                    'name': curr.get('display_name', name),
                    'namespace': curr.get('namespace'),
                    'old_status': prev.get('phase'),
                    'new_status': curr.get('phase'),
                    'is_cp4i': curr.get('is_cp4i', False)
                })

    def _compare_pods(self):
        """Compare pods between snapshots"""
        prev_pods = {f"{p['namespace']}/{p['name']}": p
                     for p in self.previous.get('pods', [])}
        curr_pods = {f"{p['namespace']}/{p['name']}": p
                     for p in self.current.get('pods', [])}

        # New pods
        for key, pod in curr_pods.items():
            if key not in prev_pods:
                self.changes['additions'].append({
                    'type': 'pod',
                    'action': 'created',
                    'name': pod['name'],
                    'namespace': pod['namespace'],
                    'phase': pod.get('phase'),
                    'ready': pod.get('ready')
                })

        # Removed pods
        for key, pod in prev_pods.items():
            if key not in curr_pods:
                self.changes['deletions'].append({
                    'type': 'pod',
                    'action': 'deleted',
                    'name': pod['name'],
                    'namespace': pod['namespace']
                })

        # Modified pods (restarts, status changes)
        for key in set(prev_pods.keys()) & set(curr_pods.keys()):
            prev = prev_pods[key]
            curr = curr_pods[key]

            # Check for restarts
            prev_restarts = prev.get('restarts', 0)
            curr_restarts = curr.get('restarts', 0)

            if curr_restarts > prev_restarts:
                restart_count = curr_restarts - prev_restarts
                self.changes['modifications'].append({
                    'type': 'pod',
                    'action': 'restarted',
                    'name': curr['name'],
                    'namespace': curr['namespace'],
                    'restart_count': restart_count,
                    'total_restarts': curr_restarts,
                    'severity': 'critical' if curr_restarts >= 5 else 'warning'
                })

            # Check for phase changes
            if prev.get('phase') != curr.get('phase'):
                self.changes['modifications'].append({
                    'type': 'pod',
                    'action': 'phase_changed',
                    'name': curr['name'],
                    'namespace': curr['namespace'],
                    'old_phase': prev.get('phase'),
                    'new_phase': curr.get('phase')
                })

    def _compare_namespaces(self):
        """Compare namespaces between snapshots"""
        prev_ns = {ns['name']: ns for ns in self.previous.get('namespaces', [])}
        curr_ns = {ns['name']: ns for ns in self.current.get('namespaces', [])}

        # New namespaces
        for name, ns in curr_ns.items():
            if name not in prev_ns:
                # Check if it's CP4I-related
                is_cp4i = any(keyword in name.lower()
                             for keyword in ['cp4i', 'integration', 'ibm', 'kafka', 'mq', 'ace', 'apic'])

                self.changes['additions'].append({
                    'type': 'namespace',
                    'action': 'created',
                    'name': name,
                    'status': ns.get('status'),
                    'is_cp4i': is_cp4i
                })

        # Removed namespaces
        for name, ns in prev_ns.items():
            if name not in curr_ns:
                self.changes['deletions'].append({
                    'type': 'namespace',
                    'action': 'deleted',
                    'name': name
                })

    def _compare_nodes(self):
        """Compare nodes between snapshots"""
        prev_nodes = {n['name']: n for n in self.previous.get('nodes', [])}
        curr_nodes = {n['name']: n for n in self.current.get('nodes', [])}

        # Node status changes
        for name in set(prev_nodes.keys()) & set(curr_nodes.keys()):
            prev = prev_nodes[name]
            curr = curr_nodes[name]

            if prev.get('status') != curr.get('status'):
                self.changes['modifications'].append({
                    'type': 'node',
                    'action': 'status_changed',
                    'name': name,
                    'old_status': prev.get('status'),
                    'new_status': curr.get('status'),
                    'severity': 'critical' if curr.get('status') != 'Ready' else 'info'
                })

    def _compare_kafka(self):
        """Compare Kafka/Event Streams resources"""
        prev_kafka = self.previous.get('kafka', {})
        curr_kafka = self.current.get('kafka', {})

        if not prev_kafka or not curr_kafka:
            return

        # Event Streams instances
        prev_instances = {i['name']: i for i in prev_kafka.get('instances', [])}
        curr_instances = {i['name']: i for i in curr_kafka.get('instances', [])}

        for name, instance in curr_instances.items():
            if name not in prev_instances:
                self.changes['additions'].append({
                    'type': 'event_streams',
                    'action': 'created',
                    'name': name,
                    'namespace': instance.get('namespace'),
                    'status': instance.get('status'),
                    'bootstrap': instance.get('bootstrap_server')
                })

        # Topics
        prev_topics = {}
        curr_topics = {}

        for es_name, topics in prev_kafka.get('topics', {}).items():
            for topic in topics:
                prev_topics[f"{es_name}/{topic['name']}"] = topic

        for es_name, topics in curr_kafka.get('topics', {}).items():
            for topic in topics:
                curr_topics[f"{es_name}/{topic['name']}"] = topic

        # New topics
        for key, topic in curr_topics.items():
            if key not in prev_topics:
                self.changes['additions'].append({
                    'type': 'kafka_topic',
                    'action': 'created',
                    'name': topic['name'],
                    'namespace': topic.get('namespace'),
                    'partitions': topic.get('partitions'),
                    'replicas': topic.get('replicas'),
                    'category': topic.get('category', 'general')
                })

        # Topic modifications (partition changes, etc.)
        for key in set(prev_topics.keys()) & set(curr_topics.keys()):
            prev = prev_topics[key]
            curr = curr_topics[key]

            if prev.get('partitions') != curr.get('partitions'):
                self.changes['modifications'].append({
                    'type': 'kafka_topic',
                    'action': 'partitions_changed',
                    'name': curr['name'],
                    'old_partitions': prev.get('partitions'),
                    'new_partitions': curr.get('partitions')
                })

    def _compare_routes(self):
        """Compare routes between snapshots"""
        prev_routes = {f"{r['namespace']}/{r['name']}": r
                       for r in self.previous.get('routes', [])}
        curr_routes = {f"{r['namespace']}/{r['name']}": r
                       for r in self.current.get('routes', [])}

        # New routes
        for key, route in curr_routes.items():
            if key not in prev_routes:
                self.changes['additions'].append({
                    'type': 'route',
                    'action': 'created',
                    'name': route['name'],
                    'namespace': route['namespace'],
                    'url': route.get('url'),
                    'service': route.get('service')
                })

    def _categorize_changes(self):
        """Categorize changes by priority"""
        # Get CP4I namespaces from current snapshot
        cp4i_namespaces = self.current.get('cp4i_namespaces', [])

        for change in self.changes['additions'] + self.changes['modifications'] + self.changes['deletions']:
            # Check if change is in a CP4I namespace
            in_cp4i_namespace = change.get('namespace') in cp4i_namespaces

            # Critical changes
            if (change.get('severity') == 'critical' or
                change.get('type') == 'node' and change.get('new_status') != 'Ready' or
                change.get('type') == 'pod' and change.get('action') == 'restarted' and change.get('total_restarts', 0) >= 5):
                self.changes['critical'].append(change)

            # Important changes (CP4I-related)
            elif (change.get('is_cp4i') or
                  change.get('type') in ['event_streams', 'kafka_topic'] or
                  change.get('type') == 'operator' and change.get('is_cp4i') or
                  change.get('type') == 'namespace' and change.get('is_cp4i') or
                  change.get('type') == 'pod' and change.get('action') == 'restarted' or
                  change.get('type') == 'pod' and in_cp4i_namespace or
                  change.get('type') == 'route' and in_cp4i_namespace):
                self.changes['important'].append(change)

            # Informational
            else:
                self.changes['informational'].append(change)

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        prev_ops = self.previous.get('operators', {})
        curr_ops = self.current.get('operators', {})

        prev_cp4i = len(prev_ops.get('cp4i', []))
        curr_cp4i = len(curr_ops.get('cp4i', []))

        return {
            'operators': {
                'previous': len(prev_ops.get('all', [])),
                'current': len(curr_ops.get('all', [])),
                'change': len(curr_ops.get('all', [])) - len(prev_ops.get('all', []))
            },
            'cp4i_operators': {
                'previous': prev_cp4i,
                'current': curr_cp4i,
                'change': curr_cp4i - prev_cp4i
            },
            'pods': {
                'previous': len(self.previous.get('pods', [])),
                'current': len(self.current.get('pods', [])),
                'change': len(self.current.get('pods', [])) - len(self.previous.get('pods', []))
            },
            'namespaces': {
                'previous': len(self.previous.get('namespaces', [])),
                'current': len(self.current.get('namespaces', [])),
                'change': len(self.current.get('namespaces', [])) - len(self.previous.get('namespaces', []))
            },
            'kafka_instances': {
                'previous': len(self.previous.get('kafka', {}).get('instances', [])),
                'current': len(self.current.get('kafka', {}).get('instances', [])),
                'change': len(self.current.get('kafka', {}).get('instances', [])) - len(self.previous.get('kafka', {}).get('instances', []))
            },
            'change_counts': {
                'additions': len(self.changes['additions']),
                'deletions': len(self.changes['deletions']),
                'modifications': len(self.changes['modifications']),
                'critical': len(self.changes['critical']),
                'important': len(self.changes['important']),
                'informational': len(self.changes['informational'])
            }
        }

    def _calculate_elapsed_time(self) -> str:
        """Calculate time elapsed between snapshots"""
        try:
            prev_time = datetime.fromisoformat(
                self.previous.get('metadata', {}).get('collection_timestamp', '').replace('Z', '+00:00')
            )
            curr_time = datetime.fromisoformat(
                self.current.get('metadata', {}).get('collection_timestamp', '').replace('Z', '+00:00')
            )
            delta = curr_time - prev_time

            minutes = int(delta.total_seconds() / 60)
            if minutes < 60:
                return f"{minutes} minute{'s' if minutes != 1 else ''}"
            else:
                hours = minutes // 60
                remaining_mins = minutes % 60
                return f"{hours} hour{'s' if hours != 1 else ''}, {remaining_mins} minute{'s' if remaining_mins != 1 else ''}"
        except:
            return "Unknown"


def compare_snapshots(previous_path: str, current_path: str) -> Dict[str, Any]:
    """
    Compare two snapshot files and return diff

    Args:
        previous_path: Path to older snapshot
        current_path: Path to newer snapshot

    Returns:
        Dictionary containing categorized changes
    """
    with open(previous_path, 'r') as f:
        previous = json.load(f)

    with open(current_path, 'r') as f:
        current = json.load(f)

    diff = SnapshotDiff(previous, current)
    return diff.compare()


def find_latest_snapshots(snapshot_dir: str = "output/snapshots", count: int = 2) -> List[str]:
    """
    Find the N most recent snapshots

    Args:
        snapshot_dir: Directory containing snapshots
        count: Number of snapshots to return

    Returns:
        List of snapshot file paths, newest first
    """
    snapshot_path = Path(snapshot_dir)
    if not snapshot_path.exists():
        return []

    snapshots = sorted(
        snapshot_path.glob("snapshot-*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    return [str(s) for s in snapshots[:count]]


if __name__ == "__main__":
    # CLI usage
    import sys

    # Find latest two snapshots
    snapshots = find_latest_snapshots()

    if len(snapshots) < 2:
        print("Not enough snapshots to compare. Need at least 2.")
        print(f"Found {len(snapshots)} snapshot(s).")
        sys.exit(1)

    previous = snapshots[1]  # Older
    current = snapshots[0]   # Newer

    print(f"Comparing:")
    print(f"  Previous: {previous}")
    print(f"  Current:  {current}")
    print()

    diff = compare_snapshots(previous, current)

    # Print results
    print("=" * 70)
    print("CHANGE DETECTION REPORT")
    print("=" * 70)
    print()

    metadata = diff['metadata']
    print(f"Time elapsed: {metadata['time_elapsed']}")
    print()

    # Critical changes
    if diff['changes']['critical']:
        print("🔴 CRITICAL CHANGES")
        print("-" * 70)
        for change in diff['changes']['critical']:
            print(f"  • {change['type']}: {change.get('name')} - {change['action']}")
        print()

    # Important changes
    if diff['changes']['important']:
        print("🟡 IMPORTANT CHANGES")
        print("-" * 70)
        for change in diff['changes']['important'][:10]:  # Limit to 10
            if change['type'] == 'operator' and change['action'] == 'added':
                print(f"  ✅ New operator: {change['name']} v{change.get('version')} ({change['namespace']})")
            elif change['type'] == 'event_streams':
                print(f"  🎉 Event Streams: {change['name']} - {change['status']}")
            elif change['type'] == 'kafka_topic':
                print(f"  📊 Topic: {change['name']} ({change.get('partitions')} partitions)")
            elif change['type'] == 'pod' and change['action'] == 'restarted':
                print(f"  🔄 Pod restarted: {change['name']} ({change['restart_count']}x)")
            else:
                print(f"  • {change['type']}: {change.get('name')} - {change['action']}")
        print()

    # Summary
    print("📊 SUMMARY")
    print("-" * 70)
    summary = diff['summary']
    for category, stats in summary.items():
        if isinstance(stats, dict) and 'change' in stats:
            change = stats['change']
            if change != 0:
                sign = '+' if change > 0 else ''
                print(f"  {category}: {stats['previous']} → {stats['current']} ({sign}{change})")

    print()
    print("=" * 70)
