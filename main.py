import numpy as np
import librosa as lb
from os import path
from pydub import AudioSegment
import soundfile as sf

WAV_DIR = "data/raw"
MP3_DIR = "data/mp3"


class MusicSample:

    mp3_path = None
    wav_path = None
    mfcc = None
    is_synthed = False
    paired_with = None

    def __init__(self, name: str) -> None:
        self.name = name
        if not (self.init_wav()) or not (self.init_mp3()):
            raise FileNotFoundError(f"None of {name}.wav or {name}.mp3 found")
        self.init_mfcc()

    def init_mfcc(self, n_mfcc: int) -> bool:
        if not (self.wav_path):
            return False
        else:
            y, sr = lb.load(self.wav_path)
            self.mfcc_path = lb.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
            return True

    def init_wav(self) -> bool:
        if not (self.mp3_path):
            return False
        else:
            sound = AudioSegment.from_mp3(self.mp3_path)
            sound.export(WAV_DIR + self.name + ".wav", format="wav")
            return True

    def init_mp3(self) -> bool:
        if not (self.name):
            return False
        else:
            self.mp3_path = MP3_DIR + self.name + ".mp3"
            return True
