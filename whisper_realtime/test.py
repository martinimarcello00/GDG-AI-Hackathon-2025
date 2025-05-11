from whisper_realtime.transcribe import transcribe
import requests
import json
import random

host = 'localhost:8000'
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




if __name__ == "__main__":
    # Initialize the transcriber
    session_data = create_session(agent_name="hr-agent")
    print(session_data)
    # if session_data is None:
    #     print("Failed to create session.")
    #     exit(1)
    # transcribe(session=session_data, model="medium")
