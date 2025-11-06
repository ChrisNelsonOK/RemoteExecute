# macOS Setup Guide for Remote Execute

This guide covers everything you need to run Remote Execute from macOS over VPN to remote Windows and Linux hosts.

## 📋 Prerequisites

### 1. Install Xcode Command Line Tools
Required for compiling Python dependencies:

```bash
xcode-select --install
```

### 2. Install Homebrew (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 3. Install Python 3.13

```bash
# Install Python via Homebrew (includes tkinter)
brew install python@3.13 python-tk@3.13

# Verify installation
python3 --version
```

## 🚀 Installation

### 1. Navigate to Project Directory

```bash
cd RemoteExecute
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 4. Launch the Application

```bash
# Using the launcher script
./run.sh

# Or directly
python3 main.py
```

## 🔌 VPN Configuration

### Network Requirements

Your VPN must allow the following ports:

| Protocol | Port | Purpose |
|----------|------|---------|
| SSH | 22 | Linux remote execution |
| WinRM HTTP | 5985 | Windows remote execution |
| WinRM HTTPS | 5986 | Windows secure remote execution |

### Testing VPN Connectivity

Before using the application, test that your VPN routes traffic correctly:

```bash
# Test SSH connectivity (Linux hosts)
nc -zv 192.168.1.100 22

# Test WinRM connectivity (Windows hosts)
nc -zv 192.168.1.200 5985

# If nc is not available, install it
brew install netcat
```

### Common VPN Issues

**Problem**: "Connection timed out" errors

**Solutions**:
1. Verify VPN is connected: Check VPN client status
2. Check split-tunnel configuration: Ensure remote network is routed through VPN
3. Test basic connectivity: `ping <remote-host-ip>`
4. Increase timeouts in `config.py` (see below)

## ⚙️ Configuration for VPN/High-Latency Connections

The application includes `config.py` with adjustable timeouts for VPN scenarios:

```python
# config.py
SSH_TIMEOUT = 30          # Increase for high-latency VPN
WINRM_TIMEOUT = 30        # Increase for high-latency VPN
EXECUTION_TIMEOUT = 600   # Time allowed for script execution
CONNECTION_TEST_TIMEOUT = 10  # Connection test timeout
```

### Recommended Settings by Connection Type

**Low-latency VPN (< 50ms):**
```python
SSH_TIMEOUT = 15
WINRM_TIMEOUT = 15
EXECUTION_TIMEOUT = 300
CONNECTION_TEST_TIMEOUT = 5
```

**High-latency VPN (50-200ms):**
```python
SSH_TIMEOUT = 30
WINRM_TIMEOUT = 30
EXECUTION_TIMEOUT = 600
CONNECTION_TEST_TIMEOUT = 10
```

**Very high-latency/Satellite (> 200ms):**
```python
SSH_TIMEOUT = 60
WINRM_TIMEOUT = 60
EXECUTION_TIMEOUT = 900
CONNECTION_TEST_TIMEOUT = 20
```

## 🔒 macOS Security Considerations

### Firewall Settings

macOS firewall should not interfere since we make **outbound** connections only. However, if issues occur:

1. Open **System Preferences** → **Security & Privacy** → **Firewall**
2. Click **Firewall Options**
3. Ensure Python is allowed to accept incoming connections

### Gatekeeper and Python

If macOS blocks Python from running:

```bash
# Allow Python through Gatekeeper
sudo spctl --master-disable

