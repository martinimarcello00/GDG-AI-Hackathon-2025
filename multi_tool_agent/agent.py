from google.adk.agents import Agent
from .tools import store_user_query
from .prompts import *

intro_agent = Agent(
    model='gemini-2.0-flash-001',
    name='intro_agent',
    description='An agent to filter the first user request',
    instruction=return_intro_agent_prompt(),
        tools=[store_user_query],
)

root_agent = intro_agent