# Remote Execute - Dark Edition

A beautiful, dark-themed Python application for remote script and binary execution on Windows and Linux systems.

![Remote Execute](https://img.shields.io/badge/Python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-green)
![License](https://img.shields.io/badge/License-MIT-orange)

## Features

### 🎨 Beautiful Dark Theme UI
- Modern, sleek dark interface built with CustomTkinter
- Professional color scheme with intuitive layout
- Responsive design that scales with your window

### 🔐 Secure Credential Management
- Store credentials for multiple systems in encrypted SQLite database
- Support for multiple credential types:
  - **Windows Local**: Local Windows accounts
  - **Windows Domain**: Active Directory domain accounts
  - **Linux**: SSH credentials for Ubuntu/Debian systems
  - **SNMPv2**: Community strings for SNMP-enabled devices
- Passwords encrypted using Fernet symmetric encryption
- Easy credential add/edit/delete interface

### 🚀 Remote Execution
- Execute scripts and binaries on remote Windows and Linux systems
- Supported script types:
  - Python (.py)
  - PowerShell (.ps1)
  - Bash (.sh)
  - Batch (.bat)
  - Executables (.exe)
- Real-time output display
- Execution history tracking

### 📁 File Management
- Multi-file selection and upload
- Drag-and-drop support (coming soon)
- Browse local filesystem for scripts and binaries

### ✍️ Built-in Script Editor
- Create scripts on-the-fly without leaving the application
- Syntax templates for Python, PowerShell, Bash, and Batch
- Save directly to temp folder and execute immediately
- Flyout window design keeps your workspace clean

### 🔍 Connection Testing
- Test connectivity before execution
- Check SSH (port 22) and WinRM (port 5985) availability
- Instant feedback on connection status

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### For Windows Remote Execution
Windows systems must have WinRM enabled. Run this PowerShell command on target machines:

```powershell
# Enable WinRM
Enable-PSRemoting -Force

# Configure WinRM for HTTP (port 5985)
Set-Item WSMan:\localhost\Service\Auth\Basic -Value $true
Set-Item WSMan:\localhost\Service\AllowUnencrypted -Value $true

# Add trusted hosts (if not in domain)
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "*" -Force

# Restart WinRM service
Restart-Service WinRM
```

### For Linux Remote Execution
Linux systems need SSH server installed:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install openssh-server

# Start SSH service
sudo systemctl start ssh
sudo systemctl enable ssh
```

### Install Application

1. **Clone or download this repository:**
   ```bash
   cd RemoteExecute
   ```

2. **Install required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## Usage Guide

### First Time Setup

1. **Launch the application:**
   ```bash
   python main.py
   ```

2. **Add credentials:**
   - Click "Manage Credentials" button
   - Click "Add Credential"
   - Fill in the form:
     - Host/IP: Target system IP or hostname
     - Type: Select credential type
     - Username: Login username
     - Password: Login password
     - Domain: (Windows Domain only) Domain name
     - Description: Optional note
   - Click "Save"

### Executing Scripts

1. **Enter target host:**
   - Type IP address or hostname in the "Host/IP" field
   - Or select from saved credentials

2. **Select credentials:**
   - Choose appropriate credentials from dropdown
   - Click refresh if you just added new credentials

3. **Select files to execute:**
   - Click "Browse Files" to select existing scripts/binaries
   - OR click "Create New Script" to write a script in the built-in editor

4. **Execute:**
   - Click the green "▶ EXECUTE" button
   - Watch real-time output in the output window

### Using the Script Editor

1. Click "Create New Script" button
2. Enter a filename (e.g., `backup.py`)
3. Select script type from dropdown
4. Click "Load Template" for a starter template
5. Write your script
6. Click "Save and Use" to add it to execution queue

### Managing Multiple Files

- You can select multiple files at once using "Browse Files"
- Files are executed in the order they were selected
- Clear selection with "Clear" button

## Database Structure

The application creates a `credentials.db` SQLite database in the working directory with the following tables:

### Credentials Table
- `id`: Unique identifier
- `host`: IP address or hostname
- `credential_type`: Type of credential
- `username`: Login username
- `password_encrypted`: Encrypted password
- `domain`: Windows domain (optional)
- `community_string_encrypted`: SNMP community string (optional)
- `description`: User description
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Execution History Table
- `id`: Unique identifier
- `host`: Target host
- `credential_type`: Type used
- `script_name`: Executed script name
- `execution_time`: When executed
- `status`: Success or Failed
- `output`: Execution output

## Security Considerations

⚠️ **Important Security Notes:**

1. **Credential Storage**: Passwords are encrypted using Fernet encryption. The encryption key is stored in `.encryption_key` file. Keep this file secure!

2. **Network Security**:
   - WinRM can be configured for HTTPS (recommended for production)
   - SSH uses password authentication by default (consider using SSH keys)

3. **Firewall Rules**: Ensure appropriate firewall rules allow:
   - SSH: Port 22
   - WinRM HTTP: Port 5985
   - WinRM HTTPS: Port 5986

4. **Access Control**: This tool provides powerful remote execution capabilities. Only use on systems you own or have explicit permission to manage.

## Troubleshooting

### Windows Connection Issues

**Problem**: "Could not establish WinRM connection"

**Solutions**:
- Verify WinRM is enabled on target system
- Check firewall allows port 5985
- Ensure user has admin rights
- Try adding target to TrustedHosts

### Linux Connection Issues

**Problem**: "Authentication failed"

**Solutions**:
- Verify SSH service is running: `sudo systemctl status ssh`
- Check username and password are correct
- Ensure user account is not locked
- Verify firewall allows port 22

### Script Execution Issues

**Problem**: Script uploads but doesn't execute

**Solutions**:
- Check script has proper shebang line (#!/usr/bin/env python3)
- Verify required interpreters are installed on target system
- Check script permissions (automatically set to 755)
- Review execution output for error messages

## Advanced Configuration

### Custom Remote Directories

By default:
- Linux: Files upload to `/tmp/`
- Windows: Files upload to `C:\Temp\`

Modify `remote_executor.py` to change these defaults.

### Execution Timeout

Default timeout is 300 seconds. Modify in `remote_executor.py`:

```python
stdin, stdout, stderr = self.client.exec_command(command, timeout=600)  # 10 minutes
```

## Project Structure

```
RemoteExecute/
├── main.py                 # Main application GUI
├── database.py             # Database and credential management
├── remote_executor.py      # Remote execution logic
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── credentials.db         # SQLite database (created on first run)
├── .encryption_key        # Encryption key (created on first run)
└── temp_scripts/          # Temporary scripts from editor (created as needed)
```

## Technologies Used

- **CustomTkinter**: Modern GUI framework
- **Paramiko**: SSH client for Linux connections
- **PyWinRM**: WinRM client for Windows connections
- **SQLite**: Lightweight database
- **Cryptography**: Fernet encryption for passwords

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

MIT License - See LICENSE file for details

## Disclaimer

This tool is provided for legitimate system administration purposes only. Users are responsible for ensuring they have appropriate authorization before executing commands on remote systems. The authors assume no liability for misuse of this software.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Happy Remote Execution! 🚀**
