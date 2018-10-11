# -*- coding: utf-8 -*-
import psycopg2, config

def db_connect():
    try:
        global conn, cur
        conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (config.dbname, config.dbuser, config.dbhost, config.dbpass))
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS table_status(
                     user_id VARCHAR (50) PRIMARY KEY,
                     username VARCHAR (50) NOT NULL,
                     status VARCHAR (50) NOT NULL,
                     app VARCHAR (50),
                     action VARCHAR (50),
                     stand VARCHAR (50),
                     version VARCHAR (50),
                     issue VARCHAR (50),
                     time_when TIMESTAMP);""")
    except:
        print("I am unable to connect to the database: %s" % config.dbhost)
        exit()


def db_state(message):
    db_connect()
    cur.execute("SELECT user_id FROM table_status;")
    user_list = cur.fetchone()
    if user_list == None:
        cur.execute("INSERT INTO table_status VALUES (" + str(message.chat.id) + ", '" + str(message.chat.username) + "', 'menu');")
    cur.execute('SELECT status FROM table_status;')
    user_status = cur.fetchone()
    if user_status == None:
        cur.execute("UPDATE table_status SET status = 'menu' WHERE user_id = '" + str(message.chat.id) + "';")
        cur.execute('SELECT status FROM table_status;')
        user_status = cur.fetchone()
    return user_status


def db_step(message, column, value, status_value):
    db_connect()
    cur.execute("UPDATE table_status SET " + column + " = '" + value +"', status = '" + status_value + "' WHERE user_id = '" + str(message.chat.id) + "';")
