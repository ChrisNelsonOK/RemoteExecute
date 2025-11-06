#!/usr/bin/env python3
"""
Cross-platform system information script
Works on both Windows and Linux
"""
import platform
import socket
import os
from datetime import datetime

def main():
    print("=" * 60)
    print("SYSTEM INFORMATION REPORT")
    print("=" * 60)
    print()

    # System info
    print(f"Operating System: {platform.system()}")
    print(f"OS Version: {platform.version()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Hostname: {socket.gethostname()}")
    print(f"Processor: {platform.processor()}")
    print()

    # Python info
    print(f"Python Version: {platform.python_version()}")
    print()

    # Network info
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        print(f"IP Address: {ip_address}")
    except:
        print("IP Address: Unable to determine")
    print()

    # Disk usage (basic)
    if platform.system() == "Windows":
        import shutil
        total, used, free = shutil.disk_usage("C:\\")
        print(f"Disk C: Total: {total // (2**30)} GB, Free: {free // (2**30)} GB")
    else:
        import shutil
        total, used, free = shutil.disk_usage("/")
        print(f"Disk /: Total: {total // (2**30)} GB, Free: {free // (2**30)} GB")

    print()
    print("=" * 60)
    print(f"Report generated: {datetime.now()}")
    print("=" * 60)

if __name__ == "__main__":
    main()
