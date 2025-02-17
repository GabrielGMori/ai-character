from RealtimeTTS import TextToAudioStream, EdgeEngine

class TextToSpeech:
    def __init__(self, voice, language, pitch, rate):
        print("[LOADING TEXT TO SPEECH ENGINE...]")
        self.voice = voice
        self.language = language
        self.pitch = pitch
        self.rate = rate
        self.interrupted = False
        
        self.engine = EdgeEngine(pitch=self.pitch, rate=self.rate)
        self.engine.set_voice(self.voice)

        print("[CREATING TEXT TO SPEECH AUDIO STREAM...]")
        self.stream = TextToAudioStream(self.engine)

    def is_playing(self):
        return self.stream.is_playing()

    def play_stream(self):
        if not self.stream.is_playing:
            print("[PLAYING TEXT TO SPEECH...]")
        self.stream.play(language=self.language)

    def interrupt_stream(self):
        self.stream.stop()
        self.stream = TextToAudioStream(self.engine)
        self.interrupted = True
    
    def say(self, text):
        self.stream.feed(text)
        self.play_stream()

    def add_to_stream(self, generator):
        self.interrupted = False
        for chunk in generator: 
            if self.interrupted == False:
                print("[ADDING TO SYNTHESIZE: " + chunk.text.replace("\n", "") + "]")
                self.stream.feed(chunk.text)