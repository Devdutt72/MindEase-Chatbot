import os
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from django.conf import settings

# --- CONFIGURATION ---
# PASTE YOUR NEW API KEY DIRECTLY INSIDE THE QUOTES BELOW
genai.configure(api_key="AIzaSyCCW4H8g9nWJi4hLsQDlkPlxCsqm7vnfQE") 

class AIService:
    
    @staticmethod
    def check_safety(user_text):
        """
        Pillar 2: Safety Layer.
        Uses the ultra-fast 'Flash-Lite' model.
        """
        try:
            # Using the LITE model from your list
            model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-09-2025")
            
            prompt = f"""
            Task: Classify if this text indicates immediate crisis, self-harm, or severe violence.
            Input: "{user_text}"
            Output ONLY: 'SAFE' or 'UNSAFE'
            """
            
            response = model.generate_content(prompt)
            result = response.text.strip().upper()
            
            if "UNSAFE" in result:
                return False, "Crisis Detected"
            return True, "Safe"

        except Exception as e:
            print(f"Safety Check Warning: {e}")
            return True, "Check Skipped"

    @staticmethod
    def generate_response(user_text, context_summary=""):
        """
        Pillar 1: Therapeutic Brain.
        SWITCHED TO 'Flash-Lite' to fix 429 Quota Error.
        It is less 'smart' than Pro but much faster and has higher free limits.
        """
        system_instruction = f"""
        You are MindEase, a compassionate mental health assistant.
        CONTEXT: {context_summary}
        RULES: Keep responses under 3 sentences. Validating tone.
        """

        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

        # *** THE FIX: Downgraded from 'gemini-3-pro' to 'flash-lite' ***
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite-preview-09-2025",
            system_instruction=system_instruction,
            safety_settings=safety_settings
        )

        try:
            response_stream = model.generate_content(
                user_text, 
                stream=True
            )

            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            yield f"I'm listening, but I'm having trouble connecting right now. ({str(e)})"