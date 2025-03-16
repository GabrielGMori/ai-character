from queue import Queue
import threading
import pyaudio

AUDIO_FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22050

class OutputHandler:
    def __init__(self, device_index, on_audio_stream_stop):
        self.pyaudio_instance = pyaudio.PyAudio()
        self.audio_stream = self.pyaudio_instance.open(format=AUDIO_FORMAT, channels=CHANNELS, rate=RATE, output=True, output_device_index=device_index)
        self.on_audio_stream_stop = on_audio_stream_stop

        self.audio_stream_interrupted = False
        self.audio_stream_playing = False

    def play_chunk_queue(self, chunk_queue):
        self.audio_stream.start_stream()
        self.audio_stream_playing = True
        buffer = b""

        frame_size = self.pyaudio_instance.get_sample_size(AUDIO_FORMAT) * CHANNELS
        min_buffer_size = 1024 * 6

        while len(buffer) < min_buffer_size and self.audio_stream_interrupted == False:
            chunk = chunk_queue.get()
            if chunk is None:
                break
            buffer += chunk

        while self.audio_stream_interrupted == False:
            if len(buffer) >= frame_size:
                num_frames = len(buffer)
                bytes_to_write = num_frames * frame_size
                self.audio_stream.write(buffer[:bytes_to_write])
                buffer = buffer[bytes_to_write:]
            else:
                chunk = chunk_queue.get()
                if chunk is None:
                    if len(buffer) > 0:
                        if len(buffer) % frame_size != 0:
                            buffer = buffer[:-(len(buffer) % frame_size)]
                        
                        self.audio_stream.write(buffer)
                    break
                buffer += chunk

        self.audio_stream_playing = False
        self.on_audio_stream_stop()
        self.audio_stream.stop_stream()

    def play_audio_generator(self, audio_generator):
        self.audio_stream_interrupted = False
        chunk_queue = Queue()

        threading.Thread(target=self.play_chunk_queue, args=[chunk_queue]).start()
        for chunk in audio_generator:
            if chunk and self.audio_stream_interrupted == False:
                chunk_queue.put(chunk)
                
        chunk_queue.put(None)

    def interrupt_playback(self):
        self.audio_stream_interrupted = True
        self.audio_stream_playing = False
        self.on_audio_stream_stop()
        self.audio_stream.stop_stream()

    def is_audio_stream_playing(self):
        return self.audio_stream_playing
