"""
config.py

Responsible for loading environment variables using python-dotenv,
and providing them to the rest of the application.
"""

import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST: str = os.getenv("DB_HOST")
DB_NAME: str = os.getenv("DB_NAME")
DB_USER: str = os.getenv("DB_USER")
DB_PASS: str = os.getenv("DB_PASS")
DB_PORT: str = os.getenv("DB_PORT")
API_KEY: str = os.getenv("API_KEY")