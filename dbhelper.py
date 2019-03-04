from flask import g
import sqlite3
import config

def connectDb():
    '''
    open a database connection and return connection and cursor
    '''
    conn = sqlite3.connect(config.DB_NAME)
    cur = conn.cursor()
    return conn, cur

def getDb():
    if not hasattr(g, 'db'):
        g.db = connectDb()
    return g.db

def resetDb():
    conn, cur = getDb()

    # DROP TABLES
    query="DROP TABLE IF EXISTS logs;"
    cur.execute(query)

    # CREATE TABLES
    query = """CREATE TABLE logs(id INTEGER PRIMARY KEY,
                                     username TEXT,
                                     appname TEXT,
                                     version TEXT,
                                     type TEXT,
                                     createdate TEXT,
                                     senddate TEXT,
                                     content TEXT)"""
    cur.execute(query)

    conn.commit()

def getUserDb():
    if not hasattr(g, 'db'):
        g.db = connectDb()
    return g.db

def resetUserDb():
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
    conn.commit()

def resetSettingsDb():
    conn, cur = getDb()
    # DROP TABLES
    query="DROP TABLE IF EXISTS settings;"
    cur.execute(query)
    # CREATE TABLES
    query = """CREATE TABLE settings(id INTEGER PRIMARY KEY,
                                     key TEXT NOT NULL UNIQUE,
                                     value TEXT)"""
    cur.execute(query)
    conn.commit()

def resetDownloadsDb():
    conn, cur = getDb()
    # DROP TABLES
    query = "DROP TABLE IF EXISTS downloads;"
    cur.execute(query)
    # CREATE TABLES
    query = """CREATE TABLE downloads(id INTEGER PRIMARY KEY,
                                     key TEXT NOT NULL UNIQUE,
                                     value TEXT)"""
    cur.execute(query)
    conn.commit()