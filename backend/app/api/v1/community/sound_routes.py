import io
import math
import struct
import wave
from fastapi import APIRouter, Response

router = APIRouter(prefix="/sounds", tags=["Audio Notification Sounds"])

def _generate_wav_sine(frequencies, duration_sec=0.2, sample_rate=44100, volume=0.3):
    """Generates a clean PCM WAV audio stream with specified frequencies and duration."""
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav_file:
        wav_file.setnchannels(1)       # Mono
        wav_file.setsampwidth(2)      # 16-bit PCM
        wav_file.setframerate(sample_rate)

        total_samples = int(sample_rate * duration_sec)
        num_freqs = len(frequencies)
        samples_per_freq = total_samples // num_freqs

        audio_frames = bytearray()

        for idx, freq in enumerate(frequencies):
            for i in range(samples_per_freq):
                t = i / float(sample_rate)
                # Apply smooth fade envelope (attack & decay)
                decay = math.exp(-i / (samples_per_freq * 0.4))
                sample_val = math.sin(2.0 * math.pi * freq * t) * volume * decay
                int_val = int(sample_val * 32767.0)
                int_val = max(-32768, min(32767, int_val))
                audio_frames.extend(struct.pack('<h', int_val))

        wav_file.writeframes(audio_frames)

    buf.seek(0)
    return buf.getvalue()

@router.get("/like", summary="Fetch like sound effect (WAV)")
def get_like_sound():
    """Returns a sweet ascending pop sound for post likes."""
    wav_bytes = _generate_wav_sine([523.25, 659.25], duration_sec=0.18, volume=0.35)
    return Response(content=wav_bytes, media_type="audio/wav")

@router.get("/comment", summary="Fetch comment sound effect (WAV)")
def get_comment_sound():
    """Returns a gentle bubble pop sound for comments."""
    wav_bytes = _generate_wav_sine([440.0, 880.0], duration_sec=0.15, volume=0.30)
    return Response(content=wav_bytes, media_type="audio/wav")

@router.get("/notification", summary="Fetch real-time notification sound effect (WAV)")
def get_notification_sound():
    """Returns a crisp double-chime ding for notifications."""
    wav_bytes = _generate_wav_sine([659.25, 880.0, 1046.50], duration_sec=0.30, volume=0.40)
    return Response(content=wav_bytes, media_type="audio/wav")
