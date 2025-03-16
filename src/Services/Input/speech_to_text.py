import threading
import speech_recognition
from queue import Queue
import logging

class TranscriptionData:
    def __init__(self, audio_data):
        self.audio_data = audio_data
        self.transcribed_text = None
        self.transcription_complete = threading.Event()

    def set_transcribed_text(self, text):
        self.transcribed_text = text
        self.transcription_complete.set()

class SpeechToText:
    def __init__(self, author, language, mic_index, on_audio_received, logger=logging.getLogger(__name__)):
        self.logger = logger

        self.author = author
        self.language = language
        self.mic_index = mic_index
        self.on_audio_received = on_audio_received

        self.listening = False
        self.transcription_queue = Queue()
        self.process_queue_lock = threading.Lock()
        self.processing_transcriptions = False

        self.logger.info("Loading speech to text model...")
        self.recognizer = speech_recognition.Recognizer()
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.pause_threshold = 0.85
        self.adjust_for_ambient_noise()
        self.logger.info("Speech to text ready!")

    def adjust_for_ambient_noise(self):
        with speech_recognition.Microphone(device_index=self.mic_index) as mic:
            self.recognizer.adjust_for_ambient_noise(source=mic, duration=0.2)
            self.logger.info(f"New stt threshold: {self.recognizer.energy_threshold}")

    def process_text(self, text):
        self.logger.info(f"Received text: {text}")
        self.on_audio_received(self.author, text)

    def process_transcription_queue(self):
        self.process_queue_lock.acquire()
        self.logger.info("Processing queue")
        full_text = ""

        while not self.transcription_queue.empty():
            transcription_data = self.transcription_queue.get()

            if transcription_data.transcribed_text == None:
                self.logger.info("Waiting for transcription")
                transcription_data.transcription_complete.wait()
            if transcription_data.transcribed_text != " ":
                full_text += f" {transcription_data.transcribed_text}"
        
        stripped_text = full_text.strip()
        if stripped_text == "": 
            self.process_queue_lock.release()
            return
        self.process_text(stripped_text)
        self.process_queue_lock.release()
        self.logger.info("Finished processing queue")

    def transcribe_audio_data(self, audio_data):
        try:
            self.logger.info("Transcribing...")
            text = self.recognizer.recognize_google(audio_data, language=self.language)
            self.logger.info(f"Transcribed: {text}")
            return text
        except speech_recognition.UnknownValueError:
            self.logger.info("Nothing to transcribe")
            return " "

    def transcribe(self, transcription_data):
        transcribed_text = self.transcribe_audio_data(transcription_data.audio_data)
        transcription_data.set_transcribed_text(transcribed_text)

    def capture_speech(self):
        self.logger.info("Capturing speech...")
        with speech_recognition.Microphone(self.mic_index) as mic:
            audio_data = self.recognizer.listen(mic)

            transcription_data = TranscriptionData(audio_data)
            self.transcription_queue.put(transcription_data)

            threading.Thread(target=self.process_transcription_queue, daemon=True).start()
            threading.Thread(target=self.transcribe, args=[transcription_data], daemon=True).start()

    def start_listening(self):
        self.logger.info("Started listening")
        self.listening = True
        while self.listening == True:
            self.capture_speech()
    
    def stop_listening(self):
        self.logger.info("Stopped listening")
        self.listening = False
