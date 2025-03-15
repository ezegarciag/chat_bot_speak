import pyaudio
import numpy as np



class Microphone:
    def __init__(self, threshold=500, silence_duration=1.0, rate=44100, chunk=1024):
        self.threshold = threshold
        self.silence_duration = silence_duration
        self.rate = rate
        self.chunk = chunk
        self.audio = pyaudio.PyAudio()

    def is_silent(self, data):
        return np.abs(np.frombuffer(data, dtype=np.int16)).mean() < self.threshold

    def start_listening(self):
        stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=self.rate, input=True, frames_per_buffer=self.chunk)
        frames = []
        silent_chunks = 0
        max_silent_chunks = int(self.silence_duration * self.rate / self.chunk)

        recording = False

        while True:
            data = stream.read(self.chunk)
            if not self.is_silent(data):
                recording = True
                frames.append(data)
                silent_chunks = 0
            elif recording:
                silent_chunks += 1
                if silent_chunks > max_silent_chunks:
                    break

        stream.stop_stream()
        stream.close()

        return b''.join(frames)
