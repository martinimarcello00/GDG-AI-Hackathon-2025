# TalentTrace 🚀

## GDG AI Hackathon 2025 - OverfittingExorcist Team 🤖

TalentTrace is an AI-powered job matching platform developed by the OverfittinExorcist Team for the GDG AI Hackathon 2025. The platform uses advanced AI agents to help **job hunters** find suitable positions and assists **HR recruiters** in identifying qualified candidates.

## Project Overview 🌟

TalentTrace integrates various AI agents and technologies to create a seamless experience for both job hunters and HR recruiters:

- **Voice-Enabled Interaction** 🎤: Real-time voice transcription using OpenAI's Whisper for hands-free operation
- **Multi-Agent System** 🧠: Specialized AI agents for different aspects of the job search and recruitment process
- **Resume Analysis** 📄: AI-powered CV parsing and skill extraction for efficient candidate screening
- **Personalized Job Recommendations & Candidate Matching** ✨: Matching candidates with suitable job opportunities and helping recruiters find the right talent

## Repository Structure 📁

- `adk-agents/`: Directory containing the various AI agents
  - `hr-agent/`: Agent for handling recruitment processes
  - `job_copilot_agent/`: Agent for assisting job seekers (not used in the demo)
  - `searchcv/`: Agent for analyzing and searching through CVs/resumes
- `ui/`: Directory containing the Electron-based user interface
  - `index.html`: Main HTML file for the UI
  - `index.js`: Main JavaScript file for Electron app logic
  - `api.js`: Handles communication with the backend/`response.json`
  - `package.json`: UI dependencies and scripts
- `whisper_realtime/`: Voice transcription module using OpenAI's Whisper
  - `transcribe.py`: Script for real-time audio transcription
  - `test.py`: Test script for the transcription module

## Setup and Installation 🛠️

### Prerequisites

- Python 3.11 or higher
- Node.js (for web interface)
- FFmpeg (for audio processing)

### Installation

1.  **Clone the Repository**
    ```bash
    # Clone the repository
    git clone https://github.com/your-username/TalentTrace.git
    cd TalentTrace
    ```

2.  **Setup Backend (Python & ADK Agents)**
    ```bash
    # Create and activate a virtual environment
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\\Scripts\\activate

    # Install Python dependencies
    pip install -r requirements.txt
    ```

3.  **Setup Frontend (Electron UI)**
    ```bash
    # Navigate to the UI directory
    cd ui

    # Install UI dependencies
    npm install

    # Go back to the root directory
    cd ..
    ```

## Usage 🚀

### 1. Starting the AI Agents

```bash
# Start the agent server
cd adk-agents
adk api_server
```
Make sure the ADK server is running before starting the client application.

### 2. Starting the Web Interface (Electron UI)
In another new terminal, from the project root directory:
```bash
# Navigate to the UI directory
cd ui

# Start the Electron application
npm start
```

## Team OverfittinExorcist 🧑‍💻

- Daniele Lagaanà
- Marcello Martini
- Gianluigi Palmisano
- Samuele Pozzani

## Acknowledgments 🙏

- GDG for organizing the AI Hackathon 2025
- Google ADK team for the AI agent development toolkit
- OpenAI for the Whisper speech-to-text model