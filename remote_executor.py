"""
Remote execution module for Windows and Linux systems
"""
import paramiko
import winrm
import os
import socket
from typing import Tuple, List
import tempfile
import time

class RemoteExecutor:
    """Base class for remote execution"""

    @staticmethod
    def test_connection(host: str, port: int = None, timeout: int = 5) -> Tuple[bool, str]:
        """Test if host is reachable"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port or 22))
            sock.close()
            if result == 0:
                return True, "Connection successful"
            else:
                return False, f"Port {port or 22} is not open"
        except socket.gaierror:
            return False, "Hostname could not be resolved"
        except socket.timeout:
            return False, "Connection timed out"
        except Exception as e:
            return False, f"Connection error: {str(e)}"


class LinuxExecutor(RemoteExecutor):
    """Execute commands on Linux systems via SSH"""

    def __init__(self, host: str, username: str, password: str, port: int = 22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.client = None

    def connect(self) -> Tuple[bool, str]:
        """Establish SSH connection"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10
            )
            return True, "Connected successfully"
        except paramiko.AuthenticationException:
            return False, "Authentication failed"
        except paramiko.SSHException as e:
            return False, f"SSH error: {str(e)}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def disconnect(self):
        """Close SSH connection"""
        if self.client:
            self.client.close()
            self.client = None

    def upload_file(self, local_path: str, remote_path: str = None) -> Tuple[bool, str]:
        """Upload a file to remote system"""
        try:
            if not self.client:
                return False, "Not connected"

            if not remote_path:
                remote_path = f"/tmp/{os.path.basename(local_path)}"

            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.chmod(remote_path, 0o755)  # Make executable
            sftp.close()

            return True, f"File uploaded to {remote_path}"
        except Exception as e:
            return False, f"Upload error: {str(e)}"

    def upload_files(self, local_paths: List[str], remote_dir: str = "/tmp") -> Tuple[bool, str, List[str]]:
        """Upload multiple files to remote system"""
        uploaded_paths = []
        try:
            if not self.client:
                return False, "Not connected", []

            sftp = self.client.open_sftp()

            # Ensure remote directory exists
            try:
                sftp.stat(remote_dir)
            except FileNotFoundError:
                sftp.mkdir(remote_dir)

            for local_path in local_paths:
                filename = os.path.basename(local_path)
                remote_path = f"{remote_dir}/{filename}"
                sftp.put(local_path, remote_path)
                sftp.chmod(remote_path, 0o755)
                uploaded_paths.append(remote_path)

            sftp.close()
            return True, f"Uploaded {len(uploaded_paths)} files", uploaded_paths
        except Exception as e:
            return False, f"Upload error: {str(e)}", uploaded_paths

    def execute_command(self, command: str) -> Tuple[bool, str, str]:
        """Execute a command on remote system"""
        try:
            if not self.client:
                return False, "Not connected", ""

            stdin, stdout, stderr = self.client.exec_command(command, timeout=300)
            exit_code = stdout.channel.recv_exit_status()

            output = stdout.read().decode('utf-8', errors='replace')
            error = stderr.read().decode('utf-8', errors='replace')

            if exit_code == 0:
                return True, output, error
            else:
                return False, output, error
        except Exception as e:
            return False, "", f"Execution error: {str(e)}"

    def execute_script(self, local_script_path: str, args: str = "") -> Tuple[bool, str, str]:
        """Upload and execute a script"""
        try:
            # Upload script
            success, message = self.upload_file(local_script_path)
            if not success:
                return False, "", message

            # Extract remote path from message
            remote_path = message.split("to ")[-1] if "to " in message else f"/tmp/{os.path.basename(local_script_path)}"

            # Determine script type and execute
            if local_script_path.endswith('.py'):
                command = f"python3 {remote_path} {args}"
            elif local_script_path.endswith('.sh'):
                command = f"bash {remote_path} {args}"
            else:
                command = f"{remote_path} {args}"

            return self.execute_command(command)
        except Exception as e:
            return False, "", f"Script execution error: {str(e)}"


