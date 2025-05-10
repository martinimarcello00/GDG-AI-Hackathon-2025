from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from .tools import *
from .prompts import *
from google.adk.tools import google_search


summarize_conversation_agent = Agent(
    model='gemini-2.0-flash-001',
    name='summarize_conversation_agent',
    description='An agent that summarizes the conversation.',
    instruction=return_summary_conversation_agent_prompt(),
    tools=[update_user_query],
    output_key='struct_info',
)

followup_agent = Agent(
    model='gemini-2.0-flash-001',
    name='followup_agent',
    description='An agent that generates follow up questions.',
    instruction=return_follow_up_questions_prompt(),
    tools=[retrive_summaries],
    output_key='follow_up_questions',
)

insights_agent = Agent(
    model='gemini-2.0-flash-001',
    name='insights_agent',
    description='An agent that generates useful insights.',
    instruction=return_useful_insights_prompt(),
    tools=[google_search],
    output_key='useful_insights',
)

parallel_agent = ParallelAgent(
    sub_agents=[followup_agent, insights_agent],
    name='parallel_agent',
    description='An agent that generates follow up questions and useful insights.',
)

sequential_agent = SequentialAgent(
    sub_agents=[summarize_conversation_agent, parallel_agent],
    name='sequential_agent',
    description='An agent that summarizes the conversation and generates follow up questions and useful insights.',
)

root_agent = sequential_agent

