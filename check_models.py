import google.generativeai as genai
import os

# Paste your hardcoded key here for the test
API_KEY = "AIzaSyCCW4H8g9nWJi4hLsQDlkPlxCsqm7vnfQE" 

genai.configure(api_key=API_KEY)

print("Fetching available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")