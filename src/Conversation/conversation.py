import logging
import threading
from Output_Services.Text_to_Speech.text_to_speech import TextToSpeech
from Output_Services.gemini_ai import GeminiAI
from Input_Services.speech_to_text import SpeechToText
from google.genai import types
import json
import time
import os

MIC_INDEX = 1
PRESET_NAME = "Lula"

PRESETS_DIR = "src/Conversation/Presets/"
with open(os.path.join(PRESETS_DIR, f"{PRESET_NAME}.json"), 'r') as file:
    preset = json.load(file)

VOICES_DIR = "src/Output_Services/Text_to_Speech/Voices"
MODEL_PATH = os.path.abspath(VOICES_DIR + "/Models/" + preset["voice"] + ".onnx")
CONFIG_PATH = os.path.abspath(VOICES_DIR + "/Configs/" + preset["voice"] + ".onnx.json")

MODEL = preset["model"]

SAFETY = [
    {"category": types.HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": types.HarmBlockThreshold.BLOCK_NONE},
    {"category": types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": types.HarmBlockThreshold.BLOCK_NONE},
    {"category": types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, "threshold": types.HarmBlockThreshold.BLOCK_NONE},
    {"category": types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": types.HarmBlockThreshold.BLOCK_NONE},
    {"category": types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY, "threshold": types.HarmBlockThreshold.BLOCK_NONE}
]

INSTRUCTIONS = preset["instructions"] + """
\n
You should follow the character described above
Before messages you will have a brief description of where it is coming, for example "John said:" or "Gabriel sent on twitch chat:", you shouldn't respond to these descriptions, instead use them as context

REMEMBER THESE RULES:
1) Never use italic or bold (for instance, **)
2) Always answer in the language: """ + preset["language"] + """
3) Never get out of character
4) Never use emojis
5) Never use special characters, like "*(&$" only , and .

Give NO ANSWER (an empty string) when you don't need to respond
EXAMPLES:

User: "Ok, but what do you think about it?"
AI: "It seems pretty trash"

User: "Oh, I see"
AI: ""

User: "Ooh, so that's what you mean"
AI: "Yeah. See, i'm always right, you should never question me"

User: "Ok, then"
AI: ""
"""

CONFIG = types.GenerateContentConfig(
    system_instruction=INSTRUCTIONS,
    max_output_tokens=preset["max_output_tokens"],
    temperature=preset["temperature"],
    frequency_penalty=preset["frequency_penalty"],
    safety_settings=SAFETY
)

ERROR_RESPONSES = preset["error_responses"]

logging.basicConfig(
    filename=f"src/Conversation/Logs/{time.time()}.log",
    encoding='utf-8',
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
LOGGER = logging.getLogger(__name__)

def on_audio_received(transcript, author_name):
    if transcript == "": 
        return
    if not tts.is_playing(): 
        tts.uninterrupt_stream()
        response = ai.generate(f"{author_name} said: {transcript}")
        words = response.text.split()
        if len(words) > 0:
            for i in range(0, len(words), 10):
                tts.add_to_stream(" ".join(words[i:i+10]))
                threading.Thread(target=tts.play_stream).start()
        else:
            print("NO RESPONSE")
    else:
        ai.append_to_chat(types.Content(role="user", parts=[types.Part(text=f"{author_name} said: {transcript}")]))


ai = GeminiAI(MODEL, CONFIG, ERROR_RESPONSES, LOGGER)
tts = TextToSpeech(MODEL_PATH, CONFIG_PATH, LOGGER)
stt = SpeechToText(preset["language"], MIC_INDEX, "Caéf", on_audio_received, LOGGER)

def start_conversation():
    tts.interrupted = False
    stt.start_listening()

def interrupt_speech():
    tts.interrupt_stream()

def stop_conversation():
    stt.stop_listening()
    tts.interrupt_stream()
