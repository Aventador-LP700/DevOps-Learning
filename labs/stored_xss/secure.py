import html

def add_comment(db, text):
    if not isinstance(text, str) or len(text) > 2000:
        raise ValueError("Invalid comment")
    db.execute("INSERT INTO comments (body) VALUES (?)", (text,))
    db.commit()

def render(db):
    return "<h1>Lab comments</h1>" + "".join("<article>" + html.escape(row[0], quote=True) + "</article>" for row in db.execute("SELECT body FROM comments"))
