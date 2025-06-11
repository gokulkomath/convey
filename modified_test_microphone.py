#!/usr/bin/env python3

import argparse
import queue
import sys
import sounddevice as sd

from json import loads
import requests
import os
import time
import subprocess
from requests.exceptions import ConnectionError, Timeout, RequestException   


import numpy as np
import tempfile
from scipy.io.wavfile import write
from faster_whisper import WhisperModel



q = queue.Queue()

def int_or_str(text):
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time_info, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))







def speak(text):



    # Run piper and pipe the output to aplay
    piper = subprocess.Popen(
        ['piper', '--model', 'en_GB-alba-medium.onnx', '--output-raw'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )

    aplay = subprocess.Popen(
        ['aplay', '-r', '22050', '-f', 'S16_LE', '-t', 'raw', '-'],
        stdin=piper.stdout
    )

    # Send text input to piper
    piper.stdin.write(text.encode('utf-8'))
    piper.stdin.close()

    # Wait for playback to complete
    aplay.wait()




 # This sends the prompt to the bot.
def send_to_bot(text):
    print(f"send to bot :{text.strip()}")
    try: 
        payload = {"sender": "user1", "message": text.strip()}
        response = requests.post("http://localhost:5005/webhooks/rest/webhook", json=payload)

        for msg in response.json():
            print(f"Convey : {msg['text']}")
            speak(msg["text"])
    

    except ConnectionError:
        print("Connection failed. Please check the action server.")

    except Timeout:
        print("⏳ The request timed out.")

    except RequestException as e:
        print(f"⚠️ An error occurred: {e}")



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
    send_to_bot(text.lower())

