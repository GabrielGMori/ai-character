import os.path
from RealtimeTTS import TextToAudioStream, PiperEngine, PiperVoice

class TextToSpeech:
    def __init__(self, model_path, config_path):
        print("[LOADING TEXT TO SPEECH VOICE...]")

        if not os.path.exists(model_path):
            print("[COULD NOT FIND TEXT TO SPEECH MODEL]")
            return
        if not os.path.exists(config_path):
            print("[COULD NOT FIND TEXT TO SPEECH CONFIGURATION FILE]")
            return
        
        self.model_file = os.path.abspath(model_path)
        self.config_file = os.path.abspath(config_path)

        self.voice = PiperVoice(
            model_file=self.model_file,
            config_file=self.config_file,
        )

        print("[LOADING TEXT TO SPEECH ENGINE...]")
        self.engine = PiperEngine(
            piper_path="piper",
            voice=self.voice,
        )

        print("[CREATING TEXT TO SPEECH AUDIO STREAM...]")
        self.stream = TextToAudioStream(self.engine)
        print("[TEXT TO SPEECH READY!]")

    def is_playing(self):
        return self.stream.is_playing()

    def play_stream(self):
        if self.stream.is_playing() == False and self.interrupted == False:
            print("[PLAYING TEXT TO SPEECH...]")
            self.stream.play()

    def interrupt_stream(self):
        self.stream.stop()
        self.stream = TextToAudioStream(self.engine)
        self.interrupted = True

    def uninterrupt_stream(self):
        self.interrupted = False
    
    def say(self, text):
        self.stream.feed(text)
        self.play_stream()

    def add_to_stream(self, string):
        if self.interrupted == False:
            print("[ADDING TO SYNTHESIZE: " + string.replace("\n", "") + "]")
            self.stream.feed(string)

