import hmac

class LoginService:
    def login(self, user, password):
        valid = user == "alice" and hmac.compare_digest(password.encode(), b"dummy-correct-horse")
        return (200, True) if valid else (401, False)
