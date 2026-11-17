def search(connection, owner):
    return connection.execute("SELECT owner, item FROM orders WHERE owner = ?", (owner,)).fetchall()
