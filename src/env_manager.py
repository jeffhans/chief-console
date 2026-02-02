"""
Environment Manager for CP4I Mission Console

Manages multiple CP4I environment profiles including:
- Credential storage and retrieval
- Environment metadata tracking
- PDF import of TechZone/cluster login information
- Environment switching and history
"""

import yaml
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
import re


class EnvironmentManager:
    """Manages CP4I environment profiles and credentials"""

    def __init__(self, env_file: str = "environments.yaml"):
        self.env_file = Path(env_file)
        self.environments = {}
        self.active_env = None

        if self.env_file.exists():
            self.load()

    def load(self) -> None:
        """Load environments from YAML file"""
        with open(self.env_file, 'r') as f:
            data = yaml.safe_load(f)
            self.environments = data.get('environments', {})
            self.active_env = data.get('active')

    def save(self) -> None:
        """Save environments to YAML file"""
        data = {
            'environments': self.environments,
            'active': self.active_env
        }
        with open(self.env_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def get_active_environment(self) -> Optional[Dict[str, Any]]:
        """Get the currently active environment configuration"""
        if self.active_env and self.active_env in self.environments:
            return self.environments[self.active_env]
        return None

    def set_active_environment(self, env_name: str) -> None:
        """Set the active environment"""
        if env_name not in self.environments:
            raise ValueError(f"Environment '{env_name}' not found")
        self.active_env = env_name
        self.save()

    def add_environment(self, env_name: str, env_data: Dict[str, Any]) -> None:
        """Add a new environment profile"""
        self.environments[env_name] = env_data
        if not self.active_env:
            self.active_env = env_name
        self.save()

    def import_from_pdf(self, pdf_path: str, env_name: Optional[str] = None, move_file: bool = False) -> str:
        """
        Import environment credentials from a TechZone/cluster PDF export

        Args:
            pdf_path: Path to the PDF file
            env_name: Optional name for the environment (auto-generated if not provided)
            move_file: If True, move the PDF to archive instead of copying (default: False)

        Returns:
            The name of the created environment
        """
        try:
            import PyPDF2
        except ImportError:
            raise ImportError(
                "PyPDF2 required for PDF import. Install with: pip install PyPDF2"
            )

        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Extract text from PDF
        text = self._extract_pdf_text(pdf_path)

        # Parse login information
        env_data = self._parse_login_info(text)

        # Add metadata
        if not env_name:
            env_name = f"imported-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        env_data['source'] = {
            'type': 'pdf',
            'file': str(pdf_path),
            'imported_date': datetime.now().isoformat(),
            'imported_by': 'chief-console-import'
        }

        if 'created_date' not in env_data:
            env_data['created_date'] = datetime.now().strftime('%Y-%m-%d')

        # Save imported PDF to archive
        self._archive_pdf(pdf_path, env_name, move_file)

        # Add to environments
        self.add_environment(env_name, env_data)

        return env_name

    def _extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text content from PDF"""
        import PyPDF2

        text = ""
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _parse_login_info(self, text: str) -> Dict[str, Any]:
        """
        Parse cluster login information from extracted PDF text

        This is a best-effort parser for common TechZone/OpenShift PDF formats.
        May need customization based on actual PDF format.
        """
        env_data = {
            'name': 'Imported Environment',
            'cluster': {},
            'platform_navigator': {},
            'capabilities': []
        }

        # Common patterns for OpenShift cluster info
        # Try TechZone format first, then OAuth format
        patterns = {
            # API URL patterns
            'api_url': [
                r'API URL\s+(https://[^\s]+)',  # TechZone: "API URL https://..."
                r'--server=(https://[^\s]+)',    # OAuth: "--server=https://..."
            ],
            # Console URL patterns
            'console_url': [
                r'OCP Console\s+(https://[^\s]+)',  # TechZone: "OCP Console https://..."
                r'Desktop url:\s+(https://[^\s]+)', # TechZone: "Desktop url: https://..."
                r'(?:Console URL|Web Console)[:\s]+(https://[^\s]+)',
            ],
            # Token pattern (OAuth format)
            'token': [
                r'--token=(sha256~[\w-]+)',      # OAuth: "--token=sha256~..."
                r'Your API token is\s+(sha256~[\w-]+)',  # OAuth display
            ],
            # Username patterns (prefer Cluster Admin)
            'username': [
                r'Cluster Admin Username\s+(\w+)',  # TechZone: "Cluster Admin Username kubeadmin"
                r'Username\s+(\w+)',                 # Generic
            ],
            # Password patterns (prefer Cluster Admin)
            'password': [
                r'Cluster Admin Password\s+([^\s\n]+)',  # TechZone: "Cluster Admin Password xxx"
                r'Password\s+([^\s\n]+)',                # Generic
            ],
            # Platform Navigator
            'platform_nav_url': [
                r'(?:Platform Navigator|Navigator URL)[:\s]+(https://[^\s]+)',
            ],
        }

        for key, pattern_list in patterns.items():
            # Try each pattern until we find a match
            for pattern in pattern_list:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()

                    if key in ['api_url', 'console_url']:
                        env_data['cluster'][key] = value
                    elif key in ['token', 'username', 'password']:
                        if 'auth' not in env_data['cluster']:
                            env_data['cluster']['auth'] = {}
                        env_data['cluster']['auth'][key] = value
                    elif key == 'platform_nav_url':
                        env_data['platform_navigator']['url'] = value
                    break  # Stop after first match

        return env_data

    def _archive_pdf(self, pdf_path: Path, env_name: str, move_file: bool = False) -> None:
        """Archive the imported PDF for future reference"""
        import shutil

        archive_dir = Path('output/env-imports')
        archive_dir.mkdir(parents=True, exist_ok=True)

        archive_path = archive_dir / f"{env_name}_{pdf_path.name}"

        if move_file:
            shutil.move(pdf_path, archive_path)
        else:
            shutil.copy2(pdf_path, archive_path)

    def get_oc_login_command(self, env_name: Optional[str] = None) -> str:
        """Generate the oc login command for an environment"""
        if not env_name:
            env_name = self.active_env

        if not env_name or env_name not in self.environments:
            raise ValueError("No environment specified or found")

        env = self.environments[env_name]
        cluster = env.get('cluster', {})
        auth = cluster.get('auth', {})

        api_url = cluster.get('api_url')
        if not api_url:
            raise ValueError(f"No API URL found for environment '{env_name}'")

        # Build oc login command
        cmd_parts = ['oc', 'login', api_url]

        if 'token' in auth:
            cmd_parts.extend(['--token', auth['token']])
        elif 'username' in auth:
            cmd_parts.extend(['--username', auth['username']])
            if 'password' in auth:
                cmd_parts.extend(['--password', auth['password']])

        # Add insecure-skip-tls-verify for TechZone environments (common)
        cmd_parts.append('--insecure-skip-tls-verify=true')

        return ' '.join(cmd_parts)

    def list_environments(self) -> Dict[str, Dict[str, Any]]:
        """List all configured environments with summary info"""
        summary = {}
        for name, env in self.environments.items():
            summary[name] = {
                'name': env.get('name', name),
                'created_date': env.get('created_date'),
                'expires_date': env.get('expires_date'),
                'cluster_url': env.get('cluster', {}).get('api_url'),
                'is_active': (name == self.active_env)
            }
        return summary


if __name__ == "__main__":
    # CLI usage example
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python env_manager.py list")
        print("  python env_manager.py import <pdf_path> [env_name] [--move]")
        print("  python env_manager.py activate <env_name>")
        print("  python env_manager.py login [env_name]")
        sys.exit(1)

    manager = EnvironmentManager()
    command = sys.argv[1]

    if command == "list":
        envs = manager.list_environments()
        for name, info in envs.items():
            active = " (ACTIVE)" if info['is_active'] else ""
            print(f"{name}{active}")
            print(f"  Name: {info['name']}")
            print(f"  Cluster: {info['cluster_url']}")
            print(f"  Created: {info['created_date']}")
            print()

    elif command == "import":
        if len(sys.argv) < 3:
            print("Error: PDF path required")
            sys.exit(1)
        pdf_path = sys.argv[2]

        # Parse optional arguments
        env_name = None
        move_file = False
        for arg in sys.argv[3:]:
            if arg == "--move":
                move_file = True
            elif not env_name:
                env_name = arg

        imported_name = manager.import_from_pdf(pdf_path, env_name, move_file)
        action = "Moved" if move_file else "Copied"
        print(f"Imported environment: {imported_name}")
        print(f"{action} PDF to: output/env-imports/{imported_name}_{Path(pdf_path).name}")
        print(f"Set as active. Use 'python env_manager.py login' to connect.")

    elif command == "activate":
        if len(sys.argv) < 3:
            print("Error: Environment name required")
            sys.exit(1)
        env_name = sys.argv[2]
        manager.set_active_environment(env_name)
        print(f"Activated environment: {env_name}")

    elif command == "login":
        env_name = sys.argv[2] if len(sys.argv) > 2 else None
        cmd = manager.get_oc_login_command(env_name)
        print(f"Run this command to login:\n\n{cmd}\n")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
