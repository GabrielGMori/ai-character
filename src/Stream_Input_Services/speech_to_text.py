import threading
import speech_recognition
from queue import Queue
import chalk

class TranscriptionData:
    def __init__(self, audio_data):
        self.audio_data = audio_data
        self.transcribed_text = None
        self.transcription_complete = threading.Event()

    def set_transcribed_text(self, text):
        self.transcribed_text = text
        self.transcription_complete.set()

class SpeechToText:
    def __init__(self, language, mic_index, author_name, on_audio_received):
        self.language = language
        self.mic_index = mic_index
        self.author_name = author_name
        self.on_audio_received = on_audio_received

        self.listening = False
        self.transcription_queue = Queue()
        self.processing_transcriptions = False

        print(chalk.blue("[LOADING SPEECH TO TEXT MODEL...]"))
        self.recognizer = speech_recognition.Recognizer()
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.pause_threshold = 0.85
        self.adjust_for_ambient_noise()
        print(chalk.blue("[SPEECH TO TEXT READY!]"))

    def adjust_for_ambient_noise(self):
        with speech_recognition.Microphone(self.mic_index) as mic:
            self.recognizer.adjust_for_ambient_noise(mic, 0.2)
            print(chalk.yellow(f"[NEW STT THRESHOLD: {self.recognizer.energy_threshold}]"))

    def process_text(self, text):
        print(chalk.cyan(f"[RECEIVED TEXT: {text}]"))
        self.on_audio_received(text, self.author_name)

    def process_transcription_queue(self):
        if self.processing_transcriptions == True: return
        print(chalk.black("[PROCESSING QUEUE]"))
        full_text = ""

        while not self.transcription_queue.empty():
            self.processing_transcriptions = True
            next = self.transcription_queue.get()

            if next.transcribed_text == None:
                print(chalk.black("[WAITING FOR TRANSCRIPTION]"))
                next.transcription_complete.wait()
            if not next.transcribed_text == " ":
                full_text += f" {next.transcribed_text}"
        
        stripped_text = full_text.strip()
        self.processing_transcriptions = False
        if stripped_text == "": return
        self.process_text(stripped_text)

    def transcribe_audio_data(self, audio_data):
        try:
            print(chalk.green("[TRANSCRIBING...]"))
            text = self.recognizer.recognize_google(audio_data, language=self.language)
            print(chalk.green(f"[TRANSCRIBED: {text}]"))
            return text
        except speech_recognition.UnknownValueError:
            print(chalk.green("[NOTHING TO TRANSCRIBE]"))
            return " "

    def transcribe(self, transcription_data):
        transcribed_text = self.transcribe_audio_data(transcription_data.audio_data)
        transcription_data.set_transcribed_text(transcribed_text)

    def capture_speech(self):
        print(chalk.red("[CAPTURING SPEECH...]")) 
        with speech_recognition.Microphone(self.mic_index) as mic:
            audio_data = self.recognizer.listen(mic)

            transcription_data = TranscriptionData(audio_data)
            self.transcription_queue.put(transcription_data)

            threading.Thread(target=self.process_transcription_queue, args=[]).start()
            threading.Thread(target=self.transcribe, args=[transcription_data]).start()

    def start_listening(self):
        print("[STARTED LISTENING]")
        self.listening = True
        while self.listening == True:
            self.capture_speech()
    
    def stop_listening(self):
        print("[STOPPED LISTENING]")
        self.listening = False

if __name__ == "__main__":
    def process(text, author):
        print(chalk.bold(f"[TEXT PROCESSED FROM {author}: {text}]"))

    tts = SpeechToText("pt", 1, "Mori", process)
    tts.start_listening()
