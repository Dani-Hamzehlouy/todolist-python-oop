# src/core/config.py

import os
from dotenv import load_dotenv

# Load environment variables from the .env file.
# NOTE: In production, .env files are often placed outside the project root for security.
# For this phase, we assume it's loaded from the current working directory.
load_dotenv()


class Config:
    """
    Configuration class to hold application settings loaded from the environment.
    This includes mandatory limits for projects and tasks.
    """
    # Functional Requirement: Apply maximum limits from environment variables[cite: 135].
    MAX_NUMBER_OF_PROJECT = int(os.getenv("MAX_NUMBER_OF_PROJECT", 5))
    MAX_NUMBER_OF_TASK = int(os.getenv("MAX_NUMBER_OF_TASK", 20))

    # Task status and word limits defined in models.py could also be moved here
    # for full separation, but we keep them with the models for now.
