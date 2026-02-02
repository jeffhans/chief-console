"""
OpenShift / CP4I Data Collector

Collects cluster state and CP4I-specific information via oc CLI.
Implements graceful degradation when CP4I is not installed or partially configured.
"""

import json
import subprocess
import re
from datetime import datetime
from typing import Dict, List, Optional, Any


class OCPCollector:
    """Collects OpenShift and CP4I data via oc CLI"""

    def __init__(self):
        self.data = {}
        self.errors = []
        self.warnings = []

    def _run_oc(self, args: List[str], output_format: str = "json", timeout: int = 30) -> Optional[Any]:
        """
        Run oc command and return parsed output

        Args:
            args: Command arguments (without 'oc')
            output_format: Output format (json, yaml, or raw)
            timeout: Command timeout in seconds (default: 30)

        Returns:
            Parsed output or None on error
        """
        cmd = ["oc"] + args

        if output_format in ["json", "yaml"] and "-o" not in args:
            cmd.extend(["-o", output_format])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode != 0:
                error_msg = f"Command failed: {' '.join(cmd)}\n{result.stderr}"
                self.errors.append(error_msg)
                return None

            if output_format == "json":
                return json.loads(result.stdout) if result.stdout else None
            elif output_format == "yaml":
                return result.stdout
            else:
                return result.stdout.strip()

        except subprocess.TimeoutExpired:
            self.errors.append(f"Command timeout: {' '.join(cmd)}")
            return None
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON parse error: {e}")
            return None
        except Exception as e:
            self.errors.append(f"Unexpected error: {e}")
            return None

    def collect_cluster_info(self) -> Dict[str, Any]:
        """Collect basic cluster information"""
        print("Collecting cluster info...")

        cluster_info = {
            'collection_timestamp': datetime.now().isoformat(),
            'version': None,
            'console_url': None,
            'api_url': None,
        }

        # Get cluster version
        version_data = self._run_oc(["get", "clusterversion", "version"])
        if version_data and 'status' in version_data:
            cluster_info['version'] = version_data['status'].get('desired', {}).get('version')
            cluster_info['version_history'] = version_data['status'].get('history', [])[:3]  # Last 3 versions

        # Get console and API URLs
        console = self._run_oc(["whoami", "--show-console"], output_format="raw")
        if console:
            cluster_info['console_url'] = console

        api = self._run_oc(["whoami", "--show-server"], output_format="raw")
        if api:
            cluster_info['api_url'] = api

        return cluster_info

    def collect_nodes(self) -> List[Dict[str, Any]]:
        """Collect node information including capacity and allocatable resources"""
        print("Collecting node information...")

        nodes_data = self._run_oc(["get", "nodes"])
        if not nodes_data or 'items' not in nodes_data:
            return []

        nodes = []
        for node in nodes_data['items']:
            node_info = {
                'name': node['metadata']['name'],
                'roles': node['metadata'].get('labels', {}).get('node-role.kubernetes.io', 'worker'),
                'status': 'Unknown',
                'capacity': node['status'].get('capacity', {}),
                'allocatable': node['status'].get('allocatable', {}),
                'created': node['metadata'].get('creationTimestamp'),
                'version': node['status']['nodeInfo'].get('kubeletVersion'),
            }

            # Determine status
            conditions = node['status'].get('conditions', [])
            for condition in conditions:
                if condition['type'] == 'Ready':
                    node_info['status'] = 'Ready' if condition['status'] == 'True' else 'NotReady'
                    break

            nodes.append(node_info)

        return nodes

    def collect_namespaces(self, filter_pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Collect namespace/project information

        Args:
            filter_pattern: Optional regex pattern to filter namespace names
        """
        print("Collecting namespaces...")

        ns_data = self._run_oc(["get", "projects"])
        if not ns_data or 'items' not in ns_data:
            return []

        namespaces = []
        for ns in ns_data['items']:
            ns_name = ns['metadata']['name']

            # Apply filter if provided
            if filter_pattern and not re.search(filter_pattern, ns_name, re.IGNORECASE):
                continue

            ns_info = {
                'name': ns_name,
                'status': ns['status'].get('phase', 'Unknown'),
                'created': ns['metadata'].get('creationTimestamp'),
                'labels': ns['metadata'].get('labels', {}),
                'annotations': ns['metadata'].get('annotations', {}),
            }

            namespaces.append(ns_info)

        return namespaces

    def discover_cp4i_namespaces(self) -> List[str]:
        """
        Discover namespaces that contain CP4I components

        Returns list of namespace names
        """
        print("Discovering CP4I namespaces...")

        # Common CP4I labels and patterns
        cp4i_patterns = [
            r'.*cp4i.*',
            r'.*integration.*',
            r'.*ibm.*navigator.*',
            r'.*eventstreams.*',
            r'.*apic.*',
            r'.*ace.*',
            r'.*mq.*',
        ]

        all_namespaces = self.collect_namespaces()
        cp4i_namespace_set = set()

        for ns in all_namespaces:
            # Check name patterns
            for pattern in cp4i_patterns:
                if re.search(pattern, ns['name'], re.IGNORECASE):
                    cp4i_namespace_set.add(ns['name'])
                    break
            else:
                # Check labels (both keys and values)
                labels = ns.get('labels', {})
                # Check label keys
                if any('cp4i' in k.lower() or 'integration' in k.lower() for k in labels.keys()):
                    cp4i_namespace_set.add(ns['name'])
                # Check label values
                elif any('cp4i' in str(v).lower() or 'integration' in str(v).lower() for v in labels.values()):
                    cp4i_namespace_set.add(ns['name'])

        # Also include namespaces hosting key CP4I custom resources (handles generic names like "tools")
        cr_kinds = [
            "eventstreams",
            "eventprocessing",
            "platformnavigator",
            "eventendpointmanagement",
        ]
        for kind in cr_kinds:
            cr_data = self._run_oc(["get", kind, "--all-namespaces"])
            if cr_data and 'items' in cr_data:
                for item in cr_data['items']:
                    ns_name = item['metadata'].get('namespace')
                    if ns_name:
                        cp4i_namespace_set.add(ns_name)

        cp4i_namespaces = sorted(cp4i_namespace_set)
        if not cp4i_namespaces:
            self.warnings.append("No CP4I namespaces discovered. Cluster may not have CP4I installed.")

        return cp4i_namespaces

    def collect_operators(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Collect installed operators (CSVs)

        Args:
            namespace: Optional namespace to filter (None = all namespaces)
        """
        print(f"Collecting operators{' in namespace: ' + namespace if namespace else ''}...")

        cmd = ["get", "csv"]
        if namespace:
            cmd.extend(["-n", namespace])
        else:
            cmd.append("--all-namespaces")

        # CSV listing can be slow; allow a longer timeout
        csv_data = self._run_oc(cmd, timeout=180)
        if not csv_data or 'items' not in csv_data:
            return []

        operators = []
        for csv in csv_data['items']:
            op_info = {
                'name': csv['metadata']['name'],
                'namespace': csv['metadata']['namespace'],
                'display_name': csv['spec'].get('displayName', csv['metadata']['name']),
                'version': csv['spec'].get('version'),
                'phase': csv['status'].get('phase', 'Unknown'),
                'reason': csv['status'].get('reason'),
                'created': csv['metadata'].get('creationTimestamp'),
            }

            # Check if it's a CP4I operator
            display_name = op_info['display_name'].lower()
            op_info['is_cp4i'] = any(
                keyword in display_name
                for keyword in ['cp4i', 'integration', 'navigator', 'event streams', 'event processing',
                                'api connect', 'app connect', 'mq', 'aspera', 'datapower']
            )

            operators.append(op_info)

        return operators

    def collect_pods(self, namespace: Optional[str] = None, label_selector: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Collect pod information

        Args:
            namespace: Optional namespace filter
            label_selector: Optional label selector (e.g., "app=myapp")
        """
        print(f"Collecting pods{' in namespace: ' + namespace if namespace else ''}...")

        cmd = ["get", "pods"]
        if namespace:
            cmd.extend(["-n", namespace])
        else:
            cmd.append("--all-namespaces")

        if label_selector:
            cmd.extend(["-l", label_selector])

        pod_data = self._run_oc(cmd)
        if not pod_data or 'items' not in pod_data:
            return []

        pods = []
        for pod in pod_data['items']:
            pod_info = {
                'name': pod['metadata']['name'],
                'namespace': pod['metadata']['namespace'],
                'phase': pod['status'].get('phase', 'Unknown'),
                'ready': self._count_ready_containers(pod),
                'restarts': self._count_restarts(pod),
                'age': pod['metadata'].get('creationTimestamp'),
                'node': pod['spec'].get('nodeName'),
                'labels': pod['metadata'].get('labels', {}),
                'annotations': pod['metadata'].get('annotations', {}),
                'resources': self._get_pod_resources(pod),
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
        """Count total restarts across all containers in a pod"""
        container_statuses = pod['status'].get('containerStatuses', [])
        return sum(c.get('restartCount', 0) for c in container_statuses)

    def _get_pod_resources(self, pod: Dict) -> Dict[str, Any]:
        """Extract resource requests and limits from pod"""
        containers = pod['spec'].get('containers', [])

        total_cpu_requests = 0
        total_cpu_limits = 0
        total_memory_requests = 0
        total_memory_limits = 0

        for container in containers:
            resources = container.get('resources', {})
            requests = resources.get('requests', {})
            limits = resources.get('limits', {})

            # Parse CPU (can be in cores like "1" or millicores like "500m")
            cpu_request = self._parse_cpu(requests.get('cpu', '0'))
            cpu_limit = self._parse_cpu(limits.get('cpu', '0'))

            # Parse memory (can be in various units: Gi, Mi, Ki, bytes)
            mem_request = self._parse_memory(requests.get('memory', '0'))
            mem_limit = self._parse_memory(limits.get('memory', '0'))

            total_cpu_requests += cpu_request
            total_cpu_limits += cpu_limit
            total_memory_requests += mem_request
            total_memory_limits += mem_limit

        return {
            'cpu_requests': total_cpu_requests,  # in cores
            'cpu_limits': total_cpu_limits,      # in cores
            'memory_requests': total_memory_requests,  # in bytes
            'memory_limits': total_memory_limits,      # in bytes
        }

    def _parse_cpu(self, cpu_str: str) -> float:
        """Parse CPU string to cores (float)"""
        if not cpu_str or cpu_str == '0':
            return 0.0

        cpu_str = str(cpu_str).strip()

        if cpu_str.endswith('m'):
            # Millicores: 500m = 0.5 cores
            return float(cpu_str[:-1]) / 1000.0
        else:
            # Cores: 2 = 2.0 cores
            return float(cpu_str)

    def _parse_memory(self, mem_str: str) -> int:
        """Parse memory string to bytes (int)"""
        if not mem_str or mem_str == '0':
            return 0

        mem_str = str(mem_str).strip()

        units = {
            'Ki': 1024,
            'Mi': 1024 ** 2,
            'Gi': 1024 ** 3,
            'Ti': 1024 ** 4,
            'K': 1000,
            'M': 1000 ** 2,
            'G': 1000 ** 3,
            'T': 1000 ** 4,
        }

        for unit, multiplier in units.items():
            if mem_str.endswith(unit):
                return int(float(mem_str[:-len(unit)]) * multiplier)

        # No unit, assume bytes
        return int(mem_str)

    def collect_routes(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Collect routes for deep linking"""
        print(f"Collecting routes{' in namespace: ' + namespace if namespace else ''}...")

        cmd = ["get", "routes"]
        if namespace:
            cmd.extend(["-n", namespace])
        else:
            cmd.append("--all-namespaces")

        route_data = self._run_oc(cmd)
        if not route_data or 'items' not in route_data:
            return []

        routes = []
        for route in route_data['items']:
            route_info = {
                'name': route['metadata']['name'],
                'namespace': route['metadata']['namespace'],
                'host': route['spec'].get('host'),
                'path': route['spec'].get('path', '/'),
                'tls': 'tls' in route['spec'],
                'service': route['spec'].get('to', {}).get('name'),
            }

            # Build full URL
            protocol = 'https' if route_info['tls'] else 'http'
            route_info['url'] = f"{protocol}://{route_info['host']}{route_info['path']}"

            routes.append(route_info)

        return routes

    def collect_all(self) -> Dict[str, Any]:
        """
        Collect all OpenShift and CP4I data

        Returns comprehensive snapshot of cluster state
        """
        print("=" * 60)
        print("CP4I Chief Console - Data Collection")
        print("=" * 60)

        snapshot = {
            'metadata': {
                'collection_timestamp': datetime.now().isoformat(),
                'collector_version': '1.0.0',
            },
            'cluster': self.collect_cluster_info(),
            'nodes': self.collect_nodes(),
        }

        # Discover CP4I namespaces
        cp4i_namespaces = self.discover_cp4i_namespaces()
        snapshot['cp4i_namespaces'] = cp4i_namespaces

        # Collect all namespaces
        snapshot['namespaces'] = self.collect_namespaces()

        # Collect operators (focus on CP4I namespaces if found)
        all_operators = self.collect_operators()
        snapshot['operators'] = {
            'all': all_operators,
            'cp4i': [op for op in all_operators if op.get('is_cp4i')],
        }

        # Collect pods from CP4I namespaces
        if cp4i_namespaces:
            cp4i_pods = []
            for ns in cp4i_namespaces:
                cp4i_pods.extend(self.collect_pods(namespace=ns))
            snapshot['pods'] = cp4i_pods
        else:
            # Collect sample from openshift-operators
            snapshot['pods'] = self.collect_pods(namespace="openshift-operators")

        # Collect routes from CP4I namespaces
        if cp4i_namespaces:
            cp4i_routes = []
            for ns in cp4i_namespaces:
                cp4i_routes.extend(self.collect_routes(namespace=ns))
            snapshot['routes'] = cp4i_routes
        else:
            snapshot['routes'] = []

        # Collect Kafka/Event Streams data (optional)
        try:
            from collector_kafka import KafkaCollector
            kafka_collector = KafkaCollector()
            kafka_data = kafka_collector.collect_all()
            snapshot['kafka'] = kafka_data.get('event_streams', {})
            # Merge warnings and errors
            self.warnings.extend(kafka_collector.warnings)
            self.errors.extend(kafka_collector.errors)
        except Exception as e:
            self.warnings.append(f"Kafka collection skipped: {e}")
            snapshot['kafka'] = None

        # Add errors and warnings
        snapshot['metadata']['errors'] = self.errors
        snapshot['metadata']['warnings'] = self.warnings

        print("=" * 60)
        print(f"Collection complete!")
        print(f"  CP4I namespaces found: {len(cp4i_namespaces)}")
        print(f"  Total operators: {len(all_operators)}")
        print(f"  CP4I operators: {len(snapshot['operators']['cp4i'])}")
        print(f"  Pods collected: {len(snapshot['pods'])}")
        print(f"  Routes collected: {len(snapshot['routes'])}")
        print(f"  Warnings: {len(self.warnings)}")
        print(f"  Errors: {len(self.errors)}")
        print("=" * 60)

        return snapshot


if __name__ == "__main__":
    # CLI usage
    collector = OCPCollector()
    snapshot = collector.collect_all()

    # Save to file
    from pathlib import Path
    output_dir = Path("output/snapshots")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = output_dir / f"snapshot-{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump(snapshot, f, indent=2)

    print(f"\nSnapshot saved to: {output_file}")

    # Print summary
    if snapshot['metadata']['warnings']:
        print("\nWarnings:")
        for warning in snapshot['metadata']['warnings']:
            print(f"  - {warning}")

    if snapshot['metadata']['errors']:
        print("\nErrors:")
        for error in snapshot['metadata']['errors']:
            print(f"  - {error}")
