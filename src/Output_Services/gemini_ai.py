import os
from random import randint
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

class GenericResponse:
    def __init__(self, text):
        self.text = text

class GeminiAI:
    def __init__(self, model, config, error_responses=["Something went wrong with my AI"]):
        API_KEY = os.getenv("GEMINI_API_KEY")
        if not API_KEY:
            print("[!] Oops, it was not possible to read the gemini API key, check if the .env file is formated correctly")
            return
        print("[LOADING GEMINI MODEL...]")
        self.client = genai.Client(api_key=API_KEY)
        self.chat = self.client.chats.create(model="gemini-2.0-flash-exp")
        self.config = config
        self.error_responses = error_responses
        print("[GEMINI MODEL READY!]")

    def generate(self, prompt, max_retries=3, delay=1):
        for i in range(max_retries):
            try:
                response = self.chat.send_message(message=prompt, config=self.config)
                break
            except Exception as exception:
                print(f"[COULD NOT GENERATE CONTENT {i+1}/{max_retries}]")
                if i == max_retries-1:
                    response = GenericResponse(text=self.error_responses[randint(0, len(self.error_responses)-1)])
                    break
            time.sleep(delay)
                
        return response
    
    def append_to_chat(self, content):
        self.chat = self.client.chats.create(model="gemini-2.0-flash-exp", history = self.chat.get_history().append(content))
    
    def generate_stream(self, prompt):
        response = self.chat.send_message_stream(message=prompt, config=self.config)
        return response