class WindowsExecutor(RemoteExecutor):
    """Execute commands on Windows systems via WinRM"""

    def __init__(self, host: str, username: str, password: str, domain: str = None, port: int = 5985):
        self.host = host
        self.username = username
        self.password = password
        self.domain = domain
        self.port = port
        self.session = None

    def connect(self) -> Tuple[bool, str]:
        """Establish WinRM connection"""
        try:
            # Format username with domain if provided
            if self.domain:
                user = f"{self.domain}\\{self.username}"
            else:
                user = self.username

            # Try both HTTP and HTTPS
            endpoints = [
                f"http://{self.host}:{self.port}/wsman",
                f"https://{self.host}:5986/wsman"
            ]

            for endpoint in endpoints:
                try:
                    self.session = winrm.Session(
                        endpoint,
                        auth=(user, self.password),
                        server_cert_validation='ignore',
                        transport='ntlm'
                    )
                    # Test connection
                    result = self.session.run_cmd('echo', ['test'])
                    if result.status_code == 0:
                        return True, f"Connected successfully via {endpoint}"
                except Exception:
                    continue

            return False, "Could not establish WinRM connection on any endpoint"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def disconnect(self):
        """Close WinRM connection"""
        self.session = None

    def upload_file(self, local_path: str, remote_path: str = None) -> Tuple[bool, str]:
        """Upload a file to remote Windows system"""
        try:
            if not self.session:
                return False, "Not connected"

            if not remote_path:
                remote_path = f"C:\\Temp\\{os.path.basename(local_path)}"

            # Ensure remote directory exists
            remote_dir = os.path.dirname(remote_path).replace('/', '\\')
            self.session.run_ps(f"New-Item -ItemType Directory -Force -Path '{remote_dir}'")

            # Read local file
            with open(local_path, 'rb') as f:
                content = f.read()

            # Upload using PowerShell
            ps_script = f"""
$bytes = [System.Convert]::FromBase64String("{content.hex()}")
[System.IO.File]::WriteAllBytes("{remote_path}", $bytes)
"""
            # For large files, we need to chunk them
            import base64
            encoded_content = base64.b64encode(content).decode()

            # Split into chunks if too large
            chunk_size = 8000
            if len(encoded_content) > chunk_size:
                # Write in chunks
                self.session.run_ps(f"Remove-Item -Path '{remote_path}' -ErrorAction SilentlyContinue")
                for i in range(0, len(encoded_content), chunk_size):
                    chunk = encoded_content[i:i + chunk_size]
                    ps_chunk = f"""
$bytes = [System.Convert]::FromBase64String("{chunk}")
Add-Content -Path "{remote_path}" -Value $bytes -Encoding Byte
"""
                    result = self.session.run_ps(ps_chunk)
                    if result.status_code != 0:
                        return False, f"Upload error: {result.std_err.decode('utf-8', errors='replace')}"
            else:
                ps_script = f"""
$bytes = [System.Convert]::FromBase64String("{encoded_content}")
[System.IO.File]::WriteAllBytes("{remote_path}", $bytes)
"""
                result = self.session.run_ps(ps_script)
                if result.status_code != 0:
                    return False, f"Upload error: {result.std_err.decode('utf-8', errors='replace')}"

            return True, f"File uploaded to {remote_path}"
        except Exception as e:
            return False, f"Upload error: {str(e)}"

    def upload_files(self, local_paths: List[str], remote_dir: str = "C:\\Temp") -> Tuple[bool, str, List[str]]:
        """Upload multiple files to remote system"""
        uploaded_paths = []
        try:
            if not self.session:
                return False, "Not connected", []

            # Ensure remote directory exists
            self.session.run_ps(f"New-Item -ItemType Directory -Force -Path '{remote_dir}'")

            for local_path in local_paths:
                filename = os.path.basename(local_path)
                remote_path = f"{remote_dir}\\{filename}"
                success, message = self.upload_file(local_path, remote_path)
                if success:
                    uploaded_paths.append(remote_path)
                else:
                    return False, message, uploaded_paths

            return True, f"Uploaded {len(uploaded_paths)} files", uploaded_paths
        except Exception as e:
            return False, f"Upload error: {str(e)}", uploaded_paths

    def execute_command(self, command: str, use_powershell: bool = False) -> Tuple[bool, str, str]:
        """Execute a command on remote Windows system"""
        try:
            if not self.session:
                return False, "Not connected", ""

            if use_powershell:
                result = self.session.run_ps(command)
            else:
                result = self.session.run_cmd(command)

            output = result.std_out.decode('utf-8', errors='replace')
            error = result.std_err.decode('utf-8', errors='replace')

            if result.status_code == 0:
                return True, output, error
            else:
                return False, output, error
        except Exception as e:
            return False, "", f"Execution error: {str(e)}"

    def execute_script(self, local_script_path: str, args: str = "") -> Tuple[bool, str, str]:
        """Upload and execute a script"""
        try:
            # Upload script
            success, message = self.upload_file(local_script_path)
            if not success:
                return False, "", message

            # Extract remote path from message
            remote_path = message.split("to ")[-1] if "to " in message else f"C:\\Temp\\{os.path.basename(local_script_path)}"

            # Determine script type and execute
            if local_script_path.endswith('.ps1'):
                command = f"PowerShell -ExecutionPolicy Bypass -File '{remote_path}' {args}"
                return self.execute_command(command, use_powershell=False)
            elif local_script_path.endswith('.py'):
                command = f"python '{remote_path}' {args}"
                return self.execute_command(command)
            elif local_script_path.endswith('.bat') or local_script_path.endswith('.cmd'):
                command = f"'{remote_path}' {args}"
                return self.execute_command(command)
            else:
                # Try to execute as binary
                command = f"'{remote_path}' {args}"
                return self.execute_command(command)
        except Exception as e:
            return False, "", f"Script execution error: {str(e)}"
