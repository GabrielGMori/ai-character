from copy import deepcopy
import os
from random import randint
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
import logging

load_dotenv()

class GenericResponse:
    def __init__(self, text):
        self.text = text

class GeminiAI:
    def __init__(self, model, config, error_responses=["Something went wrong with my AI"], logger=logging.getLogger(__name__)):
        API_KEY = os.getenv("GEMINI_API_KEY")
        if not API_KEY:
            raise Exception("Oops, it was not possible to read the gemini API key, check if the .env file is formated correctly")
        self.logger = logger
        self.logger.info("LOADING GEMINI MODEL...")
        self.client = genai.Client(api_key=API_KEY)
        self.chat = self.client.chats.create(model=model)
        self.config = config
        self.error_responses = error_responses
        self.logger.info("GEMINI MODEL READY!")

    def generate(self, prompt, config=None, max_retries=3, delay=1):
        if config == None:
            config = self.config
        for i in range(max_retries):
            try:
                response = self.chat.send_message(message=prompt, config=config)
                break
            except Exception as exception:
                self.logger.error(exception)
                self.logger.error(f"COULD NOT GENERATE CONTENT {i+1}/{max_retries}")
                if i == max_retries-1:
                    response = GenericResponse(text=self.error_responses[randint(0, len(self.error_responses)-1)])
                    break
            time.sleep(delay)
        self.logger.info(f"GENERATED CONTENT: {response.text}")
        return response
    
    def append_to_chat(self, text):
        config = deepcopy(self.config)
        config.max_output_tokens = 1
        self.generate(prompt=text, config=config)
        self.logger.info(f"APPENDED TO CHAT: {text}")


