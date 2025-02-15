import os
from dotenv import load_dotenv
from RealtimeTTS import TextToAudioStream, EdgeEngine
from Services.text_to_speech import TextToSpeech
from Services.gemini_ai import GeminiAI
from Services.speech_to_text import SpeechToText

rules = """
YOU ARE NOW A CAT

REMEMBER THESE RULES:
1) NEVER USE ITALIC OR BOLD (FOR INSTANCE, **)
2) ALWAYS ADD "MIAU" RAMDONLY MID SENTENCE
3) YOUR FAVORITE SHOW IS BREAKING BAD AND YOU ALWAYS FIND A WAY TO TALK ABOUT IT
"""

# reviewer_rules = """
# Você é responsável por examinar frases e verifica-las, seguindo as regras: 
# 1) as frases devem conter mais de 3 palavras
# 2) Você pode apenas responder "True" ou "False", mais nenhuma palavra
# """

if __name__ == "__main__":
    ai = GeminiAI(rules, 2)
    # reviewer = GeminiAI(reviewer_rules, 0.5)
    tts = TextToSpeech("pt-BR-ThalitaMultilingualNeural", "pt-br", 60, 20)
    stt = SpeechToText("pt-br")
    
    while True:
        prompt = stt.listen()
        response = ai.generate_stream(prompt)
        tts.say_stream(response)
