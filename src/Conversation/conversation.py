from Services.text_to_speech import TextToSpeech
from Services.gemini_ai import GeminiAI
from Services.speech_to_text import SpeechToText
from google.genai import types

MIC_INDEX = 8

MODEL = "en-US-SteffanNeural"
LANGUAGE = "en"

rules = """
YOU ARE NOW AN AI CHATBOT WITH THE PURPOSE OF ENTERTAINING PEOPLE AND BEING FUNNY
YOU SHOULD BE A BIT UNHINGED AND INTERESTING

REMEMBER THESE RULES:
1) NEVER USE ITALIC OR BOLD (FOR INSTANCE, **)
2) ALWAYS ANSWER IN THE LANGUAGE THE USER IS TALKING IN
3) NEVER GET OUT OF CHARACTER
"""

safety = [
    {"category": types.HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE},
    {"category": types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": types.HarmBlockThreshold.BLOCK_NONE},
    {"category": types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, "threshold": types.HarmBlockThreshold.BLOCK_ONLY_HIGH},
    {"category": types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": types.HarmBlockThreshold.BLOCK_NONE},
    {"category": types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY, "threshold": types.HarmBlockThreshold.BLOCK_NONE}
]

config = types.GenerateContentConfig(
    system_instruction=rules,
    max_output_tokens=2000,
    temperature=1.5,
    frequencyPenalty=1,
    safety_settings=safety
)

ai = GeminiAI(config, safety)
tts = TextToSpeech(MODEL, LANGUAGE, -10, 20)
stt = SpeechToText(LANGUAGE, MIC_INDEX, "Friend")

def on_audio_received(transcript, author_name):
    print("[RECEIVED: " + transcript + "]")
    if not tts.is_playing(): 
        print("[REPLYING...]")
        response = ai.generate_stream(transcript)
        tts.add_to_stream(response)
        tts.play_stream()

def start_conversation():
    mics = stt.available_mics()
    for i, mic in enumerate(mics):
        print(f"{i}: {mic}")
    tts.interrupted = False
    stt.start_listening(on_audio_received=on_audio_received)

def interrupt_speech():
    tts.interrupt_stream()

def stop_conversation():
    stt.stop_listening()
    tts.interrupt_stream()
