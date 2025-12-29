"""
Kafka / Event Streams Data Collector

Collects Kafka topic and consumer group information from IBM Event Streams
or vanilla Kafka deployments in CP4I environments.

Implements best-effort collection with graceful degradation.
"""

import json
import subprocess
import re
from typing import Dict, List, Optional, Any
from datetime import datetime


class KafkaCollector:
    """Collects Kafka/Event Streams data via oc CLI and kafka tools"""

    def __init__(self):
        self.data = {}
        self.errors = []
        self.warnings = []
        self.event_streams_instances = []

    def _run_oc(self, args: List[str], output_format: str = "json") -> Optional[Any]:
        """Run oc command and return parsed output"""
        cmd = ["oc"] + args

        if output_format in ["json", "yaml"] and "-o" not in args:
            cmd.extend(["-o", output_format])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return None

            if output_format == "json":
                return json.loads(result.stdout) if result.stdout else None
            else:
                return result.stdout.strip()

        except Exception as e:
            self.errors.append(f"Command error: {e}")
            return None

    def discover_event_streams(self) -> List[Dict[str, Any]]:
        """
        Discover IBM Event Streams instances in the cluster

        Returns list of Event Streams instances with connection info
        """
        print("Discovering Event Streams instances...")

        instances = []

        # Look for EventStreams custom resources
        es_data = self._run_oc(["get", "eventstreams", "--all-namespaces"])

        if es_data and 'items' in es_data:
            for es in es_data['items']:
                instance = {
                    'name': es['metadata']['name'],
                    'namespace': es['metadata']['namespace'],
                    'status': es.get('status', {}).get('phase', 'Unknown'),
                    'version': es.get('status', {}).get('versions', {}).get('reconciled'),
                    'created': es['metadata'].get('creationTimestamp'),
                }

                # Get bootstrap server info
                bootstrap = self._get_bootstrap_server(
                    instance['name'],
                    instance['namespace']
                )
                instance['bootstrap_server'] = bootstrap

                instances.append(instance)

        if not instances:
            self.warnings.append("No Event Streams instances found. Kafka collection unavailable.")
        else:
            print(f"  Found {len(instances)} Event Streams instance(s)")

        self.event_streams_instances = instances
        return instances

    def _get_bootstrap_server(self, es_name: str, namespace: str) -> Optional[str]:
        """Get bootstrap server URL for an Event Streams instance"""
        # Look for the bootstrap route
        route_name = f"{es_name}-kafka-bootstrap"
        route_data = self._run_oc(["get", "route", route_name, "-n", namespace])

        if route_data and 'spec' in route_data:
            host = route_data['spec'].get('host')
            if host:
                return f"{host}:443"

        # Fallback: try to get from service
        svc_data = self._run_oc(["get", "service", route_name, "-n", namespace])
        if svc_data and 'spec' in svc_data:
            cluster_ip = svc_data['spec'].get('clusterIP')
            port = svc_data['spec'].get('ports', [{}])[0].get('port', 9092)
            if cluster_ip:
                return f"{cluster_ip}:{port}"

        return None

    def collect_topics(self, es_instance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Collect Kafka topics for an Event Streams instance

        Args:
            es_instance: Event Streams instance info from discover_event_streams()

        Returns:
            List of topic information
        """
        namespace = es_instance['namespace']
        es_name = es_instance['name']

        print(f"Collecting topics for {es_name} in {namespace}...")

        # Look for KafkaTopic custom resources
        topic_data = self._run_oc(["get", "kafkatopic", "-n", namespace])

        if not topic_data or 'items' not in topic_data:
            self.warnings.append(f"No topics found for {es_name}")
            return []

        topics = []
        for topic in topic_data['items']:
            # Check if this topic belongs to this Event Streams instance
            owner_refs = topic['metadata'].get('ownerReferences', [])
            belongs_to_instance = any(
                ref.get('name') == es_name for ref in owner_refs
            ) if owner_refs else True  # Assume yes if no owner refs

            # Also check labels
            labels = topic['metadata'].get('labels', {})
            if 'eventstreams.ibm.com/cluster' in labels:
                belongs_to_instance = labels['eventstreams.ibm.com/cluster'] == es_name

            if not belongs_to_instance:
                continue

            topic_info = {
                'name': topic['metadata']['name'],
                'namespace': namespace,
                'partitions': topic['spec'].get('partitions', 1),
                'replicas': topic['spec'].get('replicas', 1),
                'retention_ms': topic['spec'].get('config', {}).get('retention.ms'),
                'status': topic.get('status', {}).get('conditions', []),
                'created': topic['metadata'].get('creationTimestamp'),
            }

            # Categorize topic by naming pattern (for BTDS-style architectures)
            topic_info['category'] = self._categorize_topic(topic_info['name'])

            topics.append(topic_info)

        print(f"  Found {len(topics)} topic(s)")
        return topics

    def _categorize_topic(self, topic_name: str) -> str:
        """
        Categorize topic by naming pattern

        Common patterns:
        - *.raw -> raw data
        - *.enriched -> enriched data
        - *.curated -> curated data
        """
        name_lower = topic_name.lower()

        if any(pattern in name_lower for pattern in ['raw', '.r.']):
            return 'raw'
        elif any(pattern in name_lower for pattern in ['enriched', 'enrich', '.e.']):
            return 'enriched'
        elif any(pattern in name_lower for pattern in ['curated', 'cur', '.c.']):
            return 'curated'
        elif any(pattern in name_lower for pattern in ['dlq', 'dead', 'error']):
            return 'dlq'
        else:
            return 'general'

    def collect_consumer_groups(self, es_instance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Collect Kafka consumer groups for an Event Streams instance

        Args:
            es_instance: Event Streams instance info

        Returns:
            List of consumer group information
        """
        namespace = es_instance['namespace']
        es_name = es_instance['name']

        print(f"Collecting consumer groups for {es_name}...")

        # Look for KafkaUser custom resources (may indicate consumers)
        user_data = self._run_oc(["get", "kafkauser", "-n", namespace])

        users = []
        if user_data and 'items' in user_data:
            for user in user_data['items']:
                labels = user['metadata'].get('labels', {})
                if 'eventstreams.ibm.com/cluster' in labels:
                    if labels['eventstreams.ibm.com/cluster'] != es_name:
                        continue

                user_info = {
                    'name': user['metadata']['name'],
                    'namespace': namespace,
                    'authentication_type': user['spec'].get('authentication', {}).get('type'),
                    'created': user['metadata'].get('creationTimestamp'),
                }
                users.append(user_info)

        # Note: Consumer group lag information requires direct Kafka connection
        # which may not be available without credentials. This is best-effort.
        self.warnings.append(
            f"Consumer group lag metrics unavailable without direct Kafka access. "
            f"Found {len(users)} Kafka users."
        )

        return users

    def collect_kafka_pods(self, namespace: str) -> List[Dict[str, Any]]:
        """Collect Kafka-related pods in a namespace"""
        print(f"Collecting Kafka pods in {namespace}...")

        pod_data = self._run_oc([
            "get", "pods",
            "-n", namespace,
            "-l", "eventstreams.ibm.com/kind=Kafka"
        ])

        if not pod_data or 'items' not in pod_data:
            return []

        pods = []
        for pod in pod_data['items']:
            pod_info = {
                'name': pod['metadata']['name'],
                'phase': pod['status'].get('phase', 'Unknown'),
                'ready': self._count_ready_containers(pod),
                'restarts': self._count_restarts(pod),
                'node': pod['spec'].get('nodeName'),
            }
            pods.append(pod_info)

        return pods

    def _count_ready_containers(self, pod: Dict) -> str:
        """Count ready containers in a pod"""
        container_statuses = pod['status'].get('containerStatuses', [])
        ready = sum(1 for c in container_statuses if c.get('ready'))
        total = len(container_statuses)
        return f"{ready}/{total}"

    def _count_restarts(self, pod: Dict) -> int:
        """Count total restarts across all containers"""
        container_statuses = pod['status'].get('containerStatuses', [])
        return sum(c.get('restartCount', 0) for c in container_statuses)

    def collect_all(self) -> Dict[str, Any]:
        """
        Collect all Kafka/Event Streams data

        Returns comprehensive snapshot of Kafka state
        """
        print("=" * 60)
        print("Kafka / Event Streams Data Collection")
        print("=" * 60)

        snapshot = {
            'metadata': {
                'collection_timestamp': datetime.now().isoformat(),
                'collector_version': '1.0.0',
            },
            'event_streams': {
                'instances': [],
                'topics': {},
                'consumer_groups': {},
                'pods': {},
            }
        }

        # Discover Event Streams instances
        instances = self.discover_event_streams()
        snapshot['event_streams']['instances'] = instances

        if not instances:
            snapshot['metadata']['warnings'] = [
                "No Event Streams instances found. Skipping Kafka collection."
            ]
            snapshot['metadata']['errors'] = []
            snapshot['metadata']['kafka_available'] = False
            return snapshot

        snapshot['metadata']['kafka_available'] = True

        # Collect data for each instance
        for instance in instances:
            es_name = instance['name']
            namespace = instance['namespace']

            # Collect topics
            topics = self.collect_topics(instance)
            snapshot['event_streams']['topics'][es_name] = topics

            # Collect consumer groups / users
            users = self.collect_consumer_groups(instance)
            snapshot['event_streams']['consumer_groups'][es_name] = users

            # Collect Kafka pods
            pods = self.collect_kafka_pods(namespace)
            snapshot['event_streams']['pods'][es_name] = pods

        # Add errors and warnings
        snapshot['metadata']['errors'] = self.errors
        snapshot['metadata']['warnings'] = self.warnings

        # Summary
        total_topics = sum(len(topics) for topics in snapshot['event_streams']['topics'].values())
        total_users = sum(len(users) for users in snapshot['event_streams']['consumer_groups'].values())

        print("=" * 60)
        print("Collection complete!")
        print(f"  Event Streams instances: {len(instances)}")
        print(f"  Total topics: {total_topics}")
        print(f"  Kafka users: {total_users}")
        print(f"  Warnings: {len(self.warnings)}")
        print(f"  Errors: {len(self.errors)}")
        print("=" * 60)

        return snapshot


if __name__ == "__main__":
    # CLI usage
    collector = KafkaCollector()
    snapshot = collector.collect_all()

    # Save to file
    from pathlib import Path
    output_dir = Path("output/snapshots")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = output_dir / f"kafka-snapshot-{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump(snapshot, f, indent=2)

    print(f"\nKafka snapshot saved to: {output_file}")

    # Print warnings
    if snapshot['metadata']['warnings']:
        print("\nWarnings:")
        for warning in snapshot['metadata']['warnings']:
            print(f"  - {warning}")

    if snapshot['metadata']['errors']:
        print("\nErrors:")
        for error in snapshot['metadata']['errors']:
            print(f"  - {error}")
