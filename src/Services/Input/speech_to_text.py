import threading
import speech_recognition
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
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
    def __init__(self, language, mic_index, author_name, on_audio_received, logger=logging.getLogger(__name__)):
        self.logger = logger
        self.executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="STT")

        self.language = language
        self.mic_index = mic_index
        self.author_name = author_name
        self.on_audio_received = on_audio_received

        self.listening = False
        self.transcription_queue = Queue()
        self.process_queue_lock = threading.Lock()
        self.processing_transcriptions = False

        self.logger.info("LOADING SPEECH TO TEXT MODEL...")
        self.recognizer = speech_recognition.Recognizer()
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.pause_threshold = 0.85
        self.adjust_for_ambient_noise()
        self.logger.info("SPEECH TO TEXT READY!")

    def adjust_for_ambient_noise(self):
        with speech_recognition.Microphone(self.mic_index) as mic:
            self.recognizer.adjust_for_ambient_noise(mic, 0.2)
            self.logger.info(f"NEW STT THRESHOLD: {self.recognizer.energy_threshold}")

    def process_text(self, text):
        self.logger.info(f"RECEIVED TEXT: {text}")
        self.on_audio_received(text, self.author_name)

    def process_transcription_queue(self):
        self.process_queue_lock.acquire(timeout=1)
        self.logger.info("PROCESSING QUEUE")
        full_text = ""

        while not self.transcription_queue.empty():
            transcription_data = self.transcription_queue.get()

            if transcription_data.transcribed_text == None:
                self.logger.info("WAITING FOR TRANSCRIPTION")
                transcription_data.transcription_complete.wait()
            if transcription_data.transcribed_text != " ":
                full_text += f" {transcription_data.transcribed_text}"
        
        stripped_text = full_text.strip()
        if stripped_text == "": 
            return
        self.process_text(stripped_text)
        self.process_queue_lock.release()

    def transcribe_audio_data(self, audio_data):
        try:
            self.logger.info("TRANSCRIBING...")
            text = self.recognizer.recognize_google(audio_data, language=self.language)
            self.logger.info(f"TRANSCRIBED: {text}")
            return text
        except speech_recognition.UnknownValueError:
            self.logger.info("NOTHING TO TRANSCRIBE")
            return " "

    def transcribe(self, transcription_data):
        transcribed_text = self.transcribe_audio_data(transcription_data.audio_data)
        transcription_data.set_transcribed_text(transcribed_text)

    def capture_speech(self):
        self.logger.info("CAPTURING SPEECH...")
        with speech_recognition.Microphone(self.mic_index) as mic:
            audio_data = self.recognizer.listen(mic)

            transcription_data = TranscriptionData(audio_data)
            self.transcription_queue.put(transcription_data)

            if not self.executor is None and not self.executor._shutdown:
                self.executor.submit(self.process_transcription_queue)
                self.executor.submit(self.transcribe, transcription_data)

    def start_listening(self):
        if self.executor is None or self.executor._shutdown:
            self.executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="STT")

        self.logger.info("STARTED LISTENING")
        self.listening = True
        while self.listening == True:
            self.capture_speech()
    
    def stop_listening(self):
        self.logger.info("STOPPED LISTENING")
        self.listening = False
        self.executor.shutdown()
        self.executor = None
