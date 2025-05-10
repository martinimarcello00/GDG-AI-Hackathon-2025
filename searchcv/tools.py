from google.adk.tools import ToolContext
import os

def find_cv(first_name: str, last_name: str):
    # Start from the user's Desktop
    curriculum_dir = os.path.join(os.path.expanduser('~'), 'curriculum')
    
    # File extensions considered as CVs
    cv_extensions = ['.pdf', '.docx', '.doc']

    # Convert to lowercase for case-insensitive matching
    first_name = first_name.lower()
    last_name = last_name.lower()

    for root, dirs, files in os.walk(curriculum_dir):
        for file in files:
            filename_lower = file.lower()
            if ((first_name in filename_lower or last_name in filename_lower) and 
                any(filename_lower.endswith(ext) for ext in cv_extensions)):
                print(f"Found it.")
                cv_path = os.path.join(root, file)
                return

    print(f"No CV found for {first_name} {last_name} on the Desktop.")

def open_cv(cv_path: str):
    # Open the CV file using the default application
    if os.path.exists(cv_path):
        os.startfile(cv_path)
    else:
        print(f"CV file not found at {cv_path}.")
