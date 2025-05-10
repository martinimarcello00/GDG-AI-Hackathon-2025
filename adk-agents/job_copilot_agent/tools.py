from google.adk.tools import ToolContext
import httpx

def store_user_query(query: dict, tool_context: ToolContext) -> dict:
    """
    Store the user query in the context.
    """
    print(f"Storing user query: {query}")

    tool_context.state["user_query"] = query
    return {'status': 'success', 'message': 'User query stored successfully.'}


async def get_linkedin_jobs(tool_context: ToolContext) -> dict:
    """
    Get the LinkedIn jobs based on the user query.
    """
   
    user_query = tool_context.state.get("user_query")
    if not user_query:
        return {'status': 'error', 'message': 'User query not found in context.'}
    
    url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    params = {
        "keywords": user_query['job_positions'],
        "location": user_query['location'],
        "trk": "public_jobs_jobs-search-bar_search-submit",
        "start": "0"
    }
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=1, i",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return {'status': 'error', 'message': f"Failed to fetch jobs: {response.status_code}"}
        else:
            return {'status': 'success', 'jobs': response.text, 'user_query': user_query}
        
async def get_web_page_content(url: str) -> dict:
    """
    Get the content of the web page.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            return {'status': 'error', 'message': f"Failed to fetch page content: {response.status_code}"}
        else:
            return {'status': 'success', 'content': response.text}