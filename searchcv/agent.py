import os
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from pypdf import PdfReader



def read_cv_file(filename: str):
    folder_path = os.path.join(os.path.expanduser("~"), "/Users/gianl_2/OneDrive/Desktop/curriculum/")
    full_path = os.path.join(folder_path, filename)
    print(f"Reading CV file: {full_path}")

    try:
        reader = PdfReader(full_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
                #open the file with the default application
                os.startfile(full_path)
            
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {e}"


def list_files_in_folder():
    folder_path = os.path.join(os.path.expanduser("~"),  "/Users/gianl_2/OneDrive/Desktop/curriculum")
    try:
        return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    except FileNotFoundError:
        return []


# Configure the agent with tools
root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='cv_agent',
    description='An assistant that finds CVs by candidate name.',
    instruction=(
        "First, use the list_files_in_folder tool to list the files in ~/Users/gianl_2/OneDrive/Desktop/curriculum. "
        "Tell the user the list of filenames you found. "
        "Then, from the list, identify the file that contains the user's full name. "
        "Extract the base filename (without extension), use the read_cv_file to read everything in the file and print everything you've read. "
        "If no match is found, let the user know the CV could not be located."
    ),
    tools=[list_files_in_folder, read_cv_file]
)

