import os
from google import genai
from dotenv import load_dotenv

# Load your API key
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in .env file.")
    exit()

try:
    # 1. The new SDK uses a Client object instead of genai.configure()
    client = genai.Client(api_key=api_key)

    print("--- Models available to your API Key ---")

    # 2. We use client.models.list() instead of genai.list_models()
    for model in client.models.list():
        # 3. The property is now called 'supported_actions'
        if 'generateContent' in model.supported_actions:
            print(f"✅ {model.name}")

except Exception as e:
    print(f"❌ Error checking models: {e}")