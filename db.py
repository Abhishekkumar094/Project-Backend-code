import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        conn = pymysql.connect(
            host=os.environ["DB_HOST"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASS"],
            database=os.environ["DB_NAME"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return conn
    except Exception as e:
        print("DB Connection Error:", e)
        return None


def execute(query, params=None, fetch=False):
    conn = get_connection()
    if not conn:
        return None

    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            if fetch:
                return cur.fetchall()
            return cur.lastrowid
    except Exception as e:
        print("Query Error:", e)
        return None
    finally:
        conn.close()
