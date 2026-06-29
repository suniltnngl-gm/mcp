#!/bin/bash
# Quick access to AI orchestration tools

AI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$1" in
    orchestrate)
        python3 "$AI_DIR/ai_orchestra.py" "${@:2}"
        ;;
    cli)
        python3 "$AI_DIR/orchestra_cli.py" "${@:2}"
        ;;
    config)
        python3 "$AI_DIR/ai_autoconfig.py" "${@:2}"
        ;;
    context)
        python3 "$AI_DIR/auto_context_manager.py" "${@:2}"
        ;;
    balance)
        python3 "$AI_DIR/load_balancer.py" "${@:2}"
        ;;
    health)
        python3 "$AI_DIR/health_monitor.py" "${@:2}"
        ;;
    list)
        echo "Available AI tools:"
        ls -1 "$AI_DIR"/*.py | xargs -n1 basename
        ;;
    *)
        echo "Usage: use_ai_tools.sh {orchestrate|cli|config|context|balance|health|list}"
        echo ""
        echo "Commands:"
        echo "  orchestrate - Run AI orchestration"
        echo "  cli         - Use orchestra CLI"
        echo "  config      - Auto-configure AI"
        echo "  context     - Manage context"
        echo "  balance     - Load balancing"
        echo "  health      - Health monitoring"
        echo "  list        - List all tools"
        ;;
esac
