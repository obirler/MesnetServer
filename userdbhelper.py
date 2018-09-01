from flask import g
import sqlite3
import config

def connectDb():
    '''
    open a database connection and return connection and cursor
    '''
    conn = sqlite3.connect(config.USER_DB_NAME)
    cur = conn.cursor()
    return conn, cur

def getDb():
    if not hasattr(g, 'db'):
        g.db = connectDb()
    return g.db

def resetDb():
    conn, cur = getDb()

    # DROP TABLES
    query="DROP TABLE IF EXISTS users;"
    cur.execute(query)

    # CREATE TABLES
    query = """CREATE TABLE users(id INTEGER PRIMARY KEY,
                                     username TEXT,
                                     appname TEXT,
                                     version TEXT,
                                     createdate TEXT,
                                     senddate TEXT,
                                     userid TEXT)"""
    cur.execute(query)

    query = '''INSERT INTO users(username, appname, version, createdate, senddate, userid) VALUES(?,?,?,?,?,?)'''

    conn.commit()