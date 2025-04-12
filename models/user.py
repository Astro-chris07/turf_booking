from database.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash

def get_user(username, password):
    db = get_db()
    if not db:
        return None
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user and check_password_hash(user['password'], password):
        return user
    return None

def create_user(username, password):
    db = get_db()
    if not db:
        return False
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        cursor.close()
        db.close()
        return False  # User already exists

    hashed_password = generate_password_hash(password)
    cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, hashed_password, 'user'))
    db.commit()
    cursor.close()
    db.close()
    return True

def is_admin(user_id):
    db = get_db()
    if not db:
        return False
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT role FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return user and user['role'] == 'admin'
