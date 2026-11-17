from pathlib import Path
import pickle

def write_marker(path):
    Path(path).write_text("LAB_PICKLE_EXECUTED")
    return {"user": "alice", "theme": "dark"}

def restore(payload):
    return pickle.loads(payload)  # Untrusted pickle may invoke callables.
