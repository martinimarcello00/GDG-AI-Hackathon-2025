#! python3.7

import argparse
import os
import numpy as np
import speech_recognition as sr
import whisper
import torch
import pyaudio
import wave
import threading

from datetime import datetime, timedelta
from queue import Queue
from time import sleep
from sys import platform

import requests
import random
import json

def create_session():
    uid = f"u_{random.randint(100, 999)}"
    url = f"http://0.0.0.0:8000/apps/hr-agent/users/{uid}/sessions/s_{random.randint(100, 999)}"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print("Session created successfully.")
        return response.json()
    else:
        print(f"Failed to create session: {response.status_code}")
        return None


def ask_agent(session_data, question):
    url = "http://0.0.0.0:8000/run"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "session_id": session_data["id"],
        "user_id": session_data["user_id"],
        "app_name": session_data["app_name"],
        "new_message": {
            "role": "user",
                "parts": [{"text": str(question)}]
            }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print("Question sent successfully.")
        return response.json()
    else:
        print(f"Failed to send question: {response.status_code}")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="medium", help="Model to use",
                        choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--non_english", action='store_true',
                        help="Don't use the english model.")
    parser.add_argument("--energy_threshold", default=1000,
                        help="Energy level for mic to detect.", type=int)
    parser.add_argument("--record_timeout", default=2,
                        help="How real time the recording is in seconds.", type=float)
    parser.add_argument("--phrase_timeout", default=3,
                        help="How much empty space between recordings before we "
                             "consider it a new line in the transcription.", type=float)
    parser.add_argument("--audio_source", default="microphone", 
                        choices=["microphone", "system"],
                        help="Audio source: microphone or system audio")
    if 'linux' in platform:
        parser.add_argument("--default_microphone", default='pulse',
                            help="Default microphone name for SpeechRecognition. "
                                 "Run this with 'list' to view available Microphones.", type=str)
    args = parser.parse_args()

    # The last time a recording was retrieved from the queue.
    phrase_time = None
    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    # Bytes object which holds audio data for the current phrase
    phrase_bytes = bytes()
    
    # Load / Download model
    model = args.model
    if args.model != "large" and not args.non_english:
        model = model + ".en"
    audio_model = whisper.load_model(model)
    
    record_timeout = args.record_timeout
    phrase_timeout = args.phrase_timeout
    
    # Set up audio source based on user choice
    if args.audio_source == "microphone":
        # Original microphone setup code
        recorder = sr.Recognizer()
        recorder.energy_threshold = args.energy_threshold
        recorder.dynamic_energy_threshold = False
        
        if 'linux' in platform:
            mic_name = args.default_microphone
            if not mic_name or mic_name == 'list':
                print("Available microphone devices are: ")
                for index, name in enumerate(sr.Microphone.list_microphone_names()):
                    print(f"Microphone with name \"{name}\" found")
                return
            else:
                for index, name in enumerate(sr.Microphone.list_microphone_names()):
                    if mic_name in name:
                        source = sr.Microphone(sample_rate=16000, device_index=index)
                        break
        else:
            source = sr.Microphone(sample_rate=16000)
        
        with source:
            recorder.adjust_for_ambient_noise(source)
        
        def record_callback(_, audio:sr.AudioData) -> None:
            """
            Threaded callback function to receive audio data when recordings finish.
            audio: An AudioData containing the recorded bytes.
            """
            data = audio.get_raw_data()
            data_queue.put(data)
        
        # Create a background thread that will pass us raw audio bytes.
        recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)
    
    else:  # System audio capture
        # Set up PyAudio for system audio capture
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        p = pyaudio.PyAudio()
        
        # Find the right device - on Windows, we need to find a WASAPI loopback device
        device_index = None
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            print(f"Device {i}: {device_info['name']}")
            
            # Look for WASAPI loopback device or other system audio capture
            if 'loopback' in device_info['name'].lower() or 'stereo mix' in device_info['name'].lower() or i == 2:
                device_index = i
                print(f"Selected device {i}: {device_info['name']} for system audio capture")
                break
        
        if device_index is None:
            print("No suitable system audio capture device found.")
            if platform == 'win32':
                print("For Windows, try enabling 'Stereo Mix' in your sound settings.")
            return
        
        # Function to continuously record system audio
        def record_system_audio():
            stream = p.open(format=FORMAT,
                           channels=CHANNELS,
                           rate=RATE,
                           input=True,
                           input_device_index=device_index,
                           frames_per_buffer=CHUNK)
            
            print("Recording system audio...")
            
            while True:
                try:
                    audio_chunk = stream.read(CHUNK)
                    data_queue.put(audio_chunk)
                    
                    # Add a small sleep to prevent overwhelming the queue
                    sleep(0.01)
                except KeyboardInterrupt:
                    break
            
            stream.stop_stream()
            stream.close()
            p.terminate()
        
        # Start the recording thread
        audio_thread = threading.Thread(target=record_system_audio)
        audio_thread.daemon = True
        audio_thread.start()

    transcription = ['']

    # Cue the user that we're ready to go.
    print("Model loaded.\n")

    session = create_session()

    while True:
        try:
            now = datetime.utcnow()
            # Pull raw recorded audio from the queue.
            if not data_queue.empty():
                phrase_complete = False
                # If enough time has passed between recordings, consider the phrase complete.
                # Clear the current working audio buffer to start over with the new data.
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    phrase_bytes = bytes()
                    phrase_complete = True
                # This is the last time we received new audio data from the queue.
                phrase_time = now
                
                # Combine audio data from queue
                audio_data = b''.join(data_queue.queue)
                data_queue.queue.clear()

                # Add the new audio data to the accumulated data for this phrase
                phrase_bytes += audio_data

                # Convert in-ram buffer to something the model can use directly without needing a temp file.
                # Convert data from 16 bit wide integers to floating point with a width of 32 bits.
                # Clamp the audio stream frequency to a PCM wavelength compatible default of 32768hz max.
                audio_np = np.frombuffer(phrase_bytes, dtype=np.int16).astype(np.float32) / 32768.0

                # Read the transcription.
                result = audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
                text = result['text'].strip()

                # If we detected a pause between recordings, add a new item to our transcription.
                # Otherwise edit the existing one.
                if phrase_complete:
                    transcription.append(text)

                    ask_agent(session, text)

                else:
                    transcription[-1] = text

                # Clear the console to reprint the updated transcription.
                os.system('cls' if os.name=='nt' else 'clear')
                for line in transcription:
                    print(line)
                # Flush stdout.
                print('', end='', flush=True)
            else:
                # Infinite loops are bad for processors, must sleep.
                sleep(0.25)
        except KeyboardInterrupt:
            break

    print("\n\nTranscription:")
    for line in transcription:
        print(line)


if __name__ == "__main__":
    main()
