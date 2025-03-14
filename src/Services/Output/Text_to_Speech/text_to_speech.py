import os.path
from RealtimeTTS import TextToAudioStream, PiperEngine, PiperVoice#, EdgeEngine
import logging

DIRNAME = os.path.dirname(__file__)
MODELS_DIR = os.path.join(DIRNAME, "Voices/Models")
CONFIGS_DIR = os.path.join(DIRNAME, "Voices/Configs")

class TextToSpeech:
    def __init__(self, model, config, on_audio_finished, logger=logging.getLogger(__name__)):
        self.logger = logger
        self.logger.info("Loading text to speech voice...")

        model_path = os.path.join(MODELS_DIR, f"{model}.onnx")
        config_path = os.path.join(CONFIGS_DIR, f"{config}.onnx.json")

        if not os.path.exists(model_path):
            self.logger.critical("Could not find text to speech model")
            raise Exception("Could not find text to speech model")
        if not os.path.exists(config_path):
            self.logger.critical("Could not find text to speech configuration file")
            raise Exception("Could not find text to speech configuration file")

        self.voice = PiperVoice(
            model_file=model_path,
            config_file=config_path,
        )

        self.logger.info("Loading text to speech engine...")
        self.engine = PiperEngine(
            piper_path="piper",
            voice=self.voice,
        )
        # self.engine = EdgeEngine(pitch=60, rate=20)
        # self.engine.set_voice("pt-BR-ThalitaMultilingualNeural")

        self.logger.info("Creating text to speech audio stream...")
        self.on_audio_finished = on_audio_finished
        self.stream = TextToAudioStream(self.engine, on_audio_stream_stop=self.on_audio_finished)
        self.interrupted = False
        self.logger.info("Text to speech ready!")

    def is_playing(self):
        return self.stream.is_playing()

    def play_stream(self):
        if not self.stream.is_playing() and not self.interrupted:
            self.logger.info("Playing text to speech...")
            self.stream.play()

    def interrupt_stream(self):
        self.stream.stop()
        self.stream = TextToAudioStream(self.engine, on_audio_stream_stop=self.on_audio_finished)
        self.interrupted = True

    def uninterrupt_stream(self):
        self.interrupted = False
    
    def say(self, text):
        self.stream.feed(text)
        self.play_stream()

    def add_to_stream(self, string):
        if self.interrupted == False:
            self.logger.info("Adding to synthesize: " + string.replace("\n", "") + "")
            self.stream.feed(string)

if __name__ == "__main__":
    def on_audio_finished():
        print("finished speaking")

    tts = TextToSpeech(model="Lula", config="Lula", on_audio_finished=on_audio_finished, logger=logging.getLogger(__name__))
    tts.s
