import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        conn = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", "12345678"),
            database=os.getenv("DB_NAME", "chatdb"),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return conn
    except Exception as e:
        print("DB Connection Error:", e)
        return None

def execute(query, params=None, fetch=False):
    """
    execute a query
    fetch=True -> return fetched rows (SELECT)
    fetch=False -> return lastrowid (INSERT/UPDATE/DELETE)
    """
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            if fetch:
                return cur.fetchall()
            return cur.lastrowid
    finally:
        conn.close()
