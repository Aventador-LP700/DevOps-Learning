import secrets
from labs.support import Denied

class SessionStore:
    def __init__(self):
        self.sessions = {}
    def start(self):
        sid = secrets.token_urlsafe(24)
        self.sessions[sid] = None
        return sid
    def login(self, sid, authenticated_user):
        if sid not in self.sessions:
            raise Denied("Unknown pre-authentication session")
        self.sessions.pop(sid)
        rotated = secrets.token_urlsafe(24)
        self.sessions[rotated] = authenticated_user
        return rotated
    def user(self, sid):
        return self.sessions.get(sid)
