"""
HTML Dashboard Renderer for CP4I Chief Console

Generates a self-contained HTML dashboard from cluster snapshots.
Implements "Meaningful Waves" design with graceful degradation.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class DashboardRenderer:
    """Renders Chief Console dashboard from snapshot data"""

    def __init__(self, snapshot: Dict[str, Any], diff: Optional[Dict[str, Any]] = None):
        self.snapshot = snapshot
        self.diff = diff
        self.metadata = snapshot.get('metadata') or {}
        self.cluster = snapshot.get('cluster') or {}
        self.nodes = snapshot.get('nodes', [])
        self.namespaces = snapshot.get('namespaces', [])
        self.operators = snapshot.get('operators', {})
        self.pods = snapshot.get('pods', [])
        self.routes = snapshot.get('routes', [])
        self.cp4i_namespaces = snapshot.get('cp4i_namespaces', [])
        self.demo_metadata = self._load_demo_metadata()
        self.cluster_alias = self.cluster.get('alias') or self.metadata.get('cluster_alias')
        self.cluster_alias_id = self.cluster.get('alias_id') or self.metadata.get('cluster_alias_id')
        self.cluster_display = (
            self.cluster.get('display_name')
            or "CP4I Chief Console"
        )
        self.cluster_id = self.cluster.get('id') or self.metadata.get('cluster_id')

        # Initialize resource categorizer and generate summary
        try:
            from resource_categorizer import ResourceCategorizer
            self.categorizer = ResourceCategorizer()
            self.resource_summary = self.categorizer.generate_summary(self.pods)
        except Exception as e:
            print(f"Warning: Could not initialize resource categorizer: {e}")
            self.categorizer = None
            self.resource_summary = None

    def _load_demo_metadata(self) -> Dict[str, Any]:
        """Load demo metadata configuration if available"""
        import yaml
        import re
        from pathlib import Path

        metadata_file = Path(__file__).parent.parent / 'demo_metadata.yaml'
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: Could not load demo metadata: {e}")
        return {}

    def _get_display_name(self, resource_type: str, resource_name: str, technical_name: str = None) -> str:
        """Get display name from metadata, fallback to technical name"""
        import re

        if not self.demo_metadata:
            return technical_name or resource_name

        # Get metadata for this resource type
        type_metadata = self.demo_metadata.get(resource_type, {})

        # Try exact match first
        if resource_name in type_metadata:
            display_name = type_metadata[resource_name].get('display_name')
            if display_name:
                return display_name

        # Try regex patterns (for dynamic names)
        for pattern, meta in type_metadata.items():
            if '.*' in pattern or '[' in pattern:  # Looks like a regex
                try:
                    if re.match(pattern, resource_name):
                        display_name = meta.get('display_name')
                        if display_name:
                            return display_name
                except:
                    pass

        return technical_name or resource_name

    def _get_metadata(self, resource_type: str, resource_name: str) -> Dict[str, Any]:
        """Get full metadata for a resource"""
        import re

        if not self.demo_metadata:
            return {}

        type_metadata = self.demo_metadata.get(resource_type, {})

        # Try exact match first
        if resource_name in type_metadata:
            return type_metadata[resource_name]

        # Try regex patterns
        for pattern, meta in type_metadata.items():
            if '.*' in pattern or '[' in pattern:
                try:
                    if re.match(pattern, resource_name):
                        return meta
                except:
                    pass

        return {}

    def render(self) -> str:
        """Generate complete HTML dashboard"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CP4I Chief Console</title>
    {self._render_styles()}
</head>
<body>
    <div class="container">
        {self._render_header()}
        {self._render_wave1_executive()}
        {self._render_wave2_cp4i()}
        {self._render_wave4_demo_artifacts()}
        {self._render_wave5_licensing()}
        {self._render_wave6_workload_health()}
        {self._render_wave7_criticality()}
        {self._render_wave8_resource_utilization()}
        {self._render_wave3_infrastructure()}
        {self._render_footer()}
    </div>
    {self._render_scripts()}
