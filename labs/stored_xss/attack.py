from html.parser import HTMLParser
import sqlite3
from . import vulnerable, secure
from labs.support import outcome

PAYLOAD = "<script>window.__pipelineproof_xss=1</script>"
class Scripts(HTMLParser):
    def __init__(self):
        super().__init__(); self.count = 0
    def handle_starttag(self, tag, attrs):
        if tag == "script": self.count += 1

def database():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE comments (body TEXT NOT NULL)")
    return db

def demonstrate(work):
    db = database()
    try:
        vulnerable.add_comment(db, PAYLOAD)
        bad, good = vulnerable.render(db), secure.render(db)
        a, b = Scripts(), Scripts(); a.feed(bad); b.feed(good)
        secure.add_comment(db, "A normal synthetic comment")
        return outcome(a.count == 1, b.count == 0 and "&lt;script&gt;" in good,
                       "A normal synthetic comment" in secure.render(db),
                       {"stored_payload": PAYLOAD, "vulnerable_script_elements": a.count, "secure_script_elements": b.count, "browser_execution": "Tested separately with tests/browser_labs.py"})
    finally:
        db.close()
