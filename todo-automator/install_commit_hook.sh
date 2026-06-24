#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_SCRIPT="${SCRIPT_DIR}/monitor"

if [ ! -f "${MONITOR_SCRIPT}" ]; then
    echo "Error: monitor script not found in ${SCRIPT_DIR}"
    exit 1
fi

read -p "Enter the path to your git repository (default: current directory): " REPO_PATH
REPO_PATH=${REPO_PATH:-.}
REPO_PATH=$(realpath "${REPO_PATH}")

if [ ! -d "${REPO_PATH}/.git" ]; then
    echo "Error: ${REPO_PATH} is not a git repository"
    exit 1
fi

CONFIG_FILE="${SCRIPT_DIR}/config.json"
if [ -f "${CONFIG_FILE}" ]; then
    if command -v jq &> /dev/null; then
        jq --arg path "${REPO_PATH}" '.repo_path = $path' "${CONFIG_FILE}" > "${CONFIG_FILE}.tmp" && mv "${CONFIG_FILE}.tmp" "${CONFIG_FILE}"
        echo "✓ Updated config.json with repository path: ${REPO_PATH}"
    else
        echo "⚠ jq not found. Please manually update repo_path in config.json to: ${REPO_PATH}"
    fi
fi

HOOK_FILE="${REPO_PATH}/.git/hooks/post-commit"

cat > "${HOOK_FILE}" <<EOF
#!/bin/bash

export PATH=\$PATH:/usr/local/bin:/usr/bin
cd "${SCRIPT_DIR}"
"${MONITOR_SCRIPT}" --quiet &
EOF

chmod +x "${HOOK_FILE}"

echo "✓ Post-commit hook installed successfully!"
echo "  Hook location: ${HOOK_FILE}"
echo ""
echo "The monitor will now run automatically after each git commit."
echo "To test, make a commit in your repository."
echo ""
echo "To remove the hook:"
echo "  rm ${HOOK_FILE}"