</body>
</html>"""

    def _render_styles(self) -> str:
        """Embedded CSS styles"""
        return """<style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f4f4f4;
            color: #161616;
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: linear-gradient(135deg, #0f62fe 0%, #001d6c 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        .header .subtitle {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .header .subtitle-name {
            font-weight: 700;
            color: #c6e2ff;
            font-size: 1.2rem;
        }

        .wave {
            background: white;
            border-radius: 8px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .wave-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e0e0e0;
        }

        .wave-title {
            font-size: 1.8rem;
            font-weight: 600;
        }

        .wave-number {
            background: #0f62fe;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .metric-card {
            background: #f4f4f4;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #0f62fe;
        }

        .metric-label {
            font-size: 0.9rem;
            color: #525252;
            margin-bottom: 8px;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 600;
            color: #161616;
        }

        .metric-sublabel {
            font-size: 0.85rem;
            color: #8d8d8d;
            margin-top: 5px;
        }

        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 500;
        }

        .status-green {
            background: #defbe6;
            color: #0e6027;
        }

        .status-yellow {
            background: #fef7dd;
            color: #8e6a00;
        }

        .status-red {
            background: #ffe0e0;
            color: #a2191f;
        }

        .status-gray {
            background: #e0e0e0;
            color: #525252;
        }

        .info-box {
            background: #e8f4ff;
            border-left: 4px solid #0f62fe;
            padding: 15px 20px;
            border-radius: 4px;
            margin-bottom: 20px;
        }

        .warning-box {
            background: #fef7dd;
            border-left: 4px solid #f1c21b;
            padding: 15px 20px;
            border-radius: 4px;
            margin-bottom: 20px;
        }

        .table-container {
            overflow-x: auto;
            margin-top: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }

        th {
            background: #f4f4f4;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #e0e0e0;
        }

        td {
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }

        tr:hover {
            background: #f9f9f9;
        }

        .footer {
            text-align: center;
            padding: 20px;
            color: #8d8d8d;
            font-size: 0.9rem;
        }

        .refresh-time {
            display: inline-block;
            background: #e0e0e0;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 0.85rem;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #8d8d8d;
        }

        .empty-state-icon {
            font-size: 4rem;
            margin-bottom: 20px;
            opacity: 0.3;
        }
    </style>"""

    def _render_scripts(self) -> str:
        """Embedded JavaScript"""
        return """<script>
        // Auto-refresh functionality (if enabled)
        function refreshDashboard() {
            window.location.reload();
        }

        // Format timestamps
        function formatTimestamp(isoString) {
            const date = new Date(isoString);
            return date.toLocaleString();
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            console.log('CP4I Chief Console Dashboard Loaded');
        });
    </script>"""

    def _render_header(self) -> str:
        """Render dashboard header"""
        cluster_version = self.cluster.get('version') or 'Unknown'
        collection_time = self.metadata.get('collection_timestamp', '')
        subtitle_lines = [
            f"<span class='subtitle-name'>Name: {self.cluster_alias}</span>" if self.cluster_alias else None,
            f"ID: {self.cluster_alias_id}" if self.cluster_alias_id else None,
            f"OpenShift {cluster_version}",
            f"Last updated: {self._format_timestamp(collection_time)}" if collection_time else None,
            f"Cluster ID: {self.cluster_id}" if self.cluster_id else None,
        ]
        subtitle_html = "<br>".join([line for line in subtitle_lines if line])

        return f"""<div class="header">
        <h1>CP4I Chief Console</h1>
        <div class="subtitle">
            {subtitle_html}
        </div>
    </div>"""

    def _render_wave1_executive(self) -> str:
        """Wave 1: Executive Summary"""
        overall_status = self._determine_overall_status()
        cp4i_installed = len(self.operators.get('cp4i', [])) > 0

        return f"""<div class="wave">
        <div class="wave-header">
            <div class="wave-title">Executive Summary</div>
            <div class="wave-number">1</div>
        </div>

        <div class="metric-grid">
            {self._render_status_card(overall_status)}
            {self._render_cp4i_status_card(cp4i_installed)}
            {self._render_capacity_card()}
            {self._render_health_card()}
        </div>

        {self._render_cp4i_installation_notice(cp4i_installed)}
        {self._render_quick_links()}
        {self._render_changes() if self.diff else ""}
    </div>"""

    def _render_status_card(self, status: Dict[str, Any]) -> str:
        """Render overall status card"""
        return f"""<div class="metric-card">
        <div class="metric-label">Overall Status</div>
        <div class="metric-value">
            <span class="status-badge status-{status['color']}">{status['text']}</span>
        </div>
        <div class="metric-sublabel">{status['reason']}</div>
    </div>"""

    def _render_cp4i_status_card(self, installed: bool) -> str:
        """Render CP4I status card"""
        cp4i_ops = self.operators.get('cp4i', [])

        # Count unique operators (deduplicate by name+version)
        unique_ops = {}
        for op in cp4i_ops:
            key = (op.get('display_name'), op.get('version'))
            unique_ops[key] = op

        unique_count = len(unique_ops)
        total_count = len(cp4i_ops)

        status_class = 'green' if installed else 'yellow'

        if installed and unique_count > 0:
            if unique_count == total_count:
                status_text = f"{unique_count} Capabilities"
            else:
                status_text = f"{unique_count} Capabilities"
        else:
            status_text = "Not Installed"

        return f"""<div class="metric-card">
        <div class="metric-label">CP4I Status</div>
        <div class="metric-value">
            <span class="status-badge status-{status_class}">{status_text}</span>
        </div>
        <div class="metric-sublabel">{len(self.cp4i_namespaces)} namespaces</div>
    </div>"""

    def _render_capacity_card(self) -> str:
        """Render cluster capacity card"""
        node_count = len(self.nodes)
        ready_nodes = sum(1 for n in self.nodes if n.get('status') == 'Ready')

        return f"""<div class="metric-card">
        <div class="metric-label">Cluster Capacity</div>
        <div class="metric-value">{ready_nodes}/{node_count}</div>
        <div class="metric-sublabel">Nodes Ready</div>
    </div>"""

    def _render_health_card(self) -> str:
        """Render health indicators card"""
        error_count = len(self.metadata.get('errors', []))
        warning_count = len(self.metadata.get('warnings', []))

        status_class = 'green' if error_count == 0 else 'red'

        return f"""<div class="metric-card">
        <div class="metric-label">Health Indicators</div>
        <div class="metric-value">
            <span class="status-badge status-{status_class}">
                {error_count} Errors
            </span>
        </div>
        <div class="metric-sublabel">{warning_count} warnings</div>
    </div>"""

    def _render_cp4i_installation_notice(self, installed: bool) -> str:
        """Render CP4I installation notice if not installed"""
        if installed:
            return ""

        return """<div class="warning-box">
        <strong>⚠️ CP4I Not Detected</strong><br>
        No Cloud Pak for Integration capabilities found. This appears to be a fresh OpenShift cluster.
        The dashboard will automatically discover CP4I components as they are installed.
    </div>"""

    def _render_quick_links(self) -> str:
        """Render quick links section"""
        console_url = self.cluster.get('console_url', '#')
        api_url = self.cluster.get('api_url', '#')

        return f"""<div class="info-box">
        <strong>Quick Links:</strong><br>
        • <a href="{console_url}" target="_blank">OpenShift Console</a><br>
        • API: <code>{api_url}</code>
    </div>"""

    def _generate_console_link(self, resource_type: str, name: str, namespace: Optional[str] = None) -> str:
        """Generate deep link to OpenShift Console for a resource"""
        console_url = self.cluster.get('console_url', '')
        if not console_url:
            return '#'

        # Remove trailing slash
        console_url = console_url.rstrip('/')

        # Resource type specific URL patterns
        if resource_type == 'pod':
            return f"{console_url}/k8s/ns/{namespace}/pods/{name}" if namespace else '#'
        elif resource_type == 'operator':
            # Operators/CSVs
            return f"{console_url}/k8s/ns/{namespace}/operators.coreos.com~v1alpha1~ClusterServiceVersion/{name}" if namespace else '#'
        elif resource_type == 'namespace':
            return f"{console_url}/k8s/cluster/projects/{name}"
        elif resource_type == 'route':
            return f"{console_url}/k8s/ns/{namespace}/routes/{name}" if namespace else '#'
        elif resource_type == 'kafka_topic':
            return f"{console_url}/k8s/ns/{namespace}/kafkatopics.eventstreams.ibm.com~v1beta2~KafkaTopic/{name}" if namespace else '#'
        elif resource_type == 'event_streams':
            return f"{console_url}/k8s/ns/{namespace}/eventstreams.eventstreams.ibm.com~v1beta2~EventStreams/{name}" if namespace else '#'
        elif resource_type == 'node':
            return f"{console_url}/k8s/cluster/nodes/{name}"
        else:
            # Generic k8s resource
            return f"{console_url}/k8s/ns/{namespace}/core~v1~{resource_type.capitalize()}/{name}" if namespace else '#'

    def _render_changes(self) -> str:
        """Render hierarchical changes section with deep links to CP4I dashboards"""
        if not self.diff:
            return ""

        metadata = self.diff.get('metadata', {})
        changes = self.diff.get('changes', {})
        summary = self.diff.get('summary', {})

        # Check if there are any meaningful changes
        total_changes = (len(changes.get('critical', [])) +
                        len(changes.get('important', [])) +
                        len(changes.get('informational', [])))

        if total_changes == 0:
            return """<div class="info-box" style="margin-top: 20px;">
        <strong>📊 No significant changes</strong> detected since last collection ({}).
    </div>""".format(metadata.get('time_elapsed', 'unknown time'))

        # Build changes HTML with hierarchical organization
        changes_html = f"""<div style="margin-top: 30px; padding: 20px; background: #fff; border-radius: 8px; border-left: 4px solid #0f62fe;">
        <h3 style="margin-bottom: 15px; color: #0f62fe;">🔄 What Changed (Last {metadata.get('time_elapsed', 'unknown')})</h3>"""

        # Critical changes - grouped by type
        if changes.get('critical'):
            changes_html += """
        <div style="margin: 15px 0;">
            <strong style="color: #da1e28; font-size: 1.1rem;">🔴 CRITICAL</strong>"""

            # Group by type
            grouped = self._group_changes_by_type(changes['critical'])
            for change_type, items in grouped.items():
                changes_html += f"""
            <div style="margin: 10px 0 10px 20px;">
                <strong style="color: #525252;">{change_type.replace('_', ' ').title()}s</strong>
                <ul style="margin: 5px 0; padding-left: 20px; list-style-type: circle;">"""
                for change in items[:10]:  # Limit per type
                    changes_html += self._format_change_with_link(change)
                changes_html += "</ul></div>"

            changes_html += "</div>"

        # Important changes - grouped hierarchically by namespace
        if changes.get('important'):
            changes_html += """
        <div style="margin: 15px 0;">
            <strong style="color: #f1c21b; font-size: 1.1rem;">🟡 IMPORTANT</strong>"""

            # Group by namespace, then by type
            by_namespace = self._group_changes_by_namespace(changes['important'])

            for ns, ns_changes in list(by_namespace.items())[:15]:  # Limit namespaces
                ns_link = self._generate_console_link('namespace', ns)
                changes_html += f"""
            <div style="margin: 10px 0 10px 20px;">
                <strong style="color: #0f62fe;">
                    📁 {ns} <a href="{ns_link}" target="_blank" style="font-size: 0.8rem; color: #0f62fe;">[View Namespace]</a>
                </strong>"""

                # Group by type within namespace
                grouped = self._group_changes_by_type(ns_changes)
                for change_type, items in grouped.items():
                    changes_html += f"""
                <div style="margin: 5px 0 5px 20px;">
                    <span style="color: #525252; font-size: 0.9rem;">{change_type.replace('_', ' ').title()}s</span>
                    <ul style="margin: 5px 0; padding-left: 20px; list-style-type: square;">"""
                    for change in items[:5]:  # Limit per type
                        changes_html += self._format_change_with_link(change)
                    changes_html += "</ul></div>"

                changes_html += "</div>"

            changes_html += "</div>"

        # Informational changes - summarized
        if changes.get('informational'):
            info_count = len(changes['informational'])
            changes_html += f"""
        <div style="margin: 15px 0;">
            <strong style="color: #0f62fe; font-size: 1.0rem;">ℹ️ INFORMATIONAL</strong>
            <div style="margin: 10px 0 10px 20px; color: #525252;">
                {info_count} additional informational change{'s' if info_count != 1 else ''} detected
            </div>
        </div>"""

        # Summary stats
        if summary.get('change_counts'):
            counts = summary['change_counts']
            changes_html += f"""
        <div style="margin-top: 20px; padding: 15px; background: #f4f4f4; border-radius: 4px; font-size: 0.9rem;">
            <strong>📊 Summary:</strong><br>
            <span style="margin-left: 10px;">
                ✅ {counts['additions']} additions &nbsp;
                🔄 {counts['modifications']} modifications &nbsp;
                ❌ {counts['deletions']} deletions
            </span>
        </div>"""

        changes_html += "</div>"

        return changes_html

    def _group_changes_by_type(self, changes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group changes by resource type"""
        grouped = {}
        for change in changes:
            change_type = change.get('type', 'unknown')
            if change_type not in grouped:
                grouped[change_type] = []
            grouped[change_type].append(change)
        return grouped

    def _group_changes_by_namespace(self, changes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group changes by namespace"""
        grouped = {}
        for change in changes:
            namespace = change.get('namespace', 'cluster-wide')
            if namespace not in grouped:
                grouped[namespace] = []
            grouped[namespace].append(change)
        return grouped

    def _format_change(self, change: Dict[str, Any]) -> str:
        """Format a single change for display (legacy method without links)"""
        change_type = change.get('type', 'unknown')
        action = change.get('action', 'changed')
        name = change.get('name', 'Unknown')

        if change_type == 'operator' and action == 'added':
            return f"<li>✅ New operator: <strong>{name}</strong> v{change.get('version', 'N/A')} in {change.get('namespace')}</li>"

        elif change_type == 'event_streams':
            return f"<li>🎉 Event Streams: <strong>{name}</strong> - {change.get('status')}</li>"

        elif change_type == 'kafka_topic' and action == 'created':
            category = change.get('category', 'general')
            return f"<li>📊 New topic: <strong>{name}</strong> ({category}, {change.get('partitions')} partitions)</li>"

        elif change_type == 'pod' and action == 'restarted':
            return f"<li>🔄 Pod <strong>{name}</strong> restarted {change.get('restart_count')}x (total: {change.get('total_restarts')})</li>"

        elif change_type == 'pod' and action == 'created':
            return f"<li>➕ New pod: <strong>{name}</strong> in {change.get('namespace')} ({change.get('phase')})</li>"

        elif change_type == 'namespace' and action == 'created':
            return f"<li>📁 New namespace: <strong>{name}</strong></li>"

        elif change_type == 'route' and action == 'created':
            return f"<li>🌐 New route: <strong>{name}</strong> → {change.get('url')}</li>"

        else:
            return f"<li>{change_type}: <strong>{name}</strong> - {action}</li>"

    def _format_change_with_link(self, change: Dict[str, Any]) -> str:
        """Format a single change with deep links to CP4I dashboards"""
        change_type = change.get('type', 'unknown')
        action = change.get('action', 'changed')
        name = change.get('name', 'Unknown')
        namespace = change.get('namespace')

        # Generate console link
        console_link = self._generate_console_link(change_type, name, namespace)
        link_html = f'<a href="{console_link}" target="_blank" style="font-size: 0.75rem; color: #0f62fe; text-decoration: none;">[🔗 View]</a>'

        # Format based on type and action
        if change_type == 'operator':
            if action == 'added':
                return f"<li>✅ <strong>{name}</strong> v{change.get('version', 'N/A')} {link_html}</li>"
            elif action == 'status_changed':
                return f"<li>⚠️ <strong>{name}</strong>: {change.get('old_status')} → {change.get('new_status')} {link_html}</li>"
            else:
                return f"<li><strong>{name}</strong> - {action} {link_html}</li>"

        elif change_type == 'event_streams':
            if action == 'created':
                # Also add link to topics
                topics_link = f"{console_link.rsplit('/', 1)[0]}"  # Link to EventStreams list
                return f"<li>🎉 <strong>{name}</strong> - {change.get('status')} {link_html}</li>"
            else:
                return f"<li>🎉 <strong>{name}</strong> - {change.get('status')} {link_html}</li>"

        elif change_type == 'kafka_topic':
            category = change.get('category', 'general')
            partitions = change.get('partitions')
            if action == 'created':
                return f"<li>📊 <strong>{name}</strong> ({category}, {partitions} partition{'s' if partitions != 1 else ''}) {link_html}</li>"
            elif action == 'partitions_changed':
                return f"<li>📊 <strong>{name}</strong>: {change.get('old_partitions')} → {change.get('new_partitions')} partitions {link_html}</li>"
            else:
                return f"<li>📊 <strong>{name}</strong> - {action} {link_html}</li>"

        elif change_type == 'pod':
            if action == 'restarted':
                severity_icon = '🔴' if change.get('severity') == 'critical' else '🟡'
                return f"<li>{severity_icon} <strong>{name}</strong> restarted {change.get('restart_count')}x (total: {change.get('total_restarts')}) {link_html}</li>"
            elif action == 'created':
                return f"<li>➕ <strong>{name}</strong> ({change.get('phase')}) {link_html}</li>"
            elif action == 'phase_changed':
                return f"<li>🔄 <strong>{name}</strong>: {change.get('old_phase')} → {change.get('new_phase')} {link_html}</li>"
            elif action == 'deleted':
                return f"<li>❌ <strong>{name}</strong> deleted</li>"
            else:
                return f"<li><strong>{name}</strong> - {action} {link_html}</li>"

        elif change_type == 'namespace':
            if action == 'created':
                return f"<li>📁 <strong>{name}</strong> {link_html}</li>"
            elif action == 'deleted':
                return f"<li>❌ <strong>{name}</strong> deleted</li>"
            else:
                return f"<li>📁 <strong>{name}</strong> - {action} {link_html}</li>"

        elif change_type == 'route':
            if action == 'created':
                url = change.get('url', 'N/A')
                return f"<li>🌐 <strong>{name}</strong> → {url} {link_html}</li>"
            else:
                return f"<li>🌐 <strong>{name}</strong> - {action} {link_html}</li>"

        elif change_type == 'node':
            if action == 'status_changed':
                severity_icon = '🔴' if change.get('new_status') != 'Ready' else '🟢'
                return f"<li>{severity_icon} <strong>{name}</strong>: {change.get('old_status')} → {change.get('new_status')} {link_html}</li>"
            else:
                return f"<li><strong>{name}</strong> - {action} {link_html}</li>"

        else:
            # Generic format
            return f"<li>{change_type}: <strong>{name}</strong> - {action} {link_html}</li>"

    def _render_wave2_cp4i(self) -> str:
        """Wave 2: CP4I Workloads"""
        cp4i_operators = self.operators.get('cp4i', [])

        if not cp4i_operators:
            return self._render_empty_wave2()

        return f"""<div class="wave">
        <div class="wave-header">
            <div class="wave-title">CP4I Workloads</div>
            <div class="wave-number">2</div>
        </div>

        {self._render_operators_table(cp4i_operators)}
    </div>"""

    def _render_empty_wave2(self) -> str:
        """Render empty state for Wave 2"""
        return f"""<div class="wave">
        <div class="wave-header">
            <div class="wave-title">CP4I Workloads</div>
            <div class="wave-number">2</div>
        </div>

        <div class="empty-state">
            <div class="empty-state-icon">📦</div>
            <h3>No CP4I Workloads Found</h3>
            <p>Install Cloud Pak for Integration to see capabilities here.</p>
        </div>
    </div>"""

    def _render_wave4_demo_artifacts(self) -> str:
        """Wave 4: Demo Artifacts - Your Custom Deployments"""
        kafka_data = self.snapshot.get('kafka', {})

        return f"""<div class="wave">
        <div class="wave-header">
            <div class="wave-title">Demo Artifacts</div>
            <div class="wave-number">4</div>
        </div>

        <div class="info-box" style="margin-bottom: 20px;">
            <strong>🎯 Your Custom Deployments</strong><br>
            This section shows the unique applications, data streams, and integrations created in this environment.
            Use this as a starting point for demos and to understand relationships between components.
        </div>

        {self._render_demo_artifacts_hierarchy(kafka_data)}
    </div>"""

    def _render_demo_artifacts_hierarchy(self, kafka_data: Dict) -> str:
        """Render hierarchical view of demo artifacts grouped by namespace"""
        console_url = (self.cluster.get('console_url') or '').rstrip('/')

        # Group artifacts by CP4I namespace (exclude system namespaces)
        demo_namespaces = [ns for ns in self.cp4i_namespaces
                          if ns not in ['openshift-marketplace', 'ibm-common-services']]

        if not demo_namespaces:
            return """<div class="empty-state">
                <div class="empty-state-icon">🎯</div>
                <h3>No Demo Artifacts Found</h3>
                <p>Deploy custom applications to see them here.</p>
            </div>"""

        html = ""

        for namespace in demo_namespaces:
            # Get topology link
            topology_link = f"{console_url}/topology/ns/{namespace}" if console_url else "#"
            namespace_link = self._generate_console_link('namespace', namespace)

            # Gather artifacts in this namespace
            ns_pods = [p for p in self.pods if p.get('namespace') == namespace]
            ns_routes = [r for r in self.routes if r.get('namespace') == namespace]

            # Get Event Streams and topics for this namespace
            es_instances = [i for i in kafka_data.get('instances', [])
                           if i.get('namespace') == namespace]

            # Count artifacts
            artifact_count = len(ns_pods) + len(ns_routes) + len(es_instances)

            if artifact_count == 0:
                continue

            html += f"""
        <div style="margin: 20px 0; padding: 20px; background: #f9f9f9; border-left: 4px solid #0f62fe; border-radius: 4px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="margin: 0; color: #0f62fe;">📁 {namespace}</h3>
                <div>
                    <a href="{topology_link}" target="_blank" style="margin-right: 10px; padding: 6px 12px; background: #0f62fe; color: white; text-decoration: none; border-radius: 4px; font-size: 0.85rem;">
                        📊 View Topology
                    </a>
                    <a href="{namespace_link}" target="_blank" style="padding: 6px 12px; background: #525252; color: white; text-decoration: none; border-radius: 4px; font-size: 0.85rem;">
                        🔗 View Namespace
                    </a>
                </div>
            </div>"""

            # Event Streams Instances
            if es_instances:
                html += """
            <div style="margin: 15px 0 15px 20px;">
                <strong style="color: #525252; font-size: 1.0rem;">🎉 Event Streams</strong>
                <ul style="margin: 10px 0; padding-left: 20px;">"""

                for instance in es_instances:
                    es_name = instance.get('name')
                    status = instance.get('status', 'Unknown')
                    version = instance.get('version', 'N/A')

                    # Get display name and metadata
                    display_name = self._get_display_name('event_streams', es_name, es_name)
                    meta = self._get_metadata('event_streams', es_name)
                    description = meta.get('description', '')

                    # Find Event Streams UI route instead of OpenShift resource link
                    es_ui_route = None
                    for route in self.routes:
                        if route.get('namespace') == namespace and f"{es_name}-ibm-es-ui" in route.get('name', ''):
                            es_ui_route = route.get('url')
                            break

                    # Fallback to OpenShift resource link if no UI route found
                    es_link = es_ui_route if es_ui_route else self._generate_console_link('event_streams', es_name, namespace)
                    link_text = "🎯 Open UI" if es_ui_route else "🔗 View Config"

                    # Get topics for this instance
                    topics = kafka_data.get('topics', {}).get(es_name, [])

                    html += f"""<li style="margin: 8px 0;">
                        <strong>{display_name}</strong>"""

                    if display_name != es_name:
                        html += f""" <span style="color: #8d8d8d; font-size: 0.85rem;">({es_name})</span>"""

                    html += f""" (v{version}, {status})
                        <a href="{es_link}" target="_blank" style="margin-left: 8px; font-size: 0.75rem; color: #0f62fe; text-decoration: none;">[{link_text}]</a>"""

                    if description:
                        html += f"""<br><span style="color: #525252; font-size: 0.85rem; margin-left: 20px;">💡 {description}</span>"""

                    # Show topics grouped by category
                    if topics:
                        # Group topics by category
                        topics_by_category = {}
                        for topic in topics:
                            category = topic.get('category', 'general')
                            if category not in topics_by_category:
                                topics_by_category[category] = []
                            topics_by_category[category].append(topic)

                        html += """
                        <div style="margin: 10px 0 10px 20px;">
                            <span style="color: #525252; font-size: 0.9rem;">📊 Kafka Topics:</span>
                            <ul style="margin: 5px 0; padding-left: 20px;">"""

                        # Show in order: raw → enriched → curated → dlq → general
                        for category in ['raw', 'enriched', 'curated', 'dlq', 'general']:
                            if category in topics_by_category:
                                html += f"""<li style="margin: 5px 0; color: #525252;">
                                    <strong>{category.upper()}</strong>:"""

                                for topic in topics_by_category[category]:
                                    topic_name = topic.get('name')
                                    topic_link = self._generate_console_link('kafka_topic', topic_name, namespace)
                                    partitions = topic.get('partitions', 'N/A')

                                    # Get display name and metadata
                                    topic_display = self._get_display_name('topics', topic_name, topic_name)
                                    topic_meta = self._get_metadata('topics', topic_name)
                                    topic_desc = topic_meta.get('business_purpose', '')

                                    html += f"""
                                    <div style="margin-left: 20px;">
                                        • <strong>{topic_display}</strong>"""

                                    if topic_display != topic_name:
                                        html += f""" <span style="color: #8d8d8d; font-size: 0.75rem;">({topic_name})</span>"""

                                    html += f""" ({partitions} partitions)
                                        <a href="{topic_link}" target="_blank" style="margin-left: 8px; font-size: 0.7rem; color: #0f62fe; text-decoration: none;">[🔗 View]</a>"""

                                    if topic_desc:
                                        html += f"""<br><span style="color: #8d8d8d; font-size: 0.75rem; margin-left: 25px;">└ {topic_desc}</span>"""

                                    html += "</div>"

                                html += "</li>"

                        html += "</ul></div>"

                    html += "</li>"

                html += "</ul></div>"

            # Pods
            if ns_pods:
                # Filter for demo/custom pods (exclude operator pods)
                demo_pods = [p for p in ns_pods if not any(x in p.get('name', '').lower()
                            for x in ['operator', 'zookeeper', 'kafka-', 'strimzi'])]

                if demo_pods:
                    html += """
            <div style="margin: 15px 0 15px 20px;">
                <strong style="color: #525252; font-size: 1.0rem;">🚀 Applications</strong>
                <ul style="margin: 10px 0; padding-left: 20px;">"""

                    for pod in demo_pods:
                        pod_name = pod.get('name')
                        pod_link = self._generate_console_link('pod', pod_name, namespace)
                        phase = pod.get('phase', 'Unknown')
                        ready = pod.get('ready', 'N/A')

                        # Get display name and metadata
                        pod_display = self._get_display_name('applications', pod_name, pod_name)
                        pod_meta = self._get_metadata('applications', pod_name)
                        pod_desc = pod_meta.get('description', '')

                        phase_icon = '🟢' if phase == 'Running' else '🟡'

                        html += f"""<li style="margin: 5px 0;">
                            {phase_icon} <strong>{pod_display}</strong>"""

                        if pod_display != pod_name:
                            html += f""" <span style="color: #8d8d8d; font-size: 0.75rem;">({pod_name})</span>"""

                        html += f""" ({phase}, {ready} ready)
                            <a href="{pod_link}" target="_blank" style="margin-left: 8px; font-size: 0.75rem; color: #0f62fe; text-decoration: none;">[🔗 View]</a>"""

                        if pod_desc:
                            html += f"""<br><span style="color: #8d8d8d; font-size: 0.85rem; margin-left: 25px;">💡 {pod_desc}</span>"""

                        html += "</li>"

                    html += "</ul></div>"

            # Routes
            if ns_routes:
                html += """
            <div style="margin: 15px 0 15px 20px;">
                <strong style="color: #525252; font-size: 1.0rem;">🌐 Routes</strong>
                <ul style="margin: 10px 0; padding-left: 20px;">"""

                for route in ns_routes:
                    route_name = route.get('name')
                    route_link = self._generate_console_link('route', route_name, namespace)
                    url = route.get('url', 'N/A')

                    # Get display name and metadata
                    route_display = self._get_display_name('routes', route_name, route_name)
                    route_meta = self._get_metadata('routes', route_name)
                    route_desc = route_meta.get('description', '')

                    html += f"""<li style="margin: 5px 0;">
                        <strong>{route_display}</strong>"""

                    if route_display != route_name:
                        html += f""" <span style="color: #8d8d8d; font-size: 0.75rem;">({route_name})</span>"""

                    html += f""" → <a href="{url}" target="_blank" style="color: #0f62fe;">{url}</a>
                        <a href="{route_link}" target="_blank" style="margin-left: 8px; font-size: 0.75rem; color: #0f62fe; text-decoration: none;">[🔗 Config]</a>"""

                    if route_desc:
                        html += f"""<br><span style="color: #8d8d8d; font-size: 0.85rem; margin-left: 25px;">💡 {route_desc}</span>"""

                    html += "</li>"

                html += "</ul></div>"

            html += "</div>"

        return html

    def _render_wave5_licensing(self) -> str:
        """Wave 5: Licensing Cost Map"""
        if not self.resource_summary:
            return ""

        licensing = self.resource_summary.get('licensing', {})
        breakdown = licensing.get('breakdown', {})
        total_vpc = licensing.get('total_vpc', 0)

        cp4i_count = breakdown.get('cp4i_licensed', 0)
        platform_count = breakdown.get('openshift_platform', 0)
        free_count = breakdown.get('free', 0)

        # Get CP4I licensed pods for detail view
        categorized = self.resource_summary.get('categorized_pods', [])
        cp4i_pods = [p for p in categorized if p['licensing'] == 'cp4i_licensed']

        return f"""<div class="wave">
        <div class="wave-header">
            <div class="wave-title">💰 Licensing Cost Map</div>
            <div class="wave-number">5</div>
        </div>

        <div class="info-box" style="margin-bottom: 20px;">
            <strong>💡 License Consumption</strong><br>
            This view shows which components consume IBM/Red Hat licenses and estimated VPC (Virtual Processor Core) usage.
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px;">
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; border-radius: 4px;">
                <div style="font-size: 2rem; font-weight: bold; color: #856404;">{cp4i_count}</div>
                <div style="color: #856404; font-weight: 500;">CP4I Licensed Pods</div>
                <div style="font-size: 0.85rem; color: #856404; margin-top: 5px;">Consume VPC licenses</div>
            </div>

            <div style="background: #d4edda; border-left: 4px solid #28a745; padding: 20px; border-radius: 4px;">
                <div style="font-size: 2rem; font-weight: bold; color: #155724;">{total_vpc}</div>
                <div style="color: #155724; font-weight: 500;">Total VPC Allocated</div>
                <div style="font-size: 0.85rem; color: #155724; margin-top: 5px;">CPU cores to CP4I workloads</div>
            </div>

            <div style="background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 20px; border-radius: 4px;">
                <div style="font-size: 2rem; font-weight: bold; color: #0c5460;">{platform_count}</div>
                <div style="color: #0c5460; font-weight: 500;">Platform Components</div>
                <div style="font-size: 0.85rem; color: #0c5460; margin-top: 5px;">Part of cluster license</div>
            </div>

            <div style="background: #f8f9fa; border-left: 4px solid #6c757d; padding: 20px; border-radius: 4px;">
                <div style="font-size: 2rem; font-weight: bold; color: #495057;">{free_count}</div>
                <div style="color: #495057; font-weight: 500;">Free/Open Source</div>
                <div style="font-size: 0.85rem; color: #495057; margin-top: 5px;">No additional license cost</div>
            </div>
        </div>

        <h3 style="margin: 30px 0 15px 0;">CP4I Licensed Components (VPC Contributors)</h3>
        <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Component</th>
                    <th>Namespace</th>
                    <th>CPU Requested</th>
                    <th>VPC Contribution</th>
                </tr>
            </thead>
            <tbody>
"""

        for pod in sorted(cp4i_pods, key=lambda x: x.get('vpc_contribution', 0), reverse=True):
            name = pod.get('name', 'Unknown')
            namespace = pod.get('namespace', 'Unknown')
            cpu = pod.get('resources', {}).get('cpu_requests', 0)
            vpc = pod.get('vpc_contribution', 0)

            html_row = f"""                <tr>
                    <td>{name}</td>
                    <td><span class="status-badge status-blue">{namespace}</span></td>
                    <td>{cpu:.2f} cores</td>
                    <td><strong>{vpc:.2f} VPC</strong></td>
                </tr>"""
            html += html_row

        html += """            </tbody>
        </table>
        </div>

        <div class="info-box" style="margin-top: 20px; background: #e7f3ff;">
            <strong>📊 Cost Optimization Tips:</strong><br>
            • Right-size pod resource requests to actual usage<br>
            • Share Event Streams clusters across workloads<br>
            • Use non-production licenses for dev/test environments<br>
            • Review VPC allocation quarterly
        </div>
    </div>"""

        return html

    def _render_wave6_workload_health(self) -> str:
        """Wave 6: Workload Health View"""
        if not self.resource_summary:
            return ""

        workloads = self.resource_summary.get('workloads', {})
        business_count = workloads.get('business_workloads', 0)
        infra_count = workloads.get('infrastructure', 0)

        # Get business workload pods
        categorized = self.resource_summary.get('categorized_pods', [])
        business_pods = [p for p in categorized if p['is_workload']]

        return f"""<div class="wave">
        <div class="wave-header">
            <div class="wave-title">🎯 Workload Health</div>
            <div class="wave-number">6</div>
        </div>

        <div class="info-box" style="margin-bottom: 20px;">
            <strong>💡 Business Workloads Only</strong><br>
            This view shows ONLY your business workloads (applications that deliver value).
            Infrastructure and platform components are excluded.
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 8px; color: white;">
                <div style="font-size: 3rem; font-weight: bold;">{business_count}</div>
                <div style="font-size: 1.2rem; font-weight: 500;">Business Workloads</div>
                <div style="font-size: 0.9rem; opacity: 0.9; margin-top: 5px;">Applications delivering value</div>
            </div>

            <div style="background: #f8f9fa; border: 2px solid #dee2e6; padding: 30px; border-radius: 8px;">
                <div style="font-size: 3rem; font-weight: bold; color: #6c757d;">{infra_count}</div>
                <div style="font-size: 1.2rem; font-weight: 500; color: #6c757d;">Infrastructure Pods</div>
                <div style="font-size: 0.9rem; color: #6c757d; margin-top: 5px;">Supporting components (hidden below)</div>
            </div>
        </div>

        <h3 style="margin: 30px 0 15px 0;">Your Business Workloads</h3>
"""

        if not business_pods:
            html += """        <div class="info-box" style="background: #fff3cd;">
            <strong>⚠️ No Business Workloads Detected</strong><br>
            Either you have no custom applications deployed, or the categorization rules need updating.
            Check <code>resource_categories.yaml</code> to adjust workload patterns.
        </div>
    </div>"""
            return html

        # Group by namespace
        by_namespace = {}
        for pod in business_pods:
            ns = pod.get('namespace', 'unknown')
            if ns not in by_namespace:
                by_namespace[ns] = []
            by_namespace[ns].append(pod)

        html = ""
        for namespace, pods in sorted(by_namespace.items()):
            html += f"""        <div style="margin: 20px 0;">
            <h4 style="color: #0f62fe; margin-bottom: 10px;">📁 {namespace}</h4>
            <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Workload</th>
                        <th>Status</th>
                        <th>CPU</th>
                        <th>Memory</th>
                        <th>Criticality</th>
                    </tr>
                </thead>
                <tbody>
"""

            for pod in pods:
                name = pod.get('name', 'Unknown')
                # Get original pod data for status
                original_pod = next((p for p in self.pods if p['name'] == name), {})
                phase = original_pod.get('phase', 'Unknown')
                ready = original_pod.get('ready', '0/0')

                status_class = 'status-green' if phase == 'Running' else 'status-yellow'

                cpu = pod.get('resources', {}).get('cpu_requests', 0)
                mem = pod.get('resources', {}).get('memory_requests', 0)
                mem_gb = mem / (1024 ** 3) if mem > 0 else 0

                criticality = pod.get('criticality', 'unknown')
                crit_color = {'critical': '#dc3545', 'important': '#ffc107', 'optional': '#28a745'}.get(criticality, '#6c757d')

                html += f"""                    <tr>
                        <td><strong>{name}</strong></td>
                        <td><span class="status-badge {status_class}">{phase} ({ready})</span></td>
                        <td>{cpu:.2f} cores</td>
                        <td>{mem_gb:.2f} GB</td>
                        <td><span style="padding: 4px 8px; background: {crit_color}; color: white; border-radius: 4px; font-size: 0.8rem;">{criticality.upper()}</span></td>
                    </tr>
"""

            html += """                </tbody>
            </table>
            </div>
        </div>
"""

        html += """    </div>"""
        return html

    def _render_wave7_criticality(self) -> str:
        """Wave 7: Criticality Tiers"""
        if not self.resource_summary:
            return ""

        criticality = self.resource_summary.get('criticality', {})
        breakdown = criticality.get('breakdown', {})

        critical_count = breakdown.get('critical', 0)
        important_count = breakdown.get('important', 0)
        optional_count = breakdown.get('optional', 0)

        # Get pods by criticality
        categorized = self.resource_summary.get('categorized_pods', [])

        return f"""<div class="wave">
        <div class="wave-header">
            <div class="wave-title">🚦 Criticality Tiers</div>
            <div class="wave-number">7</div>
        </div>

        <div class="info-box" style="margin-bottom: 20px;">
            <strong>💡 What Can You Afford to Lose?</strong><br>
            Components categorized by criticality: Critical (can't function without), Important (needed for operations), Optional (nice to have).
        </div>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px;">
            <div style="background: #f8d7da; border-left: 4px solid #dc3545; padding: 20px; border-radius: 4px;">
                <div style="font-size: 2.5rem; font-weight: bold; color: #721c24;">{critical_count}</div>
                <div style="color: #721c24; font-weight: 500; font-size: 1.1rem;">🔴 CRITICAL</div>
                <div style="font-size: 0.85rem; color: #721c24; margin-top: 5px;">Must be running</div>
            </div>

            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; border-radius: 4px;">
                <div style="font-size: 2.5rem; font-weight: bold; color: #856404;">{important_count}</div>
                <div style="color: #856404; font-weight: 500; font-size: 1.1rem;">🟡 IMPORTANT</div>
                <div style="font-size: 0.85rem; color: #856404; margin-top: 5px;">Needed for operations</div>
            </div>

            <div style="background: #d4edda; border-left: 4px solid #28a745; padding: 20px; border-radius: 4px;">
                <div style="font-size: 2.5rem; font-weight: bold; color: #155724;">{optional_count}</div>
                <div style="color: #155724; font-weight: 500; font-size: 1.1rem;">🟢 OPTIONAL</div>
                <div style="font-size: 0.85rem; color: #155724; margin-top: 5px;">Nice to have</div>
            </div>
        </div>

        <div class="accordion" style="margin: 20px 0;">
"""

        # Critical section
        critical_pods = [p for p in categorized if p['criticality'] == 'critical']
        html = ""
        html += f"""            <div class="accordion-item" style="border: 2px solid #dc3545; margin-bottom: 10px;">
                <div class="accordion-header" style="background: #f8d7da; padding: 15px; cursor: pointer;" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'">
                    <strong style="color: #721c24;">🔴 CRITICAL Components ({critical_count})</strong>
                    <span style="float: right;">▼</span>
                </div>
                <div class="accordion-content" style="display: none; padding: 15px; background: white;">
                    <ul style="margin: 0; padding-left: 20px;">
"""
        for pod in critical_pods[:20]:  # Limit to 20
            name = pod.get('name', 'Unknown')
            namespace = pod.get('namespace', 'Unknown')
            html += f"""                        <li>{name} <span style="color: #6c757d; font-size: 0.85rem;">({namespace})</span></li>
"""
        if len(critical_pods) > 20:
            html += f"""                        <li style="color: #6c757d; font-style: italic;">... and {len(critical_pods) - 20} more</li>
"""
        html += """                    </ul>
                </div>
            </div>
"""

        # Important section
        important_pods = [p for p in categorized if p['criticality'] == 'important']
        html += f"""            <div class="accordion-item" style="border: 2px solid #ffc107; margin-bottom: 10px;">
                <div class="accordion-header" style="background: #fff3cd; padding: 15px; cursor: pointer;" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'">
                    <strong style="color: #856404;">🟡 IMPORTANT Components ({important_count})</strong>
                    <span style="float: right;">▼</span>
                </div>
                <div class="accordion-content" style="display: none; padding: 15px; background: white;">
                    <ul style="margin: 0; padding-left: 20px;">
"""
        for pod in important_pods[:20]:
            name = pod.get('name', 'Unknown')
            namespace = pod.get('namespace', 'Unknown')
            html += f"""                        <li>{name} <span style="color: #6c757d; font-size: 0.85rem;">({namespace})</span></li>
"""
        if len(important_pods) > 20:
            html += f"""                        <li style="color: #6c757d; font-style: italic;">... and {len(important_pods) - 20} more</li>
"""
        html += """                    </ul>
                </div>
            </div>
"""

        # Optional section
        optional_pods = [p for p in categorized if p['criticality'] == 'optional']
        html += f"""            <div class="accordion-item" style="border: 2px solid #28a745;">
                <div class="accordion-header" style="background: #d4edda; padding: 15px; cursor: pointer;" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'">
                    <strong style="color: #155724;">🟢 OPTIONAL Components ({optional_count})</strong>
                    <span style="float: right;">▼</span>
                </div>
                <div class="accordion-content" style="display: none; padding: 15px; background: white;">
                    <ul style="margin: 0; padding-left: 20px;">
"""
        for pod in optional_pods[:20]:
            name = pod.get('name', 'Unknown')
            namespace = pod.get('namespace', 'Unknown')
            html += f"""                        <li>{name} <span style="color: #6c757d; font-size: 0.85rem;">({namespace})</span></li>
"""
        if len(optional_pods) > 20:
            html += f"""                        <li style="color: #6c757d; font-style: italic;">... and {len(optional_pods) - 20} more</li>
"""
        html += """                    </ul>
                </div>
            </div>
        </div>

        <div class="info-box" style="margin-top: 20px; background: #e7f3ff;">
            <strong>💡 Using This View:</strong><br>
            • <strong>During Outages:</strong> Prioritize restoring CRITICAL components first<br>
            • <strong>Cost Cutting:</strong> OPTIONAL components can be scaled down or removed<br>
            • <strong>Maintenance Windows:</strong> Schedule OPTIONAL updates separately from CRITICAL<br>
            • <strong>Disaster Recovery:</strong> CRITICAL components need backup/DR, OPTIONAL may not
        </div>
    </div>"""

        return html

    def _render_wave8_resource_utilization(self) -> str:
        """Wave 8: Resource Utilization"""
        if not self.resource_summary:
            return ""

        resources = self.resource_summary.get('resources', {})
        total_cpu = resources.get('total_cpu_requests_cores', 0)
        total_mem_gb = resources.get('total_memory_requests_gb', 0)

        # Get top resource consumers
        categorized = self.resource_summary.get('categorized_pods', [])
        by_cpu = sorted(categorized, key=lambda x: x.get('resources', {}).get('cpu_requests', 0), reverse=True)[:10]
        by_mem = sorted(categorized, key=lambda x: x.get('resources', {}).get('memory_requests', 0), reverse=True)[:10]

        return f"""<div class="wave">
        <div class="wave-header">
            <div class="wave-title">📊 Resource Utilization</div>
            <div class="wave-number">8</div>
        </div>

        <div class="info-box" style="margin-bottom: 20px;">
            <strong>💡 Resource Allocation Overview</strong><br>
            Shows resource requests across all pods. Use this to identify over/under-provisioned components.
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 30px; border-radius: 8px; color: white;">
                <div style="font-size: 3rem; font-weight: bold;">{total_cpu:.1f}</div>
                <div style="font-size: 1.2rem; font-weight: 500;">Total CPU Cores</div>
                <div style="font-size: 0.9rem; opacity: 0.9; margin-top: 5px;">Requested across all pods</div>
            </div>

            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 30px; border-radius: 8px; color: white;">
                <div style="font-size: 3rem; font-weight: bold;">{total_mem_gb:.1f}</div>
                <div style="font-size: 1.2rem; font-weight: 500;">Total Memory (GB)</div>
                <div style="font-size: 0.9rem; opacity: 0.9; margin-top: 5px;">Requested across all pods</div>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
            <div>
                <h3 style="margin-bottom: 15px;">🔥 Top CPU Consumers</h3>
                <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Pod</th>
                            <th>Namespace</th>
                            <th>CPU Cores</th>
                        </tr>
                    </thead>
                    <tbody>
"""

        for pod in by_cpu:
            name = pod.get('name', 'Unknown')
            namespace = pod.get('namespace', 'Unknown')
            cpu = pod.get('resources', {}).get('cpu_requests', 0)

            html += f"""                        <tr>
                            <td style="font-size: 0.85rem;">{name[:40]}{'...' if len(name) > 40 else ''}</td>
                            <td><span class="status-badge status-blue">{namespace}</span></td>
                            <td><strong>{cpu:.2f}</strong></td>
                        </tr>
"""

        html += """                    </tbody>
                </table>
                </div>
            </div>

            <div>
                <h3 style="margin-bottom: 15px;">💾 Top Memory Consumers</h3>
                <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Pod</th>
                            <th>Namespace</th>
                            <th>Memory (GB)</th>
                        </tr>
                    </thead>
                    <tbody>
"""

        for pod in by_mem:
            name = pod.get('name', 'Unknown')
            namespace = pod.get('namespace', 'Unknown')
            mem = pod.get('resources', {}).get('memory_requests', 0)
            mem_gb = mem / (1024 ** 3) if mem > 0 else 0

            html += f"""                        <tr>
                            <td style="font-size: 0.85rem;">{name[:40]}{'...' if len(name) > 40 else ''}</td>
                            <td><span class="status-badge status-blue">{namespace}</span></td>
                            <td><strong>{mem_gb:.2f}</strong></td>
                        </tr>
"""

        html += """                    </tbody>
                </table>
                </div>
            </div>
        </div>

        <div class="info-box" style="margin-top: 30px; background: #fff3cd;">
            <strong>⚠️ Note: Resource Requests vs Actual Usage</strong><br>
            This view shows <strong>resource requests</strong> (what pods ask for), not actual usage.
            For true efficiency analysis, you would need to compare requests to actual metrics from Prometheus.
            <br><br>
            <strong>Common Patterns:</strong><br>
            • Over-provisioned: Pod requests 4 cores but uses < 1 core (wasteful)<br>
            • Under-provisioned: Pod requests 1 core but consistently uses > 0.9 cores (risky)<br>
            • Efficient: Pod uses 50-80% of requested resources (ideal)
        </div>
    </div>"""

        return html

    def _render_wave3_infrastructure(self) -> str:
        """Wave 3: Infrastructure View"""
        return f"""<div class="wave">
        <div class="wave-header">
            <div class="wave-title">Infrastructure</div>
            <div class="wave-number">3</div>
        </div>

        <h3 style="margin-bottom: 15px;">Cluster Nodes</h3>
        {self._render_nodes_table()}

        <h3 style="margin: 30px 0 15px 0;">Namespaces</h3>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total Projects</div>
                <div class="metric-value">{len(self.namespaces)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Operators</div>
                <div class="metric-value">{len(self.operators.get('all', []))}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Pods Collected</div>
                <div class="metric-value">{len(self.pods)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Routes</div>
                <div class="metric-value">{len(self.routes)}</div>
            </div>
        </div>
    </div>"""

    def _format_memory(self, memory_str: str) -> str:
        """Format memory from Ki to human-readable GiB/MiB"""
        if not memory_str or memory_str == 'N/A':
            return 'N/A'

        try:
            # Remove 'Ki' suffix and convert to int
            if memory_str.endswith('Ki'):
                memory_ki = int(memory_str[:-2])

                # Convert to GiB
                memory_gib = memory_ki / (1024 * 1024)

                # If >= 1 GiB, show in GiB, otherwise MiB
                if memory_gib >= 1:
                    return f"{memory_gib:.1f} GiB"
                else:
                    memory_mib = memory_ki / 1024
                    return f"{memory_mib:.0f} MiB"
            else:
                return memory_str
        except (ValueError, AttributeError):
            return memory_str

    def _format_version(self, version_str: str) -> str:
        """Format version string to be more readable"""
        if not version_str or version_str == 'Unknown':
            return 'Unknown'

        # Format: v1.29.14+f3cb5c1 -> v1.29.14 (f3cb5c1)
        if '+' in version_str:
            parts = version_str.split('+')
            main_version = parts[0]
            commit = parts[1] if len(parts) > 1 else ''
            return f"{main_version}<br><span style='font-size: 0.75em; color: #6c757d;'>({commit})</span>"

        return version_str

    def _render_nodes_table(self) -> str:
        """Render nodes table"""
        rows = ""
        for node in self.nodes:
            status_class = 'green' if node.get('status') == 'Ready' else 'red'
            cpu = node.get('capacity', {}).get('cpu', 'N/A')
            memory_raw = node.get('capacity', {}).get('memory', 'N/A')
            memory = self._format_memory(memory_raw)
            version = self._format_version(node.get('version', 'Unknown'))

            rows += f"""<tr>
            <td>{node.get('name', 'Unknown')}</td>
            <td><span class="status-badge status-{status_class}">{node.get('status', 'Unknown')}</span></td>
            <td>{cpu}</td>
            <td>{memory}</td>
            <td>{version}</td>
        </tr>"""

        return f"""<div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Node Name</th>
                    <th>Status</th>
                    <th>CPU</th>
                    <th>Memory</th>
                    <th>Version</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>"""

    def _render_operators_table(self, operators: List[Dict]) -> str:
        """Render operators table with deduplication and grouping"""
        # Group operators by name to avoid showing duplicates
        from collections import defaultdict
        grouped = defaultdict(list)

        for op in operators:
            key = (op.get('display_name', 'Unknown'), op.get('version', 'N/A'))
            grouped[key].append(op)

        rows = ""
        count = 0

        # Sort by name
        for (display_name, version), op_list in sorted(grouped.items()):
            if count >= 15:  # Limit to 15 unique operators
                break

            # Get namespaces where this operator exists
            namespaces = [op.get('namespace') for op in op_list]

            # Focus on CP4I-relevant namespaces
            cp4i_namespaces = [ns for ns in namespaces if
                              'integration' in ns or 'ibm' in ns or 'cp4i' in ns]

            if not cp4i_namespaces:
                cp4i_namespaces = namespaces[:3]  # Show first 3 if none match

            # Show primary namespace + count if multiple
            if len(namespaces) == 1:
                ns_display = namespaces[0]
            elif len(cp4i_namespaces) <= 2:
                ns_display = ", ".join(cp4i_namespaces)
            else:
                ns_display = f"{cp4i_namespaces[0]} (+{len(namespaces)-1} more)"

            # Determine status
            phases = [op.get('phase', 'Unknown') for op in op_list]
            if all(p == 'Succeeded' for p in phases):
                phase = 'Succeeded'
                status_class = 'green'
            elif any(p == 'Failed' for p in phases):
                phase = 'Failed'
                status_class = 'red'
            else:
                phase = phases[0]
                status_class = 'yellow'

            rows += f"""<tr>
            <td>{display_name}</td>
            <td>{ns_display}</td>
            <td>{version}</td>
            <td><span class="status-badge status-{status_class}">{phase}</span></td>
        </tr>"""
            count += 1

        return f"""<div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Capability</th>
                    <th>Namespace(s)</th>
                    <th>Version</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>"""

    def _render_footer(self) -> str:
        """Render dashboard footer"""
        collection_time = self.metadata.get('collection_timestamp', '')
        return f"""<div class="footer">
        <div class="refresh-time">Snapshot: {self._format_timestamp(collection_time)}</div>
        <p style="margin-top: 10px;">CP4I Chief Console v1.0 | Powered by Chief Console Prototype</p>
    </div>"""

    def _determine_overall_status(self) -> Dict[str, str]:
        """Determine overall cluster status"""
        error_count = len(self.metadata.get('errors', []))
        warning_count = len(self.metadata.get('warnings', []))
        ready_nodes = sum(1 for n in self.nodes if n.get('status') == 'Ready')
        total_nodes = len(self.nodes)

        if error_count > 0:
            return {'color': 'red', 'text': 'Issues', 'reason': f'{error_count} errors detected'}
        elif warning_count > 0:
            return {'color': 'yellow', 'text': 'Warning', 'reason': f'{warning_count} warnings'}
        elif ready_nodes == total_nodes and total_nodes > 0:
            return {'color': 'green', 'text': 'Healthy', 'reason': 'All systems operational'}
        else:
            return {'color': 'yellow', 'text': 'Degraded', 'reason': f'{total_nodes - ready_nodes} nodes not ready'}

    def _format_timestamp(self, iso_string: str) -> str:
        """Format ISO timestamp to readable format"""
        if not iso_string:
            return "Unknown"
        try:
            dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return iso_string


def render_dashboard(snapshot_path: str, output_path: str = "output/dashboard.html", diff: Optional[Dict[str, Any]] = None) -> str:
    """
    Render dashboard from snapshot file

    Args:
        snapshot_path: Path to JSON snapshot file
        output_path: Path for output HTML file
        diff: Optional diff data from comparing snapshots

    Returns:
        Path to generated HTML file
    """
    # Load snapshot
    with open(snapshot_path, 'r') as f:
        snapshot = json.load(f)

    # Render dashboard
    renderer = DashboardRenderer(snapshot, diff)
    html = renderer.render()

    # Write to file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        f.write(html)

    return str(output_file)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        # Find latest snapshot
        snapshots = sorted(Path("output/snapshots").glob("snapshot-*.json"))
        if not snapshots:
            print("No snapshots found. Run collector first: python src/collector_ocp.py")
            sys.exit(1)
        snapshot_path = snapshots[-1]
        print(f"Using latest snapshot: {snapshot_path}")
    else:
        snapshot_path = sys.argv[1]

    output_path = sys.argv[2] if len(sys.argv) > 2 else "output/dashboard.html"

    print(f"Rendering dashboard from: {snapshot_path}")
    result = render_dashboard(str(snapshot_path), output_path)
    print(f"Dashboard generated: {result}")
    print(f"\nOpen in browser: file://{Path(result).absolute()}")
