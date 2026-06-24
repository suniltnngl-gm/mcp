#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="${SCRIPT_DIR}/src/git_todo_monitor.py"

echo "Setting up hourly cron job for Git Todo Monitor..."
echo ""
echo "This script will add a cron job that runs every hour."
echo "Script location: ${SCRIPT_PATH}"
echo ""

read -p "Enter the absolute path to your git repository (default: ${SCRIPT_DIR}): " REPO_PATH
REPO_PATH=${REPO_PATH:-${SCRIPT_DIR}}

read -p "Enter time window in hours to check for changes (default: 1): " TIME_WINDOW
TIME_WINDOW=${TIME_WINDOW:-1}

cat > "${SCRIPT_DIR}/config.json" <<EOF
{
  "repo_path": "${REPO_PATH}",
  "time_window_hours": ${TIME_WINDOW},
  "log_file": "${SCRIPT_DIR}/todo_monitor.log",
  "notification_timeout": 10000
}
EOF

echo "Configuration updated in config.json"
echo ""

if [ ! -f "${SCRIPT_DIR}/.env" ]; then
    echo "Creating .env file..."
    read -p "Enter your Ollama Cloud API key (or set OLLAMA_API_KEY in ~/Public/ENV/.env): " OLLAMA_KEY
    echo "OLLAMA_API_KEY=${OLLAMA_KEY}" > "${SCRIPT_DIR}/.env"
    chmod 600 "${SCRIPT_DIR}/.env"
    echo ".env file created"
fi

chmod +x "${SCRIPT_PATH}"

CRON_JOB="0 * * * * cd ${SCRIPT_DIR} && /usr/bin/python3 ${SCRIPT_PATH} >> ${SCRIPT_DIR}/cron.log 2>&1"

(crontab -l 2>/dev/null | grep -v "${SCRIPT_PATH}"; echo "${CRON_JOB}") | crontab -

echo ""
echo "✓ Cron job installed successfully!"
echo ""
echo "The script will run every hour at :00 minutes."
echo "Logs will be saved to: ${SCRIPT_DIR}/cron.log"
echo "Summaries will be saved to: ${SCRIPT_DIR}/todo_monitor.log"
echo ""
echo "To verify installation, run: crontab -l"
echo "To remove the cron job, run: crontab -e"
echo ""
echo "Testing the script now..."
cd "${SCRIPT_DIR}" && python3 "${SCRIPT_PATH}"
