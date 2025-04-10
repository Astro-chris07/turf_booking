from database.db import get_db

def get_user(username, password):
    db = get_db()
    if not db:
        return None
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return user

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
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    db.commit()
    cursor.close()
    db.close()
    return True

def is_admin(user_id):
    db = get_db()
    if not db:
        return False
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT is_admin FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return user and user['is_admin']


