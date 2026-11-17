import traceback

def handle(operation):
    try:
        return 200, {"result": operation()}
    except Exception:
        return 500, {"debug": traceback.format_exc(), "config": {"database": "synthetic-db", "password": "lab-only"}}
