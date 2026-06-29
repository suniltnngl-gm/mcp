
import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

def main():
    env_path = Path("/media/sunil-kr/storage/workspace/.env")
    load_dotenv(dotenv_path=env_path)
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file.")
    
    genai.configure(api_key=gemini_api_key)

    print("Available Gemini Models:")
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(f"  - {m.name} (Supports generateContent)")
        else:
            print(f"  - {m.name}")

if __name__ == "__main__":
    main()
