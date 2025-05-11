import requests
import json
import random
from whisper_realtime.transcribe import transcribe
import threading
import time
import signal
import sys
import os
import argparse

host = 'localhost:8000'

# Create a stop event
stop_event = threading.Event()

def create_session(agent_name="hr-agent"):
    uid = f"u_{random.randint(100, 999)}"
    url = f"http://{host}/apps/{agent_name}/users/{uid}/sessions/s_{random.randint(100, 999)}"
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

def parse_cv_response(response):
    # Extract the markdown block from the response
    for content in reversed(response):
        if content["author"] == "cv_agent" and "text" in content["content"]["parts"][0].keys():
            text = content["content"]["parts"][0]["text"]
            return text
    return None

def ask_agent(session_data, question):
    url = f"http://{host}/run"
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

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Client for interacting with the HR agent and SearchCV')
    parser.add_argument('--prompt', default='Find the CV', help='Prompt for the HR agent')

    args = parser.parse_args()

    # delete the file response.json if it exists
    try:
        os.remove("response.json")
    except OSError:
        if os.path.exists("response.json"):
            print("Error deleting file")
        else:
            print("File does not exist")

    previous_summary = "";
    # Create session searchcv
    session_data_searchcv = create_session(agent_name="searchcv")
    print("Session Data:", session_data_searchcv)
    if session_data_searchcv:
        question = args.prompt
        print ("Prompt hr-agent:", question)
        response_data = ask_agent(session_data_searchcv, question)
        previous_summary = parse_cv_response(response_data)
        # Print the json in a readable format
        if response_data:
            print("Response Data:", json.dumps(response_data, indent=4))
            parse_cv_response(response_data)
        else:
            print("No response data received.")

    session_data_hr = create_session(agent_name="hr-agent")
    if session_data_hr:
        # question = f"Hi, I'm Marcello Martini, a computer science and engineering student at Politecnico di Milano. I was a professional swimmer.\n Previous summary: {previous_summary}"
        question = f"Previous summary: {previous_summary}"
        print ("Question:", question)
        response_data = ask_agent(session_data_hr, question)
        # Print the json in a readable format
        if response_data:
            print("Response Data:", json.dumps(response_data, indent=4))
            json.dump(parse_agent_response(response_data), open("response.json", "w"), indent=4)

        else:
            print("No response data received.")
    else:
        print("No session data available.")

    # Start whisper
    whisper_thread = threading.Thread(target=transcribe, args=('medium', session_data_hr, 1000, 10, 10))
    whisper_thread.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping...")
        stop_event.set()  # Signal the thread to stop
        whisper_thread.join()
        print("Thread has exited cleanly.")
        sys.exit(0)

    

    