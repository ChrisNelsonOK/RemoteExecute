#!/usr/bin/env python3
"""
Simple Hello World test script
Perfect for testing remote execution
"""
import platform
import sys
from datetime import datetime

def main():
    print("*" * 50)
    print("HELLO FROM REMOTE EXECUTE!")
    print("*" * 50)
    print()
    print(f"Timestamp: {datetime.now()}")
    print(f"Running on: {platform.system()} {platform.release()}")
    print(f"Hostname: {platform.node()}")
    print(f"Python version: {sys.version.split()[0]}")
    print()
    print("Remote execution successful! ✓")
    print("*" * 50)

if __name__ == "__main__":
    main()
