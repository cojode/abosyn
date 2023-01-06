import numpy as np
import librosa as lb
from os import path
from pydub import AudioSegment
import soundfile as sf


def main():
    mp2wav("data/mp3/rick.mp3", "data/raw/rick.wav")
    mfcc = wav2mfcc("data/raw/rick.wav", 40)
    mfcc2wav(mfcc, "results/rick.mp3")


def mp2wav(mp3_src: str, wav_dst: str) -> None:
    print(f"Processing {mp3_src}...", end='')
    sound = AudioSegment.from_mp3(mp3_src)
    sound.export(wav_dst, format="wav")
    print(" Done!")


def wav2mfcc(wav_path: str, n_mfcc: int) -> np.ndarray:
    y, sr = lb.load(wav_path)
    return lb.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)


def mfcc2wav(mfcc: np.ndarray, wav_dst: str) -> None:
    print("From mfcc to wav...")
    wav = lb.feature.inverse.mfcc_to_audio(mfcc)
    sf.write(wav_dst, wav, 48000, "PCM_24")


if __name__ == '__main__':
    main()
