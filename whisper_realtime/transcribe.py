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
import base64

agent_host = '0.0.0.0:8000'
session_data = {}


def ask_agent(session_data, question):
    url = f"http://{agent_host}/run"
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
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print("Question sent successfully.")
            return response.json()
        else:
            print(f"Failed to send question: {response.status_code}")
            return None
    except:
        print("Error sending question to agent.")
        return None
    
def parse_agent_response(response):
    followUp = ""
    insights = ""
    summary = ""
    for content in response:
        if content["author"] == "followup_agent" and "text" in content["content"]["parts"][0].keys():
            followUp = content["content"]["parts"][0]["text"]
        elif content["author"] == "insights_agent" and "text" in content["content"]["parts"][0].keys():
            insights = content["content"]["parts"][0]["text"]
        elif content["author"] == "retrieve_user_summary_agent" and "text" in content["content"]["parts"][0].keys():
            summary = content["content"]["parts"][0]["text"]
    return {"followUp" : followUp, "insights": insights, "summary": summary}


def transcribe(model, session, non_english=False, energy_threshold=1000, record_timeout=10, phrase_timeout=3):
    global session_data
    session_data = session

    # The last time a recording was retrieved from the queue.
    phrase_time = None
    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    # Bytes object which holds audio data for the current phrase
    phrase_bytes = bytes()
    
    # Load / Download model
    if model != "large" and not non_english:
        model = model + ".en"
    audio_model = whisper.load_model(model)
    
    # Original microphone setup code
    recorder = sr.Recognizer()
    recorder.energy_threshold = energy_threshold
    recorder.dynamic_energy_threshold = False
    
    if 'linux' in platform:
        mic_name = 'pulse'
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

    transcription = ['']

    # Cue the user that we're ready to go.
    print("Model loaded.\n")
    print("==========================")
    print("STARTED RECORDING")
    print("==========================\n")

    while True:
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
                print(text)
                response = ask_agent(session, text)
                json.dump(parse_agent_response(response), open("response.json", "w"), indent=4)

            else:
                transcription[-1] = text

            # Clear the console to reprint the updated transcription.
            # os.system('cls' if os.name=='nt' else 'clear')
            # for line in transcription:
            #     print(line)
            # # Flush stdout.
            # print('', end='', flush=True)
        else:
            # Infinite loops are bad for processors, must sleep.
            sleep(0.25)

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--model", default="base", help="Model to use",
#                         choices=["tiny", "base", "small", "medium", "large"])
#     parser.add_argument("--session", required=True,
#                         help="JSON string containing session data")
    
#     args = parser.parse_args()
    
#     try:
#         session = json.loads(args.session)
#         print(f"Session loaded: {session}")
#         transcribe(args.model, session)
#     except json.JSONDecodeError as e:
#         print(f"Error parsing session JSON: {e}")
#         exit(1)
