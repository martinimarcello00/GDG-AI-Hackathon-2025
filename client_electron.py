#!/usr/bin/env python
import requests
import json
import random
import threading
import time
import sys
import os
import argparse
from pathlib import Path

# Path to write the response.json file
RESPONSE_FILE_PATH = Path(__file__).parent / "response.json"

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
        print(f"Session created successfully for {agent_name}.")
        return response.json()
    else:
        print(f"Failed to create session for {agent_name}: {response.status_code}")
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
    return {"followUp": followUp, "insights": insights, "summary": summary}

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
        print(f"Question sent successfully to {session_data['app_name']}.")
        return response.json()
    else:
        print(f"Failed to send question to {session_data['app_name']}: {response.status_code}")
        return None

def write_response_to_file(data):
    try:
        with open(RESPONSE_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Response written to {RESPONSE_FILE_PATH}")
    except Exception as e:
        print(f"Error writing response to file: {e}")

def process_user_query(user_prompt):
    previous_summary = ""
    
    # Create initial response with "processing" status
    initial_response = {
        "followUp": "Thinking of follow-up questions...",
        "insights": "Analyzing data...",
        "summary": ""
    }
    write_response_to_file(initial_response)
    
    # Step 1: Create session for searchcv
    session_data_searchcv = create_session(agent_name="searchcv")
    if session_data_searchcv:
        question = f"Find me a CV with information related to: {user_prompt}"
        response_data = ask_agent(session_data_searchcv, question)
        if response_data:
            previous_summary = parse_cv_response(response_data) or ""
            
            # Update response file with CV data
            update_response = {
                "followUp": "Preparing follow-up questions...",
                "insights": "Preparing insights...",
                "summary": previous_summary
            }
            write_response_to_file(update_response)
    
    # Step 2: Process with HR agent
    session_data_hr = create_session(agent_name="hr-agent")
    if session_data_hr:
        question = f"{user_prompt}\nPrevious summary: {previous_summary}"
        response_data = ask_agent(session_data_hr, question)
        
        if response_data:
            parsed_response = parse_agent_response(response_data)
            # Include the summary from CV agent
            parsed_response["summary"] = previous_summary
            write_response_to_file(parsed_response)
            return parsed_response
    
    # If we couldn't get data, return a default response
    default_response = {
        "followUp": "Couldn't generate follow-up questions.",
        "insights": "Couldn't generate insights.",
        "summary": previous_summary
    }
    write_response_to_file(default_response)
    return default_response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process user prompt and interact with the agent API')
    parser.add_argument('prompt', type=str, nargs='?', default="", help='User prompt for the agent')
    args = parser.parse_args()
    
    if not args.prompt:
        print("Error: No prompt provided. Please provide a prompt as a command-line argument.")
        sys.exit(1)
    
    try:
        result = process_user_query(args.prompt)
        print("Processing complete. Response data written to response.json")
        sys.exit(0)
    except Exception as e:
        print(f"Error processing query: {e}")
        error_response = {
            "followUp": f"Error: {str(e)}",
            "insights": "An error occurred while processing your request.",
            "summary": ""
        }
        write_response_to_file(error_response)
        sys.exit(1)
