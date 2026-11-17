import hmac
import threading
import time

class LoginService:
    def __init__(self, limit=3, window=30, clock=time.monotonic):
        self.limit, self.window, self.clock = limit, window, clock
        self.attempts = {}
        self.lock = threading.Lock()
    def login(self, user, password):
        with self.lock:
            now = self.clock()
            user = user.casefold()
            # Remove expired buckets to limit retained state.
            self.attempts = {u: [t for t in times if now - t < self.window] for u, times in self.attempts.items() if times and now - times[-1] < self.window}
            times = self.attempts.get(user, [])
            if len(times) >= self.limit or len(self.attempts) >= 1000 and user not in self.attempts:
                return 429, False
            valid = user == "alice" and hmac.compare_digest(password.encode(), b"dummy-correct-horse")
            if valid:
                self.attempts.pop(user, None)
                return 200, True
            self.attempts[user] = times + [now]
            return 401, False
