#!/bin/bash
# Linux System Information Script
# For Ubuntu/Debian systems

echo "========================================"
echo "LINUX SYSTEM INFORMATION"
echo "========================================"
echo ""

# System Info
echo "Hostname: $(hostname)"
echo "OS: $(lsb_release -d | cut -f2)"
echo "Kernel: $(uname -r)"
echo "Architecture: $(uname -m)"
echo ""

# Current User
echo "Current User: $(whoami)"
echo "Home Directory: $HOME"
echo ""

# Uptime
echo "System Uptime:"
uptime
echo ""

# Memory Info
echo "Memory Information:"
free -h
echo ""

# Disk Usage
echo "Disk Usage:"
df -h | grep -E '^/dev/'
echo ""

# Network Interfaces
echo "Network Interfaces:"
ip addr show | grep -E '^[0-9]+:' | awk '{print $2}' | sed 's/://'
echo ""

# Active Network Connections
echo "Active Network Connections:"
ip addr show | grep 'inet ' | awk '{print $2}'
echo ""

# Top 10 Processes by Memory
echo "Top 10 Processes by Memory:"
ps aux --sort=-%mem | head -11
echo ""

# Load Average
echo "Load Average:"
cat /proc/loadavg
echo ""

# Listening Ports
echo "Listening Ports:"
if command -v ss &> /dev/null; then
    ss -tlnp 2>/dev/null | grep LISTEN | head -10
elif command -v netstat &> /dev/null; then
    netstat -tlnp 2>/dev/null | grep LISTEN | head -10
else
    echo "Neither ss nor netstat available"
fi
echo ""

echo "========================================"
echo "Report completed: $(date)"
echo "========================================"
