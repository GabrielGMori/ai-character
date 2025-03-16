import os.path
from queue import Queue
import threading
from RealtimeTTS import TextToAudioStream, PiperEngine, PiperVoice#, EdgeEngine
import logging

DIRNAME = os.path.dirname(__file__)
MODELS_DIR = os.path.join(DIRNAME, "Voices/Models")
CONFIGS_DIR = os.path.join(DIRNAME, "Voices/Configs")

class TextToSpeech:
    def __init__(self, model, config, logger=logging.getLogger(__name__)):
        self.logger = logger
        self.logger.debug("Loading text to speech voice...")

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

        self.logger.debug("Loading text to speech engine...")
        self.engine = PiperEngine(
            piper_path="piper",
            voice=self.voice,
        )
        # self.engine = EdgeEngine(pitch=60, rate=20)
        # self.engine.set_voice("pt-BR-ThalitaMultilingualNeural")

        self.logger.debug("Creating text to speech audio stream...")
        self.stream = TextToAudioStream(self.engine, on_audio_stream_stop=self.on_audio_stream_stop, level=logging.DEBUG)
        self.audio_queue = Queue()
        self.currently_speaking = None
        self.interrupted = False
        self.logger.debug("Text to speech ready!")

    def audio_generator(self):
        first_chunk = False
        try:
            while True:
                if self.interrupted == True:
                    self.logger.debug("Stream interrupted, terminating")
                    break
                chunk = self.audio_queue.get()
                if chunk is None:
                    self.logger.debug("Last chunk reached, terminating stream")
                    break
                if not first_chunk:
                    first_chunk = True
                yield chunk
        except Exception as exeception:
            logging.error(f"Error during audio streaming: {str(exeception)}")

    def on_audio_chunk_synthesized(self, chunk):
        self.audio_queue.put(chunk)

    def on_audio_stream_stop(self):
        self.audio_queue.put(None)
        self.currently_speaking = None
        self.logger.debug("Stream stopped")

    def play_queue(self, text):
        self.currently_speaking = text
        self.logger.debug(f"Synthesizing audio for: {text}")
        self.stream.feed(text)
        self.stream.play_async(on_audio_chunk=self.on_audio_chunk_synthesized, muted=True)

    def synthesize(self, text):
        self.interrupted = False
        if not self.stream.is_playing():
            threading.Thread(target=self.play_queue, args=[text], daemon=True).start()
        return self.audio_generator()
    
    def interrupt_stream(self):
        self.logger.debug("Interrupting stream...")
        self.interrupted = True
        self.stream.stop()
        self.stream = TextToAudioStream(self.engine, on_audio_stream_stop=self.on_audio_stream_stop, level=logging.INFO)
