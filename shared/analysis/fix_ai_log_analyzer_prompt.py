import re
import os

file_path = os.path.join(os.path.dirname(__file__), "ai_log_analyzer.py")

old_str = '''def _create_summary_prompt(log_text):
    """Creates a prompt to summarize log text."""
    return f"""You are an AI orchestration analysis expert. Analyze the following log entries from 'ai-orchestrator.sh' and provide a concise summary of the operations performed. Highlight any errors, warnings, or anomalies. If there are no errors, state that the operations completed successfully.
---
--- LOG ENTRIES ---
{log_text}
---
--- END OF LOGS ---"""'''

new_str = '''def _create_summary_prompt(log_text):
    """Creates a prompt to summarize log text."""
    return (
        "You are an AI orchestration analysis expert. Analyze the following log entries from 'ai-orchestrator.sh' and provide a concise summary of the operations performed. Highlight any errors, warnings, or anomalies. If there are no errors, state that the operations completed successfully.\n"
        "--- LOG ENTRIES ---\\n"
        f"{{log_text}}\\n"
        "--- END OF LOGS ---"
    )'''

try:
    with open(file_path, "r") as f:
        content = f.read()

    # Escape special characters in old_str for regex, but keep f-string placeholder as is
    # The f-string placeholder {log_text} needs to be treated as a literal string in the regex pattern.
    # re.escape will escape the curly braces, so we need to unescape them for the placeholder.
    old_str_escaped = re.escape(old_str).replace("\\{log_text\\}", "{log_text}")

    # For the new_str, ensure f-string curly braces are escaped for the literal string
    # and then unescape the f-string placeholder for the actual replacement.
    new_str_literal = new_str.replace("{", "{{").replace("}", "}}")
    new_str_literal = new_str_literal.replace("{{log_text}}", "{log_text}")

    new_content = re.sub(old_str_escaped, new_str_literal, content, flags=re.DOTALL)

    if new_content == content:
        print(
            f"No changes needed in {file_path}. Content already matches expected format."
        )
    else:
        with open(file_path, "w") as f:
            f.write(new_content)
        print(f"Successfully updated {file_path}")

except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")
