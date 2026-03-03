import sqlite3
import uuid
import re
from datetime import datetime

DB_NAME = "users.db"

# =========================
# PASSWORD VALIDATION
# =========================
def validate_password(password):

    if not password:
        return "Password cannot be empty."

    if len(password) < 8:
        return "Password must be at least 8 characters long."

    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."

    if not re.search(r"[0-9]", password):
        return "Password must contain at least one number."

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character."

    return None


# =========================
# CREATE TABLES
# =========================
def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        name TEXT,
        email TEXT PRIMARY KEY,
        password TEXT,
        company TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        chat_id TEXT PRIMARY KEY,
        email TEXT,
        user_name TEXT,
        company TEXT,
        title TEXT,
        assistant_name TEXT,
        total_messages INTEGER DEFAULT 0,
        last_response_time REAL,
        avg_response_time REAL,
        is_hidden INTEGER DEFAULT 0,
        created_at TEXT,
        updated_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        chat_id TEXT,
        email TEXT,
        role TEXT,
        content TEXT,
        model TEXT,
        response_time REAL,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


# =========================
# SIGNUP (Validate but Store Original Password)
# =========================
def signup_user(name, email, password, company):

    validation_error = validate_password(password)
    if validation_error:
        return validation_error

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT email FROM users WHERE email=?", (email,))
    if cursor.fetchone():
        conn.close()
        return "Email already registered."

    # Store password as original (no hashing)
    cursor.execute(
        "INSERT INTO users (name, email, password, company) VALUES (?, ?, ?, ?)",
        (name, email, password, company)
    )

    conn.commit()
    conn.close()

    return "success"


# =========================
# LOGIN (Compare Plain Password)
# =========================
def login_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, company FROM users WHERE email=? AND password=?",
        (email, password)
    )

    user = cursor.fetchone()
    conn.close()
    return user


# =========================
# CREATE NEW CHAT
# =========================
def create_new_chat(email, user_name, company):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    chat_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    cursor.execute("""
        INSERT INTO chats
        (chat_id, email, user_name, company, title, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (chat_id, email, user_name, company, "", now, now))

    conn.commit()
    conn.close()
    return chat_id


# =========================
# UPDATE CHAT TITLE
# =========================
def update_chat_title(chat_id, title):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE chats SET title=?, updated_at=? WHERE chat_id=?",
        (title, datetime.utcnow().isoformat(), chat_id)
    )

    conn.commit()
    conn.close()


# =========================
# HIDE CHAT
# =========================
def hide_chat(chat_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE chats SET is_hidden=1 WHERE chat_id=?",
        (chat_id,)
    )

    conn.commit()
    conn.close()


# =========================
# SAVE MESSAGE
# =========================
def save_message(chat_id, email, role, content, model=None, response_time=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    now = datetime.utcnow().isoformat()

    cursor.execute("""
        INSERT INTO messages
        (chat_id, email, role, content, model, response_time, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (chat_id, email, role, content, model, response_time, now))

    if role == "assistant":
        cursor.execute("SELECT total_messages, avg_response_time FROM chats WHERE chat_id=?", (chat_id,))
        data = cursor.fetchone()

        total = (data[0] or 0) + 1
        old_avg = data[1] or 0
        new_avg = ((old_avg * (total - 1)) + response_time) / total

        cursor.execute("""
            UPDATE chats
            SET assistant_name=?,
                total_messages=?,
                last_response_time=?,
                avg_response_time=?,
                updated_at=?
            WHERE chat_id=?
        """, (model, total, response_time, new_avg, now, chat_id))

    else:
        cursor.execute(
            "UPDATE chats SET updated_at=? WHERE chat_id=?",
            (now, chat_id)
        )

    conn.commit()
    conn.close()


# =========================
# GET USER CHATS
# =========================
def get_user_chats(email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT chat_id, title
        FROM chats
        WHERE email=? AND is_hidden=0
        ORDER BY updated_at DESC
    """, (email,))

    data = cursor.fetchall()
    conn.close()
    return data


# =========================
# LOAD CHAT MESSAGES
# =========================
def get_chat_messages(chat_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, content, model, response_time
        FROM messages
        WHERE chat_id=?
        ORDER BY timestamp ASC
    """, (chat_id,))

    data = cursor.fetchall()
    conn.close()

    return [
        {
            "role": r,
            "content": c,
            "model": m,
            "response_time": t
        }
        for r, c, m, t in data
    ]


create_tables()