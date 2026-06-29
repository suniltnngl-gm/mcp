import os
import sys
from ai_log_analyzer import (
    get_available_provider,
    PROVIDER_MAP,
    LOG_FILE_PATH,
)

def create_error_review_prompt(error_logs):
    """Creates a specialized prompt for analyzing and fixing errors."""
    return (
        "You are a senior software engineer conducting a post-mortem on a script failure. "
        "Analyze the following error logs from an AI orchestration script. "
        "For each error, provide:\n"
        "1. A brief, clear explanation of the likely root cause (e.g., 'Invalid API key', 'Network timeout', 'Incorrect JSON payload').\n"
        "2. A specific, actionable suggestion to fix the issue (e.g., 'Verify the MISTRAL_API_KEY in the .env file', 'Check the system's internet connection').\n\n"
        f"--- ERROR LOGS ---\n{error_logs}\n--- END OF LOGS ---"
    )

def main():
    """
    Filters for errors in the log file and sends them to an AI for analysis.
    """
    try:
        if not os.path.exists(LOG_FILE_PATH):
            print(f"Log file not found at {LOG_FILE_PATH}. No errors to review.", file=sys.stderr)
            sys.exit(0)

        with open(LOG_FILE_PATH, 'r') as f:
            lines = f.readlines()

        error_lines = [line.strip() for line in lines if "ERROR:" in line]

        if not error_lines:
            print("✅ No errors found in the log file. System is healthy.")
            sys.exit(0)

        print(f"Found {len(error_lines)} error(s). Sending for analysis...")
        error_log_text = "\n".join(error_lines)

        analysis_function, api_key, provider_name = get_available_provider()
        prompt = create_error_review_prompt(error_log_text)

        # Re-use the analysis function from the main analyzer
        result = analysis_function(prompt, api_key)

        print(f"\n--- AI Error Analysis ({provider_name}) ---")
        print(result.get("summary", "Could not get a summary from the AI."))
        print("-------------------------------------\n")

    except Exception as e:
        print(f"An unexpected error occurred during error review: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
