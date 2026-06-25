import sqlite3

DB_FILE = "pca_platform.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    # FIX 3: Explicitly enforce SQLite Foreign Keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Core User Table with unique per-user salt and lockout telemetry
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            salt TEXT NOT NULL,
            matric_no TEXT UNIQUE,
            department TEXT,
            level TEXT,
            failed_attempts INTEGER DEFAULT 0,
            locked_until TEXT,
            date_created TEXT
        )
    """)
    
    # Aggregated Summary Logs with unique session ID tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            session_id TEXT PRIMARY KEY,
            username TEXT,
            timestamp TEXT,
            department TEXT,
            cgpa REAL,
            units INTEGER,
            FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE
        )
    """)
    
    # Granular Course Ledger linked to a unique session
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS course_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            username TEXT,
            semester_index INTEGER,
            course_code TEXT,
            units INTEGER,
            grade TEXT,
            points REAL,
            FOREIGN KEY(session_id) REFERENCES history(session_id) ON DELETE CASCADE,
            FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()