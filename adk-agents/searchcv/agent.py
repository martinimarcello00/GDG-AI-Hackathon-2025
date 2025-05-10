import os
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from .tools import *

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='cv_agent',
    description='An assistant that finds CVs by candidate name.',
    instruction='''
        First, use the list_files_in_folder tool to list the files.
        Tell the user the list of filenames you found.
        Then, from the list, identify the file that contains the user's full name.
        Extract the base filename (without extension), use the read_cv_file to read everything in the file and print everything you've read.
        If no match is found, let the user know the CV could not be located.
        Return *ONLY* a markdown block with the following content:

        ##Candidate: <candidate full name>

        Current job title: <job title>

        Current company: <company>

        Current location: <location>

        Current email: <email>
        
        Current phone number: <phone number>

        ## Education
        <list of the education in the cv as bulleted list>
        
        ## Personal experience
        <list of the experiences in the cv as bulleted list>

        ## Skills
        <list of the skills in the cv as bulleted list>

        ## Languages
        <list of the languages in the cv as bulleted list>

        ## Relevant activities
        <list of the relevant activities in the cv as bulleted list>
    ''',
    tools=[list_files_in_folder, read_cv_file]
)

