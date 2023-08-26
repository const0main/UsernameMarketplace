import sqlite3

connection = sqlite3.connect("assets/buy.db")
cursor = sqlite3.Cursor(connection)

cursor.execute("CREATE TABLE IF NOT EXISTS purchases (id INTEGER PRIMARY KEY AUTOINCREMENT, sellId INTEGER, buyId INTEGER, username TEXT, price INTEGER, buySuccess INTEGER, sellSuccess INTEGER, status INTEGER)")
connection.commit()

def getPurchase(sellId: int):
    cursor.execute("SELECT * FROM purchases WHERE sellId = ?", (sellId, ))
    connection.commit()
    return cursor.fetchone()

def getAllPurchases():
    cursor.execute("SELECT * FROM purchases")
    connection.commit()
    return cursor.fetchall()

def createBuyOrder(sell_id: int, buy_id: int, username: str, price: int) -> None:
    cursor.execute("INSERT INTO purchases (sellId, buyId, username, price, buySuccess, sellSuccess, status) VALUES (?, ?, ?, ?, ?, ?, ?)", (sell_id, buy_id, username, price, 0, 0, 0))
    connection.commit()

def setOrderStatus(purchase_id: int, status: int) -> None:
    if purchase_id == 1:
        cursor.execute("UPDATE purchases SET buySuccess = ? WHERE id = ?", (status, ))
    elif purchase_id == 2:
        cursor.execute("UPDATE purchases SET sellSuccess = ? WHERE id = ?", (status, ))
    connection.commit()

def removePurchase(uniq_id: int) -> None:
    cursor.execute("DELETE FROM purchases WHERE id = ?", (uniq_id, ))
    connection.commit()


def getGeneralStatus(purchase_id: int) -> bool:
    cursor.execute("SELECT * FROM purchases WHERE id = ?", (purchase_id))
    result = cursor.fetchone()
    connection.commit()

    if result[len(result) - 1] == 1:
        return True
    return False

