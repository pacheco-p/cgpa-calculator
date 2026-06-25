import hashlib
import secrets
import streamlit as st
from datetime import datetime, timedelta
from database import get_db_connection

def hash_password(password: str, salt: str) -> str:
    """FIX 1: PBKDF2 hashing utilizing unique per-user cryptographically secure salts."""
    key = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt.encode('utf-8'), 
        100000
    )
    return key.hex()

def register_user(username, password, matric_no, department, level):
    conn = get_db_connection()
    cursor = conn.cursor()
    username_clean = username.strip().lower()
    
    # Check matric number uniqueness
    cursor.execute("SELECT username FROM users WHERE matric_no = ?", (matric_no.upper().strip(),))
    if cursor.fetchone():
        conn.close()
        return False, "❌ This Matric Number is already registered."
        
    # FIX 1: Generate a unique per-user salt
    user_salt = secrets.token_hex(16)
    hashed_p = hash_password(password, user_salt)
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cursor.execute("""
            INSERT INTO users (username, password, salt, matric_no, department, level, date_created)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username_clean, hashed_p, user_salt, matric_no.upper().strip(), department, level, current_date))
        conn.commit()
        return True, username_clean
    except sqlite3.IntegrityError:
        return False, f"❌ Username '{username}' is already taken."
    finally:
        conn.close()

def authenticate_user(username, password):
    """FIX 2: Secure sign-in workflow featuring account lockout logic."""
    conn = get_db_connection()
    cursor = conn.cursor()
    username_clean = username.strip().lower()
    now = datetime.now()
    
    cursor.execute("SELECT password, salt, failed_attempts, locked_until, matric_no, department, level, date_created FROM users WHERE username = ?", (username_clean,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return False, "Invalid credentials."
        
    db_password, db_salt, failed_attempts, locked_until, matric, dept, lvl, created = row
    
    if locked_until:
        lock_time = datetime.strptime(locked_until, "%Y-%m-%d %H:%M:%S")
        if now < lock_time:
            remaining = int((lock_time - now).total_seconds() / 60)
            conn.close()
            return False, f"🔒 Account locked due to brute-force detection. Try again in {remaining + 1} minute(s)."
            
    if db_password == hash_password(password, db_salt):
        # Reset failed tracking upon successful login
        cursor.execute("UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE username = ?", (username_clean,))
        conn.commit()
        conn.close()
        return True, {"username": username_clean, "matric": matric, "dept": dept, "level": lvl, "joined": created}
    else:
        new_attempts = failed_attempts + 1
        lock_str = None
        if new_attempts >= 5:
            # Lock out account for 15 minutes
            lock_str = (now + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
            st.error("⚠️ Threshold reached! This account has been locked for 15 minutes.")
            
        cursor.execute("UPDATE users SET failed_attempts = ?, locked_until = ? WHERE username = ?", (new_attempts, lock_str, username_clean))
        conn.commit()
        conn.close()
        return False, "Invalid credentials."