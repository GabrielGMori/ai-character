import threading
from Output_Services.text_to_speech import TextToSpeech
from Output_Services.gemini_ai import GeminiAI
from Stream_Input_Services.speech_to_text import SpeechToText
from google.genai import types
import json
import os

MIC_INDEX = 3
PRESET_NAME = "Steve"

PRESETS_DIR = "src/Conversation/Presets/"
with open(os.path.join(PRESETS_DIR, f"{PRESET_NAME}.json"), 'r') as file:
    preset = json.load(file)

VOICES_DIR = "src/Conversation/TTS_Voices"
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

instructions = preset["instructions"] + """
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
    system_instruction=instructions,
    max_output_tokens=preset["max_output_tokens"],
    temperature=preset["temperature"],
    frequency_penalty=preset["frequency_penalty"],
    safety_settings=SAFETY
)

ERROR_RESPONSES = preset["error_responses"]

def on_audio_received(transcript, author_name):
    if transcript == "": 
        return
    print("[RECEIVED: " + transcript + "]")
    if not tts.is_playing(): 
        print("[REPLYING...]")
        tts.uninterrupt_stream()
        response = ai.generate(f"{author_name} said: {transcript}")
        # The first chunk of gemini's responses is usually just a maximum of 3 characters for some reason
        # For that reason, i'm attaching the first chunk to the beggining of the second chunk before sending it to TTS
        # i = 0
        # first_chunk_text = ""
        # full_response = ""
        # for chunk in response:
        #     i += 1
        #     if chunk and tts.interrupted == False:
        #         full_response += chunk.text.replace("\n", "")
        #         if i == 1:
        #             first_chunk_text = chunk.text.replace("\n", "")
        #         else:
        #             text = chunk.text.replace("\n", "")
        #             if first_chunk_text != "":
        #                 text = first_chunk_text + text
        #                 first_chunk_text = ""
        #             tts.add_to_stream(text)
        words = response.text.split()
        if len(words) > 0:
            for i in range(0, len(words), 10):
                tts.add_to_stream(" ".join(words[i:i+10]))
                threading.Thread(target=tts.play_stream).start()
        else:
            print("[NO RESPONSE]")
    else:
        ai.append_to_chat(types.Content(role="user", parts=[types.Part(text=f"{author_name} said: {transcript}")]))


ai = GeminiAI(MODEL, CONFIG, ERROR_RESPONSES)
tts = TextToSpeech(MODEL_PATH, CONFIG_PATH)
stt = SpeechToText(preset["language"], MIC_INDEX, "Caéf", on_audio_received)

def start_conversation():
    tts.interrupted = False
    stt.start_listening()

def interrupt_speech():
    tts.interrupt_stream()

def stop_conversation():
    stt.stop_listening()
    tts.interrupt_stream()
