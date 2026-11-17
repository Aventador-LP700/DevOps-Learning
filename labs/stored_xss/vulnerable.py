def add_comment(db, text):
    db.execute("INSERT INTO comments (body) VALUES (?)", (text,))
    db.commit()

def render(db):
    return "<h1>Lab comments</h1>" + "".join("<article>" + row[0] + "</article>" for row in db.execute("SELECT body FROM comments"))
