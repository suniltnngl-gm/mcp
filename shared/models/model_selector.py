import json
import os
from pathlib import Path
import google.generativeai as genai

class ModelSelector:
    def __init__(self, cache_path=".models_cache.json"):
        self.cache_path = Path(cache_path)
        self.available_models = self._load_models()

    def _load_models(self):
        """Load models from cache or fetch from API."""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # Cache is invalid, fetch from API
                pass
        
        return self._fetch_and_cache_models()

    def _fetch_and_cache_models(self):
        """Fetch the list of available models from the Gemini API and cache it."""
        print("Fetching available models from Gemini API...")
        try:
            models_list = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    models_list.append(m.name)
            
            with open(self.cache_path, 'w') as f:
                json.dump(models_list, f)
            
            return models_list
        except Exception as e:
            print(f"Warning: Could not fetch models from API: {e}")
            # Return a default list in case of API failure
            return []

    def select_model(self):
        """Select the best available model from a preferred list."""
        # Preferred models, from newest/best to oldest/most basic
        preferred_models = [
            'models/gemini-2.5-pro',
            'models/gemini-pro-latest',
            'models/gemini-2.5-flash',
            'models/gemini-flash-latest',
        ]

        if not self.available_models:
            print("Warning: No available models found. Falling back to default.")
            return 'gemini-1.5-flash' # A sensible default

        for model in preferred_models:
            if model in self.available_models:
                print(f"Selected model: {model}")
                return model
        
        # If no preferred models are found, return the first available one
        fallback_model = self.available_models[0]
        print(f"Warning: No preferred models found. Falling back to: {fallback_model}")
        return fallback_model

    def refresh_cache(self):
        """Force a refresh of the model cache."""
        self._fetch_and_cache_models()
