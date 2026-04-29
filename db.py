import os
import pymysql

def get_connection():
    try:
        return pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            port=int(os.environ["DB_PORT"]),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
            connect_timeout=5
        )
    except Exception as e:
        print("DB ERROR:", e)
        return None


def execute(query, params=None, fetch=False):
    conn = get_connection()

    if not conn:
        return None

    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchall() if fetch else cur.lastrowid
    except Exception as e:
        print("QUERY ERROR:", e)
        return None
    finally:
        conn.close()
