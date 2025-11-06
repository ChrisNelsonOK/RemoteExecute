# Quick Start Guide - Remote Execute

Get up and running in 5 minutes!

## 🚀 Installation

### Windows
1. Double-click `run.bat`
   - The script will automatically install dependencies
   - The application will launch

### Linux/Mac
1. Open terminal in the RemoteExecute directory
2. Run:
   ```bash
   ./run.sh
   ```
   - Or manually: `python3 main.py`

## 📝 First-Time Setup

### Step 1: Add Your First Credential

1. Click **"Manage Credentials"** button (top right)
2. Click **"Add Credential"** (green button)
3. Fill in the form:

   **For Windows Local:**
   - Host/IP: `192.168.1.100` (your Windows PC)
   - Type: `Windows Local`
   - Username: `Administrator`
   - Password: `your_password`
   - Description: `My Windows PC`

   **For Linux:**
   - Host/IP: `192.168.1.50` (your Linux server)
   - Type: `Linux`
   - Username: `your_username`
   - Password: `your_password`
   - Description: `My Ubuntu Server`

4. Click **"Save"**
5. Close the Credential Manager window

### Step 2: Test Connection

1. In the main window, type your host IP in the **"Host/IP"** field
2. Select the credential you just created from the dropdown
3. Click **"Test Connection"** button
4. Check the output window for connection status

### Step 3: Run Your First Script

1. Click **"Browse Files"**
2. Navigate to the `examples` folder
3. Select `hello_world.py`
4. Click **"▶ EXECUTE"** (big green button)
5. Watch the output appear in real-time!

## 🎯 Try More Examples

### System Information
- Windows: `examples/windows_info.ps1`
- Linux: `examples/linux_info.sh`
- Cross-platform: `examples/system_info.py`

## ✍️ Create Your Own Script

1. Click **"Create New Script"** button
2. Enter a filename: `my_script.py`
3. Select script type: `Python (.py)`
4. Click **"Load Template"** for starter code
5. Write your script
6. Click **"Save and Use"**
7. Click **"▶ EXECUTE"**

## 🔧 Common Tasks

### Execute Multiple Files
1. Click "Browse Files"
2. Hold Ctrl (Windows/Linux) or Cmd (Mac)
3. Select multiple files
4. Click "▶ EXECUTE"
5. Files execute in order

### View Execution History
- Currently in database only
- Use SQLite browser to view `credentials.db`
- History viewer UI coming soon!

### Update Credentials
1. Click "Manage Credentials"
2. Click on a credential line (not the header)
3. Click "Edit Selected"
4. Make changes
5. Click "Save"

## ⚠️ Troubleshooting

### "Connection failed" on Windows
- Ensure WinRM is enabled (see README.md)
- Check firewall allows port 5985
- Verify credentials are correct

### "Authentication failed" on Linux
- Verify SSH is running: `sudo systemctl status ssh`
- Check username/password
- Ensure port 22 is open

### Script runs but no output
- Check if interpreter is installed on target system
- Python scripts need Python installed
- PowerShell scripts need PowerShell

### "Permission denied" errors
- Ensure user has appropriate permissions
- Windows: User needs admin rights for many operations
- Linux: Use sudo in your script if needed

## 💡 Tips

1. **Use descriptive credential names** in the Description field
2. **Test connection first** before executing scripts
3. **Start with simple scripts** (like hello_world.py)
4. **Check the output window** for detailed error messages
5. **Use the script editor** for quick tests and modifications

## 📚 Next Steps

- Read the full [README.md](README.md) for advanced features
- Explore security considerations
- Learn about customization options
- Check out the example scripts

## 🆘 Need Help?

- Check README.md for detailed documentation
- Review example scripts for reference
- Open an issue on GitHub

---

**You're ready to go! Happy remote executing! 🎉**
