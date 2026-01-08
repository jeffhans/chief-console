"""
Cluster Utilities for CP4I Mission Console
Handles cluster detection and identification
"""

import subprocess
import re
from typing import Optional


def get_current_cluster() -> Optional[str]:
    """
    Get the current OpenShift cluster identifier

    Returns:
        Cluster identifier (sanitized server URL) or None if not logged in

    Example:
        'api.cluster-abc123.example.com:6443' -> 'cluster-abc123.example.com'
    """
    try:
        # Get server URL from oc
        result = subprocess.run(
            ['oc', 'whoami', '--show-server'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return None

        server_url = result.stdout.strip()

        # Extract cluster identifier from URL
        # Examples:
        #   https://api.cluster-abc123.example.com:6443 -> cluster-abc123.example.com
        #   https://console-openshift-console.apps.cluster.example.com -> cluster.example.com

        # Remove protocol
        server_url = server_url.replace('https://', '').replace('http://', '')

        # Remove port
        server_url = server_url.split(':')[0]

        # Remove 'api.' prefix if present
        if server_url.startswith('api.'):
            server_url = server_url[4:]

        # Sanitize for filesystem (replace invalid chars)
        cluster_id = re.sub(r'[^\w\-\.]', '_', server_url)

        return cluster_id

    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return None


def get_cluster_info() -> dict:
    """
    Get detailed cluster information

    Returns:
        Dictionary with cluster details
    """
    info = {
        'cluster_id': None,
        'server': None,
        'user': None,
        'logged_in': False,
    }

    try:
        # Get cluster ID
        cluster_id = get_current_cluster()
        if cluster_id:
            info['cluster_id'] = cluster_id
            info['logged_in'] = True

        # Get server URL
        result = subprocess.run(
            ['oc', 'whoami', '--show-server'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            info['server'] = result.stdout.strip()

        # Get current user
        result = subprocess.run(
            ['oc', 'whoami'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            info['user'] = result.stdout.strip()

    except Exception:
        pass

    return info


def format_cluster_name(cluster_id: str) -> str:
    """
    Format cluster ID for display

    Args:
        cluster_id: Cluster identifier

    Returns:
        Human-readable cluster name
    """
    # Try to extract just the meaningful part
    # cluster-abc123.example.com -> cluster-abc123
    parts = cluster_id.split('.')
    if len(parts) > 0:
        return parts[0]
    return cluster_id
