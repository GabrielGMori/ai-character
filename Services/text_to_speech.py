from RealtimeTTS import TextToAudioStream, EdgeEngine

class TextToSpeech:
    def __init__(self, voice, language, pitch, rate):
        print("[LOADING TEXT TO SPEECH ENGINE...]")
        self.voice = voice
        self.language = language
        self.pitch = pitch
        self.rate = rate
        
        self.engine = EdgeEngine(pitch=self.pitch, rate=self.rate)
        self.engine.set_voice(self.voice)

        print("[CREATING TEXT TO SPEECH AUDIO STREAM...]")
        self.stream = TextToAudioStream(self.engine)

    def play_stream(self):
        if not self.stream.is_playing:
            print("[PLAYING TEXT TO SPEECH...]")
        self.stream.play(log_synthesized_text=True, language=self.language)

    def say(self, text):
        self.stream.feed(text)
        self.play_stream()
    
    def say_stream(self, text_stream):
        for chunk in text_stream: self.stream.feed(chunk.text)
        self.play_stream()
