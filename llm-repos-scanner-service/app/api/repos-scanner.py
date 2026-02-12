import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import tempfile

class RepoScanner:
    """Compiles a git repository into a single consolidated text file"""
    def __init__(self, repo_url: str, output_file: str = None, username: str = None, password: str = None):
        """
        Initialize Repo RepoScanner Compiler

        Args:
            repo_url: Git repository URL (HTTP/HTTPS from Stash/Bitbucket)
            output_file: Output file path (defaults to repo.txt)
            username: Git username for authentication (optional)
            password: Git password/token for authentication (optional)
        """
        self.repo_url = repo_url
        self.output_file = output_file or "repo.txt"
        self.username = username
        self.password = password
        self.temp_dir = None

        # Statistics
        self.stats = {
            'total_files': 0,
            'total_size': 0,
            'binary_files': 0,
            'text_files': 0
        }

    def _prepare_repo_url(self) -> str:
        """Inject credentials into repo URL if provided"""
        if not self.username or not self.password:
            return self.repo_url

        # Handle HTTPS URLs
        if self.repo_url.startswith('https://'):
            # Insert credentials: https://user:pass@domain.com/repo.git
            url_without_protocol = self.repo_url.replace('https://', '')
            return f'https://{self.username}:{self.password}@{url_without_protocol}'
        elif self.repo_url.startswith('http://'):
            url_without_protocol = self.repo_url.replace('http://', '')
            return f'http://{self.username}:{self.password}@{url_without_protocol}'

        return self.repo_url

    def clone_repository(self) -> Path:
        """Clone the repository to a temporary directory"""
        print(f"🔄 Cloning repository: {self.repo_url}")

        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix='repoScanner_')
        clone_path = Path(self.temp_dir) / 'repo'

        try:
            # Prepare URL with credentials
            clone_url = self._prepare_repo_url()

            # Clone the repository
            result = subprocess.run(
                ['git', 'clone', clone_url, str(clone_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                raise Exception(f"Git clone failed: {result.stderr}")

            print(f"✅ Repository cloned to: {clone_path}")
            return clone_path

        except subprocess.TimeoutExpired:
            raise Exception("Git clone timed out after 5 minutes")
        except FileNotFoundError:
            raise Exception("Git is not installed or not in PATH")
        except Exception as e:
            self.cleanup()
            raise Exception(f"Failed to clone repository: {str(e)}")



