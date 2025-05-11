from google.adk.tools import ToolContext
import subprocess, os, platform
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
        
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(['open', full_path])
            # Position window using AppleScript
            applescript = '''
            tell application "System Events"
                delay 0.5
                set frontApp to name of first application process whose frontmost is true
                tell process frontApp
                    set position of front window to {0, 22}
                    set size of front window to {500, 900}
                end tell
            end tell
            '''
            subprocess.run(['osascript', '-e', applescript])
        elif platform.system() == 'Windows':    # Windows
            os.startfile(full_path)
            # For Windows, you would need pywin32 for window positioning
            # Basic opening is done without positioning
        else:                                   # linux variants
            subprocess.call(['xdg-open', full_path])
            # For Linux with X11, you could use wmctrl if installed:
            # import time
            # time.sleep(1)
            # subprocess.call(['wmctrl', '-r', os.path.basename(full_path), '-e', '0,0,0,500,700'])

        
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
