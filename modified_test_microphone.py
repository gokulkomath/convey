#!/usr/bin/env python3

import argparse
import queue
import sys
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from json import loads
import requests
import os
import time
import subprocess
from requests.exceptions import ConnectionError, Timeout, RequestException   


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




parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-l", "--list-devices", action="store_true",
    help="show list of audio devices and exit")
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)

parser = argparse.ArgumentParser(
    description="Vosk speech recognition - stop after first transcription",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    "-f", "--filename", type=str, metavar="FILENAME",
    help="audio file to store recording to (raw format)")
parser.add_argument(
    "-d", "--device", type=int_or_str,
    help="input device (numeric ID or substring)")
parser.add_argument(
    "-r", "--samplerate", type=int, help="sampling rate")
parser.add_argument(
    "-m", "--model", type=str, help="path to model directory")
args = parser.parse_args(remaining)

model_path = "/home/chico/vosk-model-en-in-0.5"
model = Model(model_path)


if args.samplerate is None:
    device_info = sd.query_devices(args.device, "input")
    args.samplerate = int(device_info["default_samplerate"])

dump_fn = None

while(True):
    try:
        with sd.RawInputStream(samplerate=args.samplerate, blocksize=8000,
                            device=args.device, dtype="int16", channels=1,
                            callback=callback):
            print("#" * 80)
   
            print("Will stop automatically after first transcription.")
            print("#" * 80)

            rec = KaldiRecognizer(model, args.samplerate)

            

            while True:
           # print("Listening... Speak something.")
                
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = loads(rec.Result())
                    text = result.get("text", "")
                    if text.strip():
                        print("\nTranscription:")
                        send_to_bot(text)
                        break
                   
                
                if dump_fn is not None:
                    dump_fn.write(data)

    except KeyboardInterrupt:
        print("\nRecording interrupted.")
        parser.exit(0)
    except Exception as e:
        parser.exit(type(e).__name__ + ": " + str(e))
    time.sleep(2)





