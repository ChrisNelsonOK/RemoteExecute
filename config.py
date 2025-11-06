"""
Configuration file for Remote Execute
Adjust these settings based on your environment
"""

# Network timeouts (in seconds)
# Increase these if you're working over VPN or high-latency connections
SSH_TIMEOUT = 30  # Default: 10
WINRM_TIMEOUT = 30  # Default: 10
EXECUTION_TIMEOUT = 600  # Default: 300 (5 minutes)
CONNECTION_TEST_TIMEOUT = 10  # Default: 5

# Default remote directories
LINUX_REMOTE_DIR = "/tmp"
WINDOWS_REMOTE_DIR = "C:\\Temp"

# WinRM settings
WINRM_HTTP_PORT = 5985
WINRM_HTTPS_PORT = 5986
WINRM_TRANSPORT = "ntlm"  # Options: ntlm, basic, credssp

# SSH settings
SSH_PORT = 22

# UI settings
WINDOW_TITLE = "Remote Execute - Dark Edition"
DEFAULT_GEOMETRY = "1200x800"

# Logging
ENABLE_DEBUG_LOGGING = False
LOG_FILE = "remote_execute.log"
