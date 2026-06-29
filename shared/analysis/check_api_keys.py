#!/usr/bin/env python3
"""
🔑 API Key Checker
==================

Utility to verify which AI provider API keys are configured.
"""

import os


def check_api_keys():
    """Check which API keys are configured and print their status."""

    print("🔑 API KEY CONFIGURATION CHECK")
    print("=============================")

    api_keys = {
        "GROQ_API_KEY": "Groq",
        "CEREBRAS_API_KEY": "Cerebras",
        "GEMINI_API_KEY": "Google Gemini",
        "AI21_API_KEY": "AI21 Labs",
        "COHERE_API_KEY": "Cohere",
        "TOGETHER_API_KEY": "Together AI",
    }

    configured = 0
    for env_var, provider_name in api_keys.items():
        if os.getenv(env_var):
            print(f"✅ {provider_name}: Configured")
            configured += 1
        else:
            print(f"❌ {provider_name}: Not configured")

    print(f"\n📊 Total configured: {configured}/{len(api_keys)} providers")

    if configured >= 2:
        print("🎉 Great! You have multiple providers configured.")
        print("Your AI Orchestra can provide redundancy and load balancing!")
    elif configured == 1:
        print("👍 Good start! Consider adding more providers for redundancy.")
    else:
        print("⚠️  No providers configured. Please set up API keys.")


if __name__ == "__main__":
    check_api_keys()
