"""Shared constants."""

import os

USERNAME = "Brendan"
AGENT_NAME = "Higgins"

# Some files are platform specific like mac_automation.py.
# To avoid loading them, we only load files that contain actions
# which are determined by looking for file with this suffix.
ACTION_FILE_SUFFIX = "_actions.py"
INTENT_FILE_SUFFIX = "_intents.py"

OPENAI_CACHE_DIR = "openai_cache/"

DEBUG_MODE = bool(os.getenv("DEBUG_HIGGINS", False))

# Database
TINY_DB_PATH = "data/tinydb.json"
EPISODE_JSONL_PATH = "data/episodes.jsonl"
