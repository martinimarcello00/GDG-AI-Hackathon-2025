from google.adk.agents import Agent, SequentialAgent
from .tools import *
from .prompts import *

intro_agent = Agent(
    model='gemini-2.0-flash-001',
    name='intro_agent',
    description='An agent to filter the first user request',
    instruction=return_intro_agent_prompt(),
        tools=[store_user_query],
)

job_posting_agent = Agent(
    model='gemini-2.0-flash-001',
    name='job_posting_agent',
    description='An agent to get the job postings from LinkedIn',
    instruction=return_job_search_agent_prompt(),
    tools=[get_linkedin_jobs, get_web_page_content],
    output_key='jobs',
)

job_search_pipeline_agents = SequentialAgent(
    sub_agents=[intro_agent, job_posting_agent],
    name='job_search_pipeline_agents',
    description='A pipeline of agents to get the job postings from LinkedIn',
)

root_agent = job_search_pipeline_agents