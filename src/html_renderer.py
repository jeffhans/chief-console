"""
HTML Dashboard Renderer for CP4I Mission Console

Generates a self-contained HTML dashboard from cluster snapshots.
Implements "Meaningful Waves" design with graceful degradation.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


class DashboardRenderer:
    """Renders Mission Console dashboard from snapshot data"""

    def __init__(self, snapshot: Dict[str, Any]):
        self.snapshot = snapshot
        self.metadata = snapshot.get('metadata', {})
        self.cluster = snapshot.get('cluster', {})
        self.nodes = snapshot.get('nodes', [])
        self.namespaces = snapshot.get('namespaces', [])
        self.operators = snapshot.get('operators', {})
        self.pods = snapshot.get('pods', [])
        self.routes = snapshot.get('routes', [])
        self.cp4i_namespaces = snapshot.get('cp4i_namespaces', [])

    def render(self) -> str:
        """Generate complete HTML dashboard"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CP4I Mission Console</title>
    {self._render_styles()}
</head>
<body>
    <div class="container">
        {self._render_header()}
        {self._render_wave1_executive()}
        {self._render_wave2_cp4i()}
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
            console.log('CP4I Mission Console Dashboard Loaded');
        });
    </script>"""

    def _render_header(self) -> str:
        """Render dashboard header"""
        cluster_version = self.cluster.get('version', 'Unknown')
        collection_time = self.metadata.get('collection_timestamp', '')

        return f"""<div class="header">
        <h1>CP4I Mission Console</h1>
        <div class="subtitle">
            OpenShift {cluster_version} | Last updated: {self._format_timestamp(collection_time)}
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

    def _render_nodes_table(self) -> str:
        """Render nodes table"""
        rows = ""
        for node in self.nodes:
            status_class = 'green' if node.get('status') == 'Ready' else 'red'
            cpu = node.get('capacity', {}).get('cpu', 'N/A')
            memory = node.get('capacity', {}).get('memory', 'N/A')

            rows += f"""<tr>
            <td>{node.get('name', 'Unknown')}</td>
            <td><span class="status-badge status-{status_class}">{node.get('status', 'Unknown')}</span></td>
            <td>{cpu}</td>
            <td>{memory}</td>
            <td>{node.get('version', 'Unknown')}</td>
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
        <p style="margin-top: 10px;">CP4I Mission Console v1.0 | Powered by Mission Console Prototype</p>
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


def render_dashboard(snapshot_path: str, output_path: str = "output/dashboard.html") -> str:
    """
    Render dashboard from snapshot file

    Args:
        snapshot_path: Path to JSON snapshot file
        output_path: Path for output HTML file

    Returns:
        Path to generated HTML file
    """
    # Load snapshot
    with open(snapshot_path, 'r') as f:
        snapshot = json.load(f)

    # Render dashboard
    renderer = DashboardRenderer(snapshot)
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
