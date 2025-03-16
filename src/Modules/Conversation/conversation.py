import logging
import threading
from Services.Output.Text_to_Speech.text_to_speech import TextToSpeech
from Services.Output.gemini_ai import GeminiAI
from google.genai import types
import json
import time
import os

DIRNAME = os.path.dirname(os.path.abspath(__file__))
PRESETS_DIR = os.path.join(DIRNAME, "Presets")
INSTRUCTIONS_DIR = os.path.join(DIRNAME, "Instructions")

logging.basicConfig(
    filename=os.path.join(DIRNAME, f"Logs/{time.time()}.log"),
    encoding='utf-8',
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class ConversationModule:
    def __init__(self, preset):
        self.logger = logging.getLogger(__name__)

        with open(os.path.join(PRESETS_DIR, f"{preset}.json"), 'r', encoding="utf-8") as file:
            self.preset = json.load(file)

        with open(os.path.join(INSTRUCTIONS_DIR, f"{self.preset['instructions_file']}.txt"), 'r', encoding="utf-8") as file:
            self.instructions = file.read()

        for key, value in self.preset.items():
            self.instructions = self.instructions.replace("{"+key+"}", str(value))

        self.config = types.GenerateContentConfig(
            system_instruction=self.instructions,
            max_output_tokens=self.preset["max_output_tokens"],
            temperature=self.preset["temperature"],
            frequency_penalty=self.preset["frequency_penalty"],
            safety_settings=[
                {"category": types.HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": types.HarmBlockThreshold.BLOCK_NONE},
                {"category": types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": types.HarmBlockThreshold.BLOCK_NONE},
                {"category": types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, "threshold": types.HarmBlockThreshold.BLOCK_NONE},
                {"category": types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": types.HarmBlockThreshold.BLOCK_NONE},
                {"category": types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY, "threshold": types.HarmBlockThreshold.BLOCK_NONE}
            ]
        )

        self.ai = GeminiAI(model=self.preset["model"], config=self.config, error_responses=self.preset["error_responses"], logger=logging.getLogger(f"{__name__} ({self.preset['name']})"))
        self.tts = TextToSpeech(model=self.preset["voice"], config=self.preset["voice"], logger=logging.getLogger(f"{__name__} ({self.preset['name']})"))
        
        self.output_locked = False
        print("Conversation initialized")

    def send(self, author, text):
        if text == "": 
            return
        text_to_send = f"[{author} said] {text}"
        print("Sending: " + text_to_send)

        if self.output_locked == True: 
            self.ai.append_to_chat(text=text_to_send)
            return None
        
        self.output_locked = True
        response = self.ai.generate(prompt=text_to_send)
        responseText = response.text.strip()
        print("Received: " + responseText)
        words = responseText.split()
        audio = None
        if len(words) > 0 and not responseText == "<no response>":
            audio = self.tts.synthesize(responseText)
        else:
            self.output_locked = False
        return {
            'text': responseText,
            'audio': audio
        }
           
    def unlock_outputting(self):
        self.output_locked = False

    def interrupt_tts_stream(self):
        self.tts.interrupt_stream()
        self.logger.info("Stream interrupted")

    def get_ai_history(self):
        return self.ai.chat.get_history()
