from pydub import AudioSegment
from scipy.signal import fftconvolve
import numpy as np
import soundfile as sf
import librosa

def process_audio_file(input_path, output_path, slow_pct=85.0, reverb_pct=50.0):
    # Convert MP3 to WAV
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(int(audio.frame_rate * (slow_pct / 100)))
    temp_wav_path = "temp.wav"
    audio.export(temp_wav_path, format="wav")

    # Load slowed audio
    y, sr = librosa.load(temp_wav_path, sr=44100)

    # Load IR for reverb
    ir, _ = librosa.load("impulse_responses/small-room.wav", sr=44100)

    # Apply convolution reverb
    reverb = fftconvolve(y, ir[:len(y)], mode="full")[:len(y)]
    reverb = reverb / np.max(np.abs(reverb))

    # Mix dry/wet
    wet_gain = reverb_pct / 100
    dry_gain = 1.0 - wet_gain
    mixed = (dry_gain * y) + (wet_gain * reverb)
    mixed = mixed / np.max(np.abs(mixed))

    # Save final
    sf.write(output_path, mixed, sr)