"""
Resource Categorizer

Categorizes OpenShift/CP4I resources for licensing, criticality, and workload identification.
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional


class ResourceCategorizer:
    """Categorizes resources based on configuration"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize categorizer with configuration

        Args:
            config_path: Path to resource_categories.yaml (optional)
        """
        if config_path is None:
            # Default to ../resource_categories.yaml
            config_path = Path(__file__).parent.parent / 'resource_categories.yaml'

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def _matches_pattern(self, name: str, patterns: List[str]) -> bool:
        """Check if name matches any pattern"""
        if not name or not patterns:
            return False

        for pattern in patterns:
            try:
                if re.match(pattern, name, re.IGNORECASE):
                    return True
            except (re.error, TypeError):
                continue
        return False

    def _matches_labels(self, pod_labels: Dict[str, str], config_labels: Dict[str, List[str]]) -> bool:
        """Check if pod labels match configuration labels"""
        if not pod_labels or not config_labels:
            return False

        for key, values in config_labels.items():
            pod_value = pod_labels.get(key)
            if pod_value and pod_value in values:
                return True
        return False

    def categorize_licensing(self, pod: Dict[str, Any]) -> str:
        """
        Determine licensing category for a pod

        Returns: 'cp4i_licensed', 'openshift_platform', or 'free'
        """
        name = pod.get('name', '')
        namespace = pod.get('namespace', '')
        labels = pod.get('labels', {})

        # Check CP4I licensed patterns
        cp4i_config = self.config['licensing']['cp4i_licensed']
        if self._matches_pattern(name, cp4i_config['patterns']):
            return 'cp4i_licensed'

        # Check OpenShift platform
        platform_config = self.config['licensing']['openshift_platform']
        if self._matches_pattern(name, platform_config['patterns']):
            return 'openshift_platform'

        if any(re.match(pattern, namespace) for pattern in platform_config.get('namespaces', [])):
            return 'openshift_platform'

        # Check free/open source
        free_config = self.config['licensing']['free']
        if self._matches_pattern(name, free_config['patterns']):
            return 'free'

        # Default to free
        return 'free'

    def categorize_criticality(self, pod: Dict[str, Any]) -> str:
        """
        Determine criticality tier for a pod

        Returns: 'critical', 'important', or 'optional'
        """
        name = pod.get('name', '')
        namespace = pod.get('namespace', '')
        labels = pod.get('labels', {})

        # Check critical
        critical_config = self.config['criticality']['critical']
        if self._matches_pattern(name, critical_config.get('patterns', [])):
            return 'critical'
        if self._matches_pattern(name, critical_config.get('pod_patterns', [])):
            return 'critical'
        if any(re.match(pattern, namespace) for pattern in critical_config.get('namespaces', [])):
            return 'critical'

        # Check important
        important_config = self.config['criticality']['important']
        if self._matches_pattern(name, important_config.get('patterns', [])):
            return 'important'
        if any(re.match(pattern, namespace) for pattern in important_config.get('namespaces', [])):
            return 'important'
        if self._matches_labels(labels, important_config.get('labels', {})):
            return 'important'

        # Check optional
        optional_config = self.config['criticality']['optional']
        if self._matches_pattern(name, optional_config.get('patterns', [])):
            return 'optional'
        if any(re.match(pattern, namespace) for pattern in optional_config.get('namespaces', [])):
            return 'optional'
        if self._matches_labels(labels, optional_config.get('labels', {})):
            return 'optional'

        # Default to important
        return 'important'

    def is_business_workload(self, pod: Dict[str, Any]) -> bool:
        """
        Determine if pod is a business workload (vs infrastructure)

        Returns: True if business workload, False if infrastructure
        """
        name = pod.get('name', '')
        namespace = pod.get('namespace', '')
        labels = pod.get('labels', {})

        workload_config = self.config['workloads']

        # Check if it's infrastructure first (excludes)
        infra_patterns = workload_config.get('infrastructure_patterns', [])
        if self._matches_pattern(name, infra_patterns):
            return False

        infra_namespaces = workload_config.get('infrastructure_namespaces', [])
        if any(re.match(pattern, namespace) for pattern in infra_namespaces):
            return False

        # Check if it matches business workload patterns (includes)
        workload_patterns = workload_config.get('business_workload_patterns', [])
        if self._matches_pattern(name, workload_patterns):
            return True

        # Check labels
        workload_labels = workload_config.get('business_workload_labels', {})
        if self._matches_labels(labels, workload_labels):
            return True

        # Default to False (not a business workload)
        return False

    def calculate_vpc(self, pod: Dict[str, Any]) -> float:
        """
        Calculate VPC (Virtual Processor Core) contribution for a pod

        Returns: CPU cores allocated to CP4I licensed components
        """
        # Only count if it's CP4I licensed
        if self.categorize_licensing(pod) != 'cp4i_licensed':
            return 0.0

        resources = pod.get('resources', {})
        cpu_requests = resources.get('cpu_requests', 0.0)

        return cpu_requests

    def analyze_resource_efficiency(self, pod: Dict[str, Any]) -> Dict[str, str]:
        """
        Analyze resource efficiency (over/under/efficient)

        Returns: {'cpu': 'efficient', 'memory': 'over_provisioned'}
        """
        resources = pod.get('resources', {})
        thresholds = self.config.get('resource_thresholds', {})

        # For now, we only have requests (not actual usage)
        # So we'll mark everything as 'unknown' until we integrate metrics
        return {
            'cpu': 'unknown',
            'memory': 'unknown',
            'note': 'Need actual usage metrics for efficiency analysis'
        }

    def categorize_pod(self, pod: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fully categorize a pod

        Returns: Dict with all categorization details
        """
        return {
            'name': pod.get('name'),
            'namespace': pod.get('namespace'),
            'licensing': self.categorize_licensing(pod),
            'criticality': self.categorize_criticality(pod),
            'is_workload': self.is_business_workload(pod),
            'vpc_contribution': self.calculate_vpc(pod),
            'resources': pod.get('resources', {}),
            'efficiency': self.analyze_resource_efficiency(pod),
        }

    def generate_summary(self, pods: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics across all pods

        Returns: Summary with licensing costs, workload counts, etc.
        """
        categorized = [self.categorize_pod(pod) for pod in pods]

        # Licensing breakdown
        licensing_counts = {}
        total_vpc = 0.0
        for cat in categorized:
            lic_type = cat['licensing']
            licensing_counts[lic_type] = licensing_counts.get(lic_type, 0) + 1
            total_vpc += cat['vpc_contribution']

        # Criticality breakdown
        criticality_counts = {}
        for cat in categorized:
            crit = cat['criticality']
            criticality_counts[crit] = criticality_counts.get(crit, 0) + 1

        # Workload counts
        workload_count = sum(1 for cat in categorized if cat['is_workload'])
        infrastructure_count = len(categorized) - workload_count

        # Resource totals
        total_cpu_requests = sum(c['resources'].get('cpu_requests', 0) for c in categorized)
        total_memory_requests = sum(c['resources'].get('memory_requests', 0) for c in categorized)

        return {
            'total_pods': len(categorized),
            'licensing': {
                'breakdown': licensing_counts,
                'total_vpc': round(total_vpc, 2),
            },
            'criticality': {
                'breakdown': criticality_counts,
            },
            'workloads': {
                'business_workloads': workload_count,
                'infrastructure': infrastructure_count,
            },
            'resources': {
                'total_cpu_requests_cores': round(total_cpu_requests, 2),
                'total_memory_requests_gb': round(total_memory_requests / (1024 ** 3), 2),
            },
            'categorized_pods': categorized,
        }
