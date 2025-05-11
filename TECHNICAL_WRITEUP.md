# TalentTrace: Technical Write-up

## 1. Introduction

TalentTrace is an AI prototype for streamlining recruitment using a multi-agent system via the Google Agent Development Kit (ADK). It automates CV parsing, summarization, generates interview follow-ups, and offers HR insights, featuring voice-enabled interaction. Developed for the GDG AI Hackathon 2025, it showcases AI agent collaboration for complex workflows and unstructured data processing.

## 2. ADK Implementation

TalentTrace uses the Google ADK to manage two primary agents: `searchcv` and `hr-agent`.

### 2.1. `searchcv` Agent (`adk-agents/searchcv/`)

* **Purpose**: Finds and processes CVs.
* **Functionality**: Lists files in a predefined folder, identifies the CV matching a user's query, reads its content, and extracts key information in a structured format.

### 2.2. `hr-agent` (`adk-agents/hr-agent/`)

* **Purpose**: Simulates an HR interview assistant.
* **Structure**: A `SequentialAgent` orchestrates sub-agents:
  1. `summarize_conversation_agent`: Integrates new user information with a previous summary and identifies key entities.
  2. `parallel_agent`: Concurrently runs:
     * `followup_agent`: Generates follow-up questions based on summary changes.
     * `insights_agent`: Uses Google Search on identified entities to provide HR-relevant insights.
  3. `retrieve_user_summary_agent`: Returns the final updated summary.
* **Interaction**: Takes an initial summary (e.g., from `searchcv`), interacts with the user (potentially via voice), updates the summary, and generates outputs.

### 2.3. `job_copilot_agent` (`adk-agents/job_copilot_agent/`)

This agent exists in the repository structure, but its specific role and integration into the main workflow are not explicitly detailed. It's presumed to be an agent for assisting job seekers.

## 3. Workflow

The prototype's workflow involves an Electron framework-based UI, a client script (`client.py`), ADK agents, and real-time voice transcription.

1. **User Interaction (Initial Prompt)**:
   * The user interacts with an Electron framework-based UI (source files in the `ui/` folder). This UI is quite limited but effective for its purpose.
   * The UI sends the user's initial prompt (e.g., "Find the CV for Marcello Martini") to `client.py`.

2. **CV Retrieval and Parsing**:
   * `client.py` uses the `searchcv` agent to find the relevant CV and extract a summary.

3. **HR Agent Interaction**:
   * `client.py` sends the CV summary to the `hr-agent`.
   * The `hr-agent` processes this information through its sequence of sub-agents (summarizing, generating follow-up questions and insights).

4. **Displaying Results**:
   * `client.py` receives outputs from the `hr-agent` (follow-up, insights, summary) and writes them to `response.json`.
   * The Electron UI reads `response.json` to display the information.

5. **Voice Interaction (Continuous Loop)**:
   * `client.py` initiates `whisper_realtime/transcribe.py` for voice input.
   * Transcribed text is sent to the active `hr-agent` session.
   * The agent's response updates `response.json`, which in turn refreshes the Electron UI, allowing for continuous interaction.

## 4. Limits of the Implementation

The TalentTrace prototype has several limitations:

* **Error Handling**: Basic; known issues like an `OpenTelemetry ValueError` with parallel agents can occur.
* **Hardcoded Elements**: Paths (e.g., CV folder `~/Desktop/CV/`) and configurations (e.g., agent host) are hardcoded. API keys in `.env` files pose a security risk.
* **State Management**: `response.json` for state passing between `client.py`/`transcribe.py` and the UI could lead to race conditions. Session management is basic.
* **Scalability**: Local Whisper model usage is resource-intensive. The system is designed for single-user local operation.
* **Incomplete Modules**: `client_electron.py` seems unfinished. The `job_copilot_agent` is not fully integrated.
* **Voice Interaction**: Transcription quality depends on environment and setup.
* **ADK Usage**: Prompt engineering may need refinement for complex scenarios.
* **Security**: Lacks user authentication/authorization.
* **UI**: The Electron UI (in `ui/`) is functional but basic, offering limited features.

## 5. Possible Future Features

Future enhancements could include:

* **Robustness & Scalability**: Improved error handling, resolving OpenTelemetry issues, cloud storage for CVs, containerization.
* **User Experience**: Develop a more comprehensive web interface (extending the current `ui/` Electron base), user accounts, and interactive feedback.
* **Advanced AI Capabilities**: Fully integrate `job_copilot_agent`, enhance NLP, develop job matching algorithms, enable dynamic agent tooling.
* **Expanded Functionality**: Integrate with job boards, calendar for scheduling, automated screening, user feedback loops.
* **Configuration & Customization**: User-configurable settings instead of hardcoding.
* **Multi-language Support**.
* **Analytics & Reporting**.
