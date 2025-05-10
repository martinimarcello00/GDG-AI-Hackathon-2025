from google.adk.agents import Agent
from google.adk.tools import ToolContext

def store_user_query(query: dict, tool_context: ToolContext) -> dict:
    """
    Store the user query in the context.
    """
    print(f"Storing user query: {query}")

    tool_context.state["user_query"] = query
    return {'status': 'success', 'message': 'User query stored successfully.'}

intro_agent = Agent(
    model='gemini-2.0-flash-001',
    name='intro_agent',
    description='An agent to filter the first user request',
    instruction='''
        ## Agent Purpose
        You are an agent designed to initiate a workflow that assists users in finding a suitable job opportunity.

        ## Your Responsibilities
        Analyze the information provided by the user to identify the following key details:

        1. Type of contract the user is seeking (e.g., internship, thesis, full-time employment).  
        2. Preferred job positions (optional — the user will share their CV in a later step, which may clarify this).  
        3. Desired job location (city, region, or country).  
        4. Work setting preference — whether the user is looking for on-site, remote, or hybrid opportunities.

        If all the required information is not provided, ask the user for the missing details.
        If you have all the informations, then use the tool 'store_user_query(query: dict)' to store a dictionary with the following keys:
        - contract_type: the type of contract the user is looking for.
        - job_positions: the job positions the user is looking for (null if not provided).
        - location: the location the user is looking for.
        - work_setting: the work setting the user is looking for

        ## Example
        User: I am looking for a full-time job in Paris, preferably in cloud arichitect field.
        Agent: query = {
            'contract_type': 'full-time',
            'job_positions': 'cloud arichitect',
            'location': 'Paris',
            'work_setting': null
        }

        ## Tools you can use:
        - store_user_query(query: dict): Use this tool to store the user query in the context. The query should be a dictionary with the keys: contract_type, job_positions, location, work_setting.
        ''',
        tools=[store_user_query],
)

root_agent = intro_agent