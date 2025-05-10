from google.adk.tools import ToolContext

def retrieve_user_summary(tool_context: ToolContext) -> dict:
    """
    Retrieve the previous summary from the context.
    """
    prev_summary = tool_context.state.get("summary", "")
    if prev_summary:
        return {'status': 'success', 'message': 'Summary retrieved successfully.', 'summary': prev_summary}
    else:
        return {'status': 'error', 'message': 'No previous summary found.'}


def update_summary(summary: dict, tool_context: ToolContext) -> dict:
    """
    Store the user query in the context.
    """
    prev_summary = tool_context.state.get("summary")
    if prev_summary:
        tool_context.state["prev_summary"] = prev_summary
    tool_context.state["summary"] = summary
    return {'status': 'success', 'message': 'Summary update successfully.'}

def retrive_summaries(tool_context: ToolContext) -> dict:
    """
    Retrieve the previous summary and the new summary from the context.
    """
    prev_summary = tool_context.state.get("prev_summary", "")
    new_summary = tool_context.state.get("summary", "")

    return {
        'prev_summary': prev_summary,
        'new_summary': new_summary
    }
