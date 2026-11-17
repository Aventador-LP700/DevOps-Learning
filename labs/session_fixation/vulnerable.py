import secrets

class SessionStore:
    def __init__(self):
        self.sessions = {}
    def start(self):
        sid = secrets.token_urlsafe(24)
        self.sessions[sid] = None
        return sid
    def login(self, sid, authenticated_user):
        self.sessions[sid] = authenticated_user  # Retains a pre-authentication identifier.
        return sid
    def user(self, sid):
        return self.sessions.get(sid)
