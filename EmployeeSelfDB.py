import sqlite3

DB_NAME = "employee_data.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS records (
        date TEXT PRIMARY KEY,
        hours REAL,
        in_time TEXT,
        out_time TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

def init_pin_table():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS app_config (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_user_name(name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO app_config VALUES('user_name', ?)", (name,))
    conn.commit()
    conn.close()

def get_user_name():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT value FROM app_config WHERE key='user_name'")
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def save_pin(pin):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO app_config VALUES('app_pin', ?)", (pin,))
    conn.commit()
    conn.close()

def get_pin():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT value FROM app_config WHERE key='app_pin'")
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def save_record_db(d, in_time, out_time, hours, status):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    INSERT OR REPLACE INTO records (date, hours, in_time, out_time, status)
    VALUES (?, ?, ?, ?, ?)
    """, (str(d), hours, in_time, out_time, status))

    conn.commit()
    conn.close()

def load_records_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT date, hours, status, in_time, out_time FROM records")
    rows = c.fetchall()
    conn.close()

    data = {}
    for r in rows:
        data[r[0]] = {
            "hours": r[1],
            "status": r[2],
            "in_time": r[3],
            "out_time": r[4]
        }
    return data
