#!/bin/bash
# Ollama Safety Check - Verify system can handle local AI

echo "=== Ollama Safety Check ==="
echo ""

# RAM check
AVAILABLE=$(free -m | awk 'NR==2{print $7}')
TOTAL=$(free -m | awk 'NR==2{print $2}')
USED_PERCENT=$(free | awk 'NR==2{printf "%.0f", $3/$2*100}')

echo "RAM:"
echo "  Total: ${TOTAL}MB"
echo "  Available: ${AVAILABLE}MB"
echo "  Used: ${USED_PERCENT}%"

if [ $AVAILABLE -lt 1500 ]; then
    echo "  ❌ Not enough RAM (need 1500MB)"
    echo "  💡 Close browser/IDE to free memory"
    SAFE=0
else
    echo "  ✅ Sufficient RAM"
    SAFE=1
fi

echo ""

# CPU check
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 | cut -d'.' -f1)
echo "CPU:"
echo "  Usage: ${CPU}%"

if [ $CPU -gt 80 ]; then
    echo "  ❌ CPU too busy"
    echo "  💡 Wait for CPU to settle"
    SAFE=0
else
    echo "  ✅ CPU available"
fi

echo ""

# Swap check
SWAP_USED=$(free | awk 'NR==3{printf "%.0f", $3/$2*100}')
echo "Swap:"
echo "  Used: ${SWAP_USED}%"

if [ $SWAP_USED -gt 30 ]; then
    echo "  ⚠️  System using swap (will be slow)"
fi

echo ""

# Disk check
DISK_AVAIL=$(df -BG / | awk 'NR==2{print $4}' | sed 's/G//')
echo "Disk:"
echo "  Available: ${DISK_AVAIL}GB"

if [ $DISK_AVAIL -lt 5 ]; then
    echo "  ❌ Low disk space"
    SAFE=0
else
    echo "  ✅ Sufficient disk"
fi

echo ""
echo "=== Verdict ==="

if [ $SAFE -eq 1 ]; then
    echo "✅ Safe to run Ollama (phi:2.7b)"
    echo ""
    echo "Recommendations:"
    echo "  - Use for quick tasks (<10s)"
    echo "  - Monitor with: watch -n 1 free -h"
    echo "  - Stop if RAM >85%"
    exit 0
else
    echo "❌ Not safe to run Ollama"
    echo ""
    echo "Actions needed:"
    if [ $AVAILABLE -lt 1500 ]; then
        echo "  1. Close browser"
        echo "  2. Close IDE/VSCode"
        echo "  3. Close other apps"
    fi
    if [ $CPU -gt 80 ]; then
        echo "  1. Wait for CPU to settle"
        echo "  2. Check: top (find heavy processes)"
    fi
    echo ""
    echo "Alternative: Use cloud providers instead"
    exit 1
fi
