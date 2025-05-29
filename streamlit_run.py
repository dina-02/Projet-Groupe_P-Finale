"""
Script to launch the Streamlit application.

This script constructs the full path to the main Streamlit entry point (main.py)
and executes it using the `streamlit run` command.

It should be run as a standalone Python script to start the app.
"""

import os

APP_ENTRY_POINT = "main.py"

dir_path = os.path.dirname(__file__)
path = os.path.join(dir_path, APP_ENTRY_POINT)
os.system(f'streamlit run "{path}"')


