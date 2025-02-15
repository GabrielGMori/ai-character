import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class GeminiAI:
    def __init__(self, instructions, temperature):
        API_KEY = os.getenv("GEMINI_API_KEY")
        if not API_KEY:
            print("[!] Oops, it was not possible to read the gemini API key, check if the .env file is formated correctly")
            return
        print("[LOADING GEMINI MODEL...]")
        self.client = genai.Client(api_key=API_KEY)
        self.chat = self.client.chats.create(model="gemini-2.0-flash")

        self.safety = [
            {"category": types.HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE},
            {"category": types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": types.HarmBlockThreshold.BLOCK_NONE},
            {"category": types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, "threshold": types.HarmBlockThreshold.BLOCK_ONLY_HIGH},
            {"category": types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": types.HarmBlockThreshold.BLOCK_NONE},
            {"category": types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY, "threshold": types.HarmBlockThreshold.BLOCK_NONE}
        ]

        self.config = types.GenerateContentConfig(
            system_instruction=instructions,
            max_output_tokens=1000,
            temperature=temperature,
            frequencyPenalty=1.5,
            safety_settings=self.safety
        )

    # def generate_no_history(self, prompt):
    #     response = self.client.models.generate_content(model="gemini-2.0-flash" [message=prompt, config=self.config])
    #     return response

    def generate(self, prompt):
        response = self.chat.send_message(message=prompt, config=self.config)
        return response
    
    def generate_stream(self, prompt):
        response = self.chat.send_message_stream(message=prompt, config=self.config)
        return response

