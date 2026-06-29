#!/usr/bin/env python3
"""Tool Manager CLI: Comprehensive tool management interface"""
import sys
from tools_manager import *
from tool_helpers import *


def show_help():
    print(
        """
Tool Manager CLI

USAGE:
  tool list [category]           - List all tools
  tool stats <name>              - Show tool statistics
  tool health                    - Show tool health summary
  tool execute <name> [args]     - Execute a tool
  
  tool discuss add <review_id> <type> <user> <msg>  - Add discussion
  tool discuss list <review_id> <type>              - List discussions
  tool discuss resolve <id>                         - Resolve discussion
  
  tool admin disable <user> <id> <reason>  - Disable tool
  tool admin enable <user> <id>            - Enable tool
  tool admin reset <user> <id>             - Reset tool stats
  tool admin logs                          - Show admin logs
"""
    )


def main():
    if len(sys.argv) < 2:
        show_help()
        return

    cmd = sys.argv[1]

    if cmd == "list":
        category = sys.argv[2] if len(sys.argv) > 2 else None
        tools = list_tools(category=category)
        for t in tools:
            print(f"[{t[0]}] {t[1]} ({t[2]}) - {t[3] or 'No description'}")

    elif cmd == "stats" and len(sys.argv) >= 3:
        name = sys.argv[2]
        stats = get_tool_stats(name)
        if stats:
            print(f"\nTool: {stats['name']}")
            print(f"Usage: {stats['usage_count']}")
            print(f"Success Rate: {stats['success_rate']:.1f}%")
            print(f"Avg Runtime: {stats['avg_runtime']:.3f}s")
        else:
            print("Tool not found")

    elif cmd == "health":
        summary = get_tool_health_summary()
        print("\n🔧 Tool Health Summary")
        print(f"Status: {summary['status_counts']}")
        print(f"Avg Success Rate: {summary['avg_success_rate']}%")

    elif cmd == "execute" and len(sys.argv) >= 3:
        name = sys.argv[2]
        args = sys.argv[3:] if len(sys.argv) > 3 else None
        result = execute_tool(name, args)
        print(result.get("output", result.get("error", "No output")))

    elif cmd == "discuss":
        if len(sys.argv) < 3:
            print("Usage: tool discuss <add|list|resolve> ...")
            return
        subcmd = sys.argv[2]
        if subcmd == "add" and len(sys.argv) >= 7:
            review_id = int(sys.argv[3])
            review_type = sys.argv[4]
            user = sys.argv[5]
            message = " ".join(sys.argv[6:])
            disc_id = add_discussion(review_id, review_type, user, message)
            print(f"✓ Discussion #{disc_id} added")
        elif subcmd == "list" and len(sys.argv) >= 5:
            review_id = int(sys.argv[3])
            review_type = sys.argv[4]
            discussions = get_discussions(review_id, review_type)
            for d in discussions:
                status = "✓" if d["resolved"] else "○"
                print(f"{status} [{d['user']}] {d['message']}")
        elif subcmd == "resolve" and len(sys.argv) >= 4:
            disc_id = int(sys.argv[3])
            resolve_discussion(disc_id)
            print("✓ Discussion resolved")

    elif cmd == "admin":
        if len(sys.argv) < 3:
            print("Usage: tool admin <disable|enable|reset|logs> ...")
            return
        subcmd = sys.argv[2]
        if subcmd == "disable" and len(sys.argv) >= 6:
            admin_user = sys.argv[3]
            tool_id = int(sys.argv[4])
            reason = " ".join(sys.argv[5:])
            admin_disable_tool(admin_user, tool_id, reason)
            print(f"✓ Tool #{tool_id} disabled")
        elif subcmd == "enable" and len(sys.argv) >= 5:
            admin_user = sys.argv[3]
            tool_id = int(sys.argv[4])
            admin_enable_tool(admin_user, tool_id)
            print(f"✓ Tool #{tool_id} enabled")
        elif subcmd == "reset" and len(sys.argv) >= 5:
            admin_user = sys.argv[3]
            tool_id = int(sys.argv[4])
            admin_reset_tool_stats(admin_user, tool_id)
            print(f"✓ Tool #{tool_id} stats reset")
        elif subcmd == "logs":
            logs = get_admin_logs()
            for log in logs:
                details = f" - {log['details']}" if log["details"] else ""
                print(
                    f"[{log['created_at']}] {log['admin']}: {log['action']} on {log['target_type']}#{log['target_id']}{details}"
                )

    else:
        show_help()


if __name__ == "__main__":
    main()
