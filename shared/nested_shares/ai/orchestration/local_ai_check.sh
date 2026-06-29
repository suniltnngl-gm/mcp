#!/bin/bash
# Local AI Safety Check - Verify system can handle llama.cpp

echo "=== Local AI (llama.cpp) Safety Check ==="
echo ""

# Binary check
BINARY_PATH="./llama.cpp/main"
MODEL_PATH="./models/phi-3-mini-q4.gguf"

echo "Files:"
if [ -f "$BINARY_PATH" ]; then
    echo "  ✅ llama.cpp binary found"
    BINARY_OK=1
else
    echo "  ❌ llama.cpp binary not found: $BINARY_PATH"
    BINARY_OK=0
fi

if [ -f "$MODEL_PATH" ]; then
    MODEL_SIZE=$(du -h "$MODEL_PATH" | cut -f1)
    echo "  ✅ Model found ($MODEL_SIZE)"
    MODEL_OK=1
else
    echo "  ❌ Model not found: $MODEL_PATH"
    MODEL_OK=0
fi

echo ""

# RAM check
AVAILABLE=$(free -m | awk 'NR==2{print $7}')
TOTAL=$(free -m | awk 'NR==2{print $2}')
USED_PERCENT=$(free | awk 'NR==2{printf "%.0f", $3/$2*100}')

echo "RAM:"
echo "  Total: ${TOTAL}MB"
echo "  Available: ${AVAILABLE}MB"
echo "  Used: ${USED_PERCENT}%"

if [ $AVAILABLE -lt 1000 ]; then
    echo "  ❌ Not enough RAM (need 1000MB for phi-3-mini)"
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

# Check for running llama.cpp processes
LLAMA_PROCS=$(pgrep -f "llama" | wc -l)
echo "Processes:"
echo "  llama.cpp running: $LLAMA_PROCS"

if [ $LLAMA_PROCS -gt 0 ]; then
    echo "  ⚠️  llama.cpp already running"
fi

echo ""
echo "=== Verdict ==="

if [ $BINARY_OK -eq 0 ] || [ $MODEL_OK -eq 0 ]; then
    echo "❌ Missing files"
    echo ""
    echo "Setup needed:"
    [ $BINARY_OK -eq 0 ] && echo "  1. Build llama.cpp: git clone https://github.com/ggerganov/llama.cpp && cd llama.cpp && make"
    [ $MODEL_OK -eq 0 ] && echo "  2. Download model: wget https://huggingface.co/.../phi-3-mini-q4.gguf -P models/"
    exit 1
fi

if [ $SAFE -eq 1 ]; then
    echo "✅ Safe to run llama.cpp (phi-3-mini)"
    echo ""
    echo "Recommendations:"
    echo "  - Use for quick tasks (<15s)"
    echo "  - Monitor: python3 local_ai_safety.py status"
    echo "  - Kill if needed: python3 local_ai_safety.py kill"
    exit 0
else
    echo "❌ Not safe to run llama.cpp"
    echo ""
    echo "Actions needed:"
    if [ $AVAILABLE -lt 1000 ]; then
        echo "  1. Close browser"
        echo "  2. Close IDE/VSCode"
        echo "  3. Close other apps"
    fi
    if [ $CPU -gt 80 ]; then
        echo "  1. Wait for CPU to settle"
        echo "  2. Check: top (find heavy processes)"
    fi
    echo ""
    echo "Alternative: Use cloud providers via smart_ai_router.py"
    exit 1
fi
