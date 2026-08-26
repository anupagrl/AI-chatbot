import sqlite3
from datetime import datetime


DB_NAME = "memory.db"


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def init_memory_db():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# ADD MEMORY
# =========================================================

def add_memory(memory, category="general"):

    if not memory:
        return False

    memory = memory.strip()

    if not memory:
        return False

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    # Prevent duplicate memories
    cursor.execute("""
        SELECT id
        FROM memories
        WHERE LOWER(memory) = LOWER(?)
    """, (memory,))

    existing = cursor.fetchone()

    if existing:

        conn.close()

        return False

    cursor.execute("""
        INSERT INTO memories
        (memory, category, created_at)
        VALUES (?, ?, ?)
    """, (
        memory,
        category,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()

    conn.close()

    return True


# =========================================================
# GET ALL MEMORIES
# =========================================================

def get_all_memories():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, memory, category, created_at
        FROM memories
        ORDER BY id DESC
    """)

    memories = cursor.fetchall()

    conn.close()

    return memories


# =========================================================
# SEARCH MEMORIES
# =========================================================

def search_memories(keyword):

    if not keyword:
        return []

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, memory, category, created_at
        FROM memories
        WHERE memory LIKE ?
        ORDER BY id DESC
    """, (f"%{keyword}%",))

    memories = cursor.fetchall()

    conn.close()

    return memories


# =========================================================
# DELETE MEMORY
# =========================================================

def delete_memory(memory_id):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM memories
        WHERE id = ?
    """, (memory_id,))

    conn.commit()

    conn.close()


# =========================================================
# CLEAR ALL MEMORIES
# =========================================================

def clear_all_memories():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("DELETE FROM memories")

    conn.commit()

    conn.close()


# =========================================================
# INITIALIZE DATABASE
# =========================================================

init_memory_db()