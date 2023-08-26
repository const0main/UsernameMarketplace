import sqlite3
from datetime import datetime

connection = sqlite3.connect("assets/orders.db")
cursor = sqlite3.Cursor(connection)

cursor.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER, price INTEGER, username TEXT, created_at TEXT, unique_id INTEGER PRIMARY KEY AUTOINCREMENT)")
connection.commit()

def getAllOrders():
    cursor.execute("SELECT * FROM orders")
    result = cursor.fetchall()
    connection.commit()
    return result

def removeOrder(uniq_id: int):
    cursor.execute("DELETE FROM orders WHERE unique_id = ?", (uniq_id, ))
    connection.commit()

def getOrder(uniq_id: int) -> dict:
    cursor.execute(f"SELECT * FROM orders WHERE unique_id = (?)", (uniq_id,))
    result = cursor.fetchone()
    connection.commit()
    if result is not None:
        return {"id": result[0], "price": result[2], "username": result[1], "created": str(result[3]).replace(']', '').replace('[', '')}
    return None

def addOrder(id: int, price: int, username: str) -> None:
    current_date = datetime.now().strftime("[%d.%m-%H:%M]")
    cursor.execute("INSERT INTO orders (id, price, username, created_at) VALUES (?, ?, ?, ?)", (id, price, username, current_date))
    connection.commit()