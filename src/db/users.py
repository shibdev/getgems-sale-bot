import sqlite3
import json

con = sqlite3.connect("db.sqlite")
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS Users (
                uid INTEGER,
                address STRING
            )""")
con.commit()


def get_user_address(uid):
    cur.execute("SELECT address FROM Users WHERE uid = ?", (uid,))
    return cur.fetchone()[0]

def check_user(uid):
    cur.execute("SELECT * FROM Users WHERE uid = ?", (uid,))
    user = cur.fetchone()
    if user:
        return True
    return False

def check_address(address):
    cur.execute("SELECT * FROM Users WHERE address = ?", (address,))
    user = cur.fetchone()
    if user:
        return True
    return False

def add_user(uid, address):
    cur.execute("INSERT INTO Users VALUES (?, ?)", (uid, address,))
    con.commit()

def delete_user(uid):
    cur.execute("DELETE FROM Users WHERE uid = ?", (uid,))
    con.commit()
