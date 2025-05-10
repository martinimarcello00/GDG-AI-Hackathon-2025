import requests
import json

def create_session():
    url = "http://0.0.0.0:8000/apps/hr-agent/users/u_123/sessions/s_123"
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

if __name__ == "__main__":
    session_data = create_session()
    print("Session Data:", session_data)
    if session_data:
        question = "Hi, I'm Marcello Martini, a computer science and engineering student at Politecnico di Milano. I am interested in AI and machine learning."
        response_data = ask_agent(session_data, question)
        # Print the json in a readable format
        if response_data:
            print("Response Data:", json.dumps(response_data, indent=4))
        else:
            print("No response data received.")
    else:
        print("No session data available.")
    