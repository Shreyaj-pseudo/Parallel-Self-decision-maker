import json
import os

SESSION_FILE = "sessions.json"

def load_sessions():
    """Returns a dictionary of {name: thread_id}."""
    if not os.path.exists(SESSION_FILE):
        return {}
    try:
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_session(name, thread_id):
    """Saves or updates a thread ID associated with a name."""
    sessions = load_sessions()
    sessions[name] = str(thread_id)
    with open(SESSION_FILE, "w") as f:
        json.dump(sessions, f, indent=4)