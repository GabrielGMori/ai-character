from copy import deepcopy
import os
from random import randint
import time
from dotenv import load_dotenv
from google import genai
import logging

load_dotenv()

class GenericResponse:
    def __init__(self, text):
        self.text = text

class GeminiAI:
    def __init__(self, model, config, error_responses=["Something went wrong with my AI"], logger=logging.getLogger(__name__)):
        self.logger = logger

        API_KEY = os.getenv("GEMINI_API_KEY")
        if not API_KEY:
            logger.critical("It was not possible to read the gemini API key, check if the .env file is formated correctly")
            raise Exception("It was not possible to read the gemini API key, check if the .env file is formated correctly")
        
        self.logger.info("Loading gemini model...")
        self.client = genai.Client(api_key=API_KEY)
        self.chat = self.client.chats.create(model=model)
        self.config = config
        self.error_responses = error_responses
        self.logger.info("Gemini model ready!")

    def generate(self, prompt, config=None, max_retries=3, delay=1):
        if config == None:
            config = self.config
        for i in range(max_retries):
            try:
                response = self.chat.send_message(message=prompt, config=config)
                break
            except Exception as exception:
                self.logger.error(exception)
                self.logger.error(f"Could not generate content {i+1}/{max_retries}")
                if i == max_retries-1:
                    response = GenericResponse(text=self.error_responses[randint(0, len(self.error_responses)-1)])
                    break
            time.sleep(delay)
        self.logger.info(f"Generated content: {response.text}")
        return response
    
    def append_to_chat(self, text):
        config = deepcopy(self.config)
        config.max_output_tokens = 1
        self.generate(prompt=text, config=config)
        self.logger.info(f"Appended to chat: {text}")
