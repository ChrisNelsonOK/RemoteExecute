# Python 3.13 Compatibility

This application is fully compatible with Python 3.13 and has been updated to use the latest package versions.

## Updated Packages

All dependencies have been updated to versions that support Python 3.13:

- **customtkinter** >= 5.2.2 (UI framework)
- **paramiko** >= 3.5.0 (SSH client)
- **pywinrm** >= 0.5.0 (Windows Remote Management)
- **cryptography** >= 43.0.0 (Encryption)
- **requests** >= 2.32.0 (HTTP library)
- **Pillow** >= 10.4.0 (Image processing)

## Installation with Python 3.13

### macOS
```bash
# Install Python 3.13 via Homebrew
brew install python@3.13 python-tk@3.13

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Windows
```bash
# Download and install Python 3.13 from python.org
# Then:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Linux
```bash
# Install Python 3.13 (Ubuntu 24.04+)
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-tk

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Backward Compatibility

The application maintains backward compatibility with Python 3.8+ through 3.13. If you're using an older Python version (3.8-3.12), the dependencies will still work, but we recommend upgrading to Python 3.13 for:

- Better performance
- Improved security features
- Latest bug fixes
- Enhanced type checking

## Testing

All core functionality has been verified to work with Python 3.13:

- ✅ SQLite database operations
- ✅ Credential encryption/decryption
- ✅ SSH connections (Paramiko)
- ✅ WinRM connections
- ✅ CustomTkinter UI rendering
- ✅ File upload/download operations
- ✅ Script execution on remote hosts

## Known Issues

None identified with Python 3.13 at this time.

## Support

If you encounter any Python 3.13-specific issues, please:

1. Verify you're using the correct Python version: `python3 --version`
2. Ensure all dependencies are up to date: `pip install -r requirements.txt --upgrade`
3. Check that you're using a virtual environment
4. Review error messages in the application output

For additional help, see:
- [README.md](README.md)
- [MACOS_SETUP.md](MACOS_SETUP.md) (for macOS users)
- [QUICKSTART.md](QUICKSTART.md)
