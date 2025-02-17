import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

class GeminiAI:
    def __init__(self, config, safety):
        API_KEY = os.getenv("GEMINI_API_KEY")
        if not API_KEY:
            print("[!] Oops, it was not possible to read the gemini API key, check if the .env file is formated correctly")
            return
        print("[LOADING GEMINI MODEL...]")
        self.client = genai.Client(api_key=API_KEY)
        self.chat = self.client.chats.create(model="gemini-2.0-flash-exp")
        self.safety = safety
        self.config = config

    def generate(self, prompt):
        response = self.chat.send_message(message=prompt, config=self.config)
        return response
    
    def generate_stream(self, prompt):
        response = self.chat.send_message_stream(message=prompt, config=self.config)
        return response

