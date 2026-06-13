import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load your API key
load_dotenv()

# Configure the SDK
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in .env file.")
    exit()

genai.configure(api_key=api_key)

print("--- Models available to your API Key ---")
try:
    models = genai.list_models()
    for m in models:
        # We only want models that support text/vision generation
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"❌ Error checking models: {e}")