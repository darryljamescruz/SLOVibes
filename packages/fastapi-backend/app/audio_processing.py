# packages/fastapi-backend/app/audio_processing.py

import os
from pydub import AudioSegment
import librosa
import numpy as np
import soundfile as sf
from scipy.signal import fftconvolve


def process_audio_file(input_path: str, output_path: str,
                       slow_pct: float = 85.0,
                       reverb_pct: float = 0.0):
    """
    1) Slows the audio by a percentage (preserving pitch drop effect)
    2) (Optional) Applies convolution reverb via impulse response
    """
    # Load source file
    audio = AudioSegment.from_file(input_path)
    orig_rate = audio.frame_rate

    # Compute new frame rate (must be >= 1)
    new_rate = int(orig_rate * (slow_pct / 100.0))
    if new_rate < 1:
        new_rate = orig_rate

    # Slow down: spawn with override then set back to orig_rate
    slowed = audio._spawn(audio.raw_data, overrides={
        'frame_rate': new_rate
    }).set_frame_rate(orig_rate)

    # Export slowed audio to a temp WAV
    temp_wav = 'temp.wav'
    slowed.export(temp_wav, format='wav')

    # Load into numpy for optional further DSP
    y, sr = librosa.load(temp_wav, sr=orig_rate, mono=True)

    # ====================
    # TODO: Reverb block
    # if reverb_pct > 0:
    #     # Load impulse response (must exist)
    #     ir, _ = librosa.load(
    #         'impulse_responses/small-room.wav', sr=orig_rate)
    #     # Convolution
    #     reverb = fftconvolve(y, ir[:len(y)], mode='full')[:len(y)]
    #     reverb = reverb / np.max(np.abs(reverb))
    #     # Mix dry + wet
    #     wet = reverb_pct / 100.0
    #     dry = 1.0 - wet
    #     y = (dry * y) + (wet * reverb)
    #     y = y / np.max(np.abs(y))
    # ====================

    # Write final output as WAV
    sf.write(output_path, y, sr)

    # Clean up
    if os.path.exists(temp_wav):
        os.remove(temp_wav)