# After installation, re-enable (optional)
sudo spctl --master-enable
```

## 🎯 Quick Start

### 1. Launch Application

```bash
cd RemoteExecute
source venv/bin/activate  # If using virtual environment
python3 main.py
```

### 2. Add Credentials

Click **"Manage Credentials"** → **"Add Credential"**

**For Windows hosts:**
- Host/IP: `192.168.1.200` (your Windows PC IP over VPN)
- Type: `Windows Local` or `Windows Domain`
- Username: `Administrator` or domain account
- Password: Your password
- Domain: (if using Windows Domain) `YOURDOMAIN`

**For Linux hosts:**
- Host/IP: `192.168.1.100` (your Linux server IP over VPN)
- Type: `Linux`
- Username: Your SSH username
- Password: Your SSH password

### 3. Test Connection

1. Enter host IP in main window
2. Select credential from dropdown
3. Click **"Test Connection"**
4. Verify both SSH and WinRM tests in output window

### 4. Execute Test Script

1. Click **"Browse Files"**
2. Navigate to `examples/`
3. Select `hello_world.py`
4. Click **"▶ EXECUTE"**
5. Watch output appear

## 🐛 Troubleshooting

### "Module 'tkinter' not found"

```bash
# Install tkinter support
brew install python-tk@3.13

# Or reinstall Python with tkinter
brew reinstall python@3.13
```

### "SSL: CERTIFICATE_VERIFY_FAILED"

This may occur with WinRM over HTTPS. The application already uses `server_cert_validation='ignore'`, but if issues persist:

```bash
# Install certificates
/Applications/Python\ 3.13/Install\ Certificates.command
```

### Slow Connection Over VPN

1. Edit `config.py` and increase timeouts
2. Use connection test first to check latency
3. Consider using WinRM HTTPS (port 5986) for Windows

### "Permission denied" on run.sh

```bash
chmod +x run.sh
```

### Python Version Conflicts

If you have multiple Python versions:

```bash
# Use specific Python version
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 🔧 Advanced Configuration

### Custom Remote Directories

Edit `config.py`:

```python
LINUX_REMOTE_DIR = "/home/myuser/scripts"
WINDOWS_REMOTE_DIR = "C:\\Scripts"
```

### Enable Debug Logging

Edit `config.py`:

```python
ENABLE_DEBUG_LOGGING = True
LOG_FILE = "remote_execute.log"
```

Then check `remote_execute.log` for detailed connection information.

### Using SSH Keys (Instead of Passwords)

For enhanced security with Linux hosts, consider using SSH keys. This requires modifying `remote_executor.py` to support key-based auth (not included by default).

## 📱 macOS-Specific Tips

### Running from Terminal

Create an alias in `~/.zshrc` or `~/.bash_profile`:

```bash
alias remote-exec='cd ~/RemoteExecute && source venv/bin/activate && python3 main.py'
```

Then simply run:
```bash
remote-exec
```

### Running as macOS Application

To create a macOS `.app` bundle:

```bash
# Install py2app
pip install py2app

# Create application (advanced users)
python setup.py py2app
```

### Menu Bar Integration

The application can be minimized to the macOS menu bar for quick access. The UI will remain in a normal window, but CustomTkinter provides native macOS look and feel.

## 🌐 VPN Provider-Specific Notes

### Cisco AnyConnect
- Works well with default settings
- May need to disable split-tunnel exclusions for remote networks

### OpenVPN
- Ensure routes are properly configured in `.ovpn` file
- Check `redirect-gateway` setting if having connectivity issues

### Tailscale/WireGuard
- Excellent performance with low overhead
- May need to adjust firewall rules on target hosts

### VPN over SSH Tunnel
- Add additional timeout padding in `config.py`
- Consider using compression: `ssh -C` for tunnel

## ✅ Verification Checklist

Before first use, verify:

- [ ] Python 3.13 installed
- [ ] Xcode Command Line Tools installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed without errors
- [ ] VPN connected and routing to remote networks
- [ ] Can ping remote hosts
- [ ] Can connect to ports 22 and 5985/5986
- [ ] Application launches without tkinter errors
- [ ] Credentials added for test host
- [ ] Connection test successful

## 📚 Additional Resources

- Main documentation: [README.md](README.md)
- Quick start guide: [QUICKSTART.md](QUICKSTART.md)
- Example scripts: `examples/` directory

## 🆘 Getting Help

If you encounter issues specific to macOS:

1. Check macOS version compatibility (macOS 10.14+)
2. Review system logs: `Console.app` → search for "Python"
3. Test with examples first before custom scripts
4. Verify VPN connectivity with `nc` tests above

---

**You're ready to execute remotely from macOS! 🎉**
