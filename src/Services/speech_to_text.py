import threading
import speech_recognition

class SpeechToText:
    def __init__(self, language, mic_index, author_name):
        self.language = language
        self.recognizer = speech_recognition.Recognizer()
        self.listening = False
        self.mic_index = mic_index
        self.author_name = author_name

    def available_mics(self):
        return speech_recognition.Microphone.list_microphone_names()
    
    def start_listening(self, on_audio_received):
        print("[LISTENING...]")
        self.listening = True
        while self.listening == True:
            try:
                with speech_recognition.Microphone(self.mic_index) as mic:
                    self.recognizer.adjust_for_ambient_noise(mic, 0.2)
                    self.recognizer.pause_threshold = 1
                    audio = self.recognizer.listen(mic)
                    text = self.recognizer.recognize_google(audio, language=self.language)
                    text = text.lower()
                    threading.Thread(target=on_audio_received, args=(text, self.author_name)).start()

            except speech_recognition.UnknownValueError:
                continue
    
    def stop_listening(self):
        self.listening = False
