import sqlite3

connection = sqlite3.connect("assets/users.db")
cursor = sqlite3.Cursor(connection)

cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance INTEGER, phone TEXT)")
connection.commit()

def getBalance(id: int) -> int:
    cursor.execute(f"SELECT balance FROM users WHERE id = {id}")
    result = cursor.fetchone()
    connection.commit()
    return result
    
def setBalance(id: int, new_balance: int) -> None:
    cursor.execute(f"UPDATE users SET balance = balance + {new_balance} WHERE id = {id}")
    connection.commit()

def addUser(id: int, phone: int) -> None:
    cursor.execute("INSERT INTO users (id, balance, phone) VALUES (?, ?, ?)", (id, 0, phone))
    connection.commit()

def getUser(id: int) -> dict:
    cursor.execute(f"SELECT * FROM users WHERE id = {id}")
    result = cursor.fetchone()
    connection.commit()
    if result is not None:
        return {'id': result[0], 'balance': result[1], 'phone': result[2]}
    return None