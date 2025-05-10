from google.adk.tools import ToolContext

def update_user_query(summary: dict, tool_context: ToolContext) -> dict:
    """
    Store the user query in the context.
    """
    tool_context.state["prev_summary"] = tool_context.state["summary"]
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
