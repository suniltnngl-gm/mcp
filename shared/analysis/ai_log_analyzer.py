import os
import sys
import requests
import json

# --- Path and Environment Setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
LOG_FILE_PATH = os.path.join(PROJECT_ROOT, "logs", "ai-orchestrator-log.txt")
SUMMARY_FILE_PATH = os.path.join(PROJECT_ROOT, "logs", "ai_orchestrator_summary.txt")
ENV_FILE_PATH = os.path.join(PROJECT_ROOT, ".env")

# --- API Configuration ---
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
OPENROUTER_API_URL = "https://openrouter.ai/v1/chat/completions"
EDENAI_API_URL = "https://api.edenai.run/v2/text/chat"

# --- Prompt Creation Functions ---
def _create_summary_prompt(log_text):
    """Creates a prompt to summarize log text."""
    return (
        "You are an AI orchestration analysis expert. Analyze the following log entries from 'ai-orchestrator.sh' and provide a concise summary of the operations performed. "
        "Highlight any errors, warnings, or anomalies. If there are no errors, state that the operations completed successfully."
        f"""
You are an AI orchestration analysis expert. Analyze the following log entries from 'ai-orchestrator.sh' and provide a concise summary of the operations performed. Highlight any errors, warnings, or anomalies. If there are no errors, state that the operations completed successfully.
--- LOG ENTRIES ---
{log_text}
--- END OF LOGS ---"""
    )

def _create_suggestions_prompt(summary_text):
    """Creates a prompt for AI to provide suggestions based on a summary."""
    return (
        "You are an AI orchestration expert. Analyze the following summary of log entries and provide actionable suggestions to improve the orchestrator's performance, efficiency, and error handling. "
        "Provide your response as a list of bullet points."
        f"--- SUMMARY ---\n{summary_text}\n--- END OF SUMMARY ---"
    )

# --- Generic API Request Function ---
def _make_api_request(url, headers, json_payload, params=None):
    """A generic function to make API requests with unified error handling."""
    try:
        response = requests.post(url, headers=headers, params=params, json=json_payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

# --- Summarization Function (Gemini Only) ---
def get_summary_from_gemini(log_text, api_key):
    """Gets a summary of log text using the Gemini API."""
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}
    prompt = _create_summary_prompt(log_text)
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    response_data = _make_api_request(GEMINI_API_URL, headers=headers, json_payload=payload, params=params)

    if "error" in response_data:
        return response_data

    try:
        return {"summary": response_data["candidates"][0]["content"]["parts"][0]["text"]}
    except (KeyError, IndexError):
        return {"error": "Failed to parse Gemini API response", "details": response_data}

# --- Suggestion Functions (Other APIs) ---
def get_suggestions_from_mistral(summary_text, api_key):
    """Gets suggestions from the Mistral API based on a summary."""
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    prompt = _create_suggestions_prompt(summary_text)
    payload = {"model": "mistral-tiny", "messages": [{"role": "user", "content": prompt}]}
    response_data = _make_api_request(MISTRAL_API_URL, headers=headers, json_payload=payload)

    if "error" in response_data:
        return response_data

    try:
        return {"suggestion": response_data["choices"][0]["message"]["content"]}
    except (KeyError, IndexError):
        return {"error": "Failed to parse Mistral API response", "details": response_data}

def get_suggestions_from_openrouter(summary_text, api_key):
    """Gets suggestions from the OpenRouter API based on a summary."""
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    prompt = _create_suggestions_prompt(summary_text)
    payload = {"model": "mistralai/mistral-7b-instruct", "messages": [{"role": "user", "content": prompt}]}
    response_data = _make_api_request(OPENROUTER_API_URL, headers=headers, json_payload=payload)

    if "error" in response_data:
        return response_data

    try:
        return {"suggestion": response_data["choices"][0]["message"]["content"]}
    except (KeyError, IndexError):
        return {"error": "Failed to parse OpenRouter API response", "details": response_data}

def get_suggestions_from_edenai(summary_text, api_key):
    """Gets suggestions from the Eden AI API based on a summary."""
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    prompt = _create_suggestions_prompt(summary_text)
    payload = {"providers": "openai", "text": prompt, "chatbot_global_action": "Act as an assistant"}
    response_data = _make_api_request(EDENAI_API_URL, headers=headers, json_payload=payload)

    if "error" in response_data:
        return response_data

    try:
        if response_data.get("openai", {}).get("status") == "success":
            return {"suggestion": response_data["openai"]["generated_text"]}
        else:
            return {"error": "Eden AI request failed", "details": response_data.get("openai", {}).get("error", {})}
    except (KeyError, IndexError):
        return {"error": "Failed to parse Eden AI API response", "details": response_data}

# --- Provider Mapping for Suggestions ---
SUGGESTION_PROVIDER_MAP = {
    "mistral": (get_suggestions_from_mistral, "MISTRAL_API_KEY"),
    "openrouter": (get_suggestions_from_openrouter, "OPENROUTER_API_KEY"),
    "edenai": (get_suggestions_from_edenai, "EDENAI_API_KEY"),
}

# --- Main Execution Logic ---
def main():
    """Main function to orchestrate log summarization and suggestion generation."""
    try:
        with open(LOG_FILE_PATH, "r") as f:
            log_text = f.read()
    except FileNotFoundError:
        print(f"Error: Log file not found at {LOG_FILE_PATH}", file=sys.stderr)
        sys.exit(1)

    # Step 1: Get summary from Gemini
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY not found in .env file.", file=sys.stderr)
        sys.exit(1)

    print("Generating summary with Gemini...")
    summary_result = get_summary_from_gemini(log_text, gemini_api_key)

    if "error" in summary_result:
        print(f"Error getting summary from Gemini: {summary_result['error']}", file=sys.stderr)
        if "details" in summary_result:
            print(f"Details: {summary_result['details']}", file=sys.stderr)
        sys.exit(1)

    summary_text = summary_result["summary"]
    print("---" + "-" * 10 + " Summary " + "-" * 10 + "---")
    print(summary_text)
    print("-" * 30)

    # Save the summary to a file
    with open(SUMMARY_FILE_PATH, "w") as f:
        f.write(summary_text)

    # Step 2: Get suggestions from other providers
    print("\nGetting suggestions from other AI providers...")
    all_suggestions = {}
    for provider_name, (suggestion_function, key_name) in SUGGESTION_PROVIDER_MAP.items():
        api_key = os.getenv(key_name)
        if api_key:
            print(f"- Getting suggestions from {provider_name}...")
            result = suggestion_function(summary_text, api_key)
            all_suggestions[provider_name] = result
        else:
            print(f"- Skipping {provider_name}: API key not found.")

    # Step 3: Display suggestions
    print("\n--- Suggestions ---")
    for provider_name, result in all_suggestions.items():
        print(f"\n--- From {provider_name} ---")
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            if "details" in result:
                print(f"Details: {result['details']}", file=sys.stderr)
        else:
            print(result.get("suggestion", "No suggestion returned."))
    print("---------------------")

if __name__ == "__main__":
    main()
