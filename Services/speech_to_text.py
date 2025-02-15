import speech_recognition

class SpeechToText:
    def __init__(self, language):
        self.language = language
        self.recognizer = speech_recognition.Recognizer()
    
    def listen(self):
        print("[LISTENING...]")
        while True:
            try:
                with speech_recognition.Microphone() as mic:
                    self.recognizer.adjust_for_ambient_noise(mic, 0.2)
                    self.recognizer.pause_threshold = 0.8
                    audio = self.recognizer.listen(mic)
                    text = self.recognizer.recognize_google(audio, language=self.language)
                    text = text.lower()
                    print(text)
                    return text;

            except speech_recognition.UnknownValueError:
                continue
