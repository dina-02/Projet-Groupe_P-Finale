"""
Launch script for the Streamlit application.

This script determines the absolute path to the main application file (`main.py`)
and launches it using the `streamlit run` command via the operating system shell.

Usage:
    Run this script directly from the terminal or an IDE to start the Streamlit web app.

Note:
    This script must be executed as a standalone Python script,
    not from within the Streamlit environment.
"""

import os

# Define the name of the main Streamlit entry point
APP_ENTRY_POINT = "main.py"

# Get the current directory where this script is located
dir_path = os.path.dirname(__file__)

# Construct the full path to the main application script
path = os.path.join(dir_path, APP_ENTRY_POINT)

# Run the Streamlit application using a shell command
os.system(f'streamlit run "{path}"')


