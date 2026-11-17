def search(connection, owner):
    query = "SELECT owner, item FROM orders WHERE owner = '" + owner + "'"
    return connection.execute(query).fetchall()
