from google.adk.tools import ToolContext
import os
from pypdf import PdfReader

def read_cv_file(filename: str):
    folder_path = os.path.join(os.path.expanduser("~"), "Desktop/CV")
    full_path = os.path.join(folder_path, filename)
    print(f"Reading CV file: {full_path}")

    try:
        reader = PdfReader(full_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        
        # Open the file with the default application (macOS specific)
        # os.system(f"open '{full_path}'")
        
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {e}"

def list_files_in_folder():
    folder_path = os.path.join(os.path.expanduser("~"), "Desktop/CV")
    try:
        return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    except FileNotFoundError:
        return []
