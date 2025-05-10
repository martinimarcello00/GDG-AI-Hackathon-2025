from google.adk.tools import ToolContext

def store_user_query(query: dict, tool_context: ToolContext) -> dict:
    """
    Store the user query in the context.
    """
    print(f"Storing user query: {query}")

    tool_context.state["user_query"] = query
    return {'status': 'success', 'message': 'User query stored successfully.'}