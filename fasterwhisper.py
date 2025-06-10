import sounddevice as sd
import numpy as np
import tempfile
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
import time

# Settings
SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_SIZE = 1024
SILENCE_THRESHOLD = 100  # Adjust this based on mic sensitivity
SILENCE_DURATION = 4.0   # Seconds of silence to trigger stop
MODEL_SIZE = "small"

# Initialize model
model = WhisperModel(MODEL_SIZE, compute_type="int8")


while (True):

    print("🎙️ Speak now. Recording will stop after silence...")

    recording = []
    last_voice_time = time.time()

    def is_silent(audio_block):
        # Compute RMS energy
        rms = np.sqrt(np.mean(np.square(audio_block)))
        return rms < SILENCE_THRESHOLD

    def callback(indata, frames, time_info, status):
        global recording, last_voice_time
        audio_block = indata[:, 0].astype(np.float32)  # 🔁 Convert to float to avoid overflow
        recording.append(audio_block.copy())

        if not is_silent(audio_block):
            last_voice_time = time.time()

    # Start stream
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS,
                        dtype='int16', callback=callback, blocksize=BLOCK_SIZE):
        while True:
            sd.sleep(100)
            if time.time() - last_voice_time > SILENCE_DURATION:
                print("🛑 Silence detected. Stopping.")
                break

# Concatenate al    l blocks
    audio_np = np.concatenate(recording).astype(np.int16)

# Save to temp WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        write(f.name, SAMPLE_RATE, audio_np)
        audio_path = f.name

# Transcribe with forced English
    segments, _ = model.transcribe(audio_path, language="en")
    text = " ".join([seg.text for seg in segments])

    print("\n📝 Transcribed Text:")
    print(text)
