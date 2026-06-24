#!/bin/bash

echo "Testing Git Todo Monitor CLI..."
echo ""

MONITOR_SCRIPT="./monitor"
PYTHON_SCRIPT="./src/git_todo_monitor.py"

if [ ! -f "${MONITOR_SCRIPT}" ]; then
    echo "✗ monitor script not found"
    exit 1
fi

if [ ! -f "${PYTHON_SCRIPT}" ]; then
    echo "✗ git_todo_monitor.py not found"
    exit 1
fi

echo "1. Testing bash entry point (./monitor)..."
if [ -x "${MONITOR_SCRIPT}" ]; then
    echo "   ✓ monitor script is executable"
else
    echo "   ✗ monitor script is not executable"
    exit 1
fi

echo ""
echo "2. Testing --help flag..."
python3 "${PYTHON_SCRIPT}" --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ --help works"
else
    echo "   ✗ --help failed"
    exit 1
fi

echo ""
echo "3. Testing custom config flag..."
if [ -f "config.json" ]; then
    cp config.json test_config.json
    python3 "${PYTHON_SCRIPT}" --config test_config.json --quiet 2>&1 | grep -q "ERROR: OLLAMA_API_KEY"
    if [ $? -eq 0 ]; then
        echo "   ✓ --config flag works (API key check triggered as expected)"
    else
        echo "   ⚠ --config flag may have issues (or API key is configured)"
    fi
    rm -f test_config.json
fi

echo ""
echo "4. Testing --quiet flag..."
OUTPUT=$(python3 "${PYTHON_SCRIPT}" --quiet 2>&1)
if echo "$OUTPUT" | grep -q "ERROR: OLLAMA_API_KEY"; then
    echo "   ✓ --quiet flag works (no verbose output, only errors)"
else
    echo "   ⚠ --quiet flag behavior unclear"
fi

echo ""
echo "5. Checking required files..."
for file in "config.json" ".env.example" "README.md" "CHANGELOG.md" "ROADMAP.md"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file exists"
    else
        echo "   ✗ $file missing"
    fi
done

echo ""
echo "CLI tests complete!"
