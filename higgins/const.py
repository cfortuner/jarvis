# Shared constants
USERNAME = "Brendan"
AGENT_NAME = "Higgins"

# Some files are platform specific like mac_automation.py.
# To avoid loading them, we only load files that contain actions
# which are determined by looking for file with this suffix.
BEHAVIOR_FILE_SUFFIX = "_actions.py"

OPENAI_CACHE_DIR = "openai_cache/"
