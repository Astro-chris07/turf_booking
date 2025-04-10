from database.db import get_db

# --- USER QUERIES ---
def authenticate_user(username, password):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )
    return cursor.fetchone()

def create_user(username, password, is_admin=False):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)",
        (username, password, is_admin)
    )
    db.commit()
    return cursor.lastrowid

# --- TURF QUERIES ---
def get_available_turfs(sport_type=None):
    db = get_db()
    cursor = db.cursor()
    if sport_type:
        cursor.execute(
            "SELECT * FROM turfs WHERE available = 1 AND sport_type = %s",
            (sport_type,)
        )
    else:
        cursor.execute("SELECT * FROM turfs WHERE available = 1")
    return cursor.fetchall()

# --- BOOKING QUERIES ---
def create_booking(user_id, turf_id, date, start_time, end_time, cost):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO bookings (user_id, turf_id, booking_date, start_time, end_time, cost)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, turf_id, date, start_time, end_time, cost))
    db.commit()
    return cursor.lastrowid

def get_all_bookings():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT b.booking_id, u.username, t.name as turf_name, b.booking_date,
               b.start_time, b.end_time, b.cost
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN turfs t ON b.turf_id = t.turf_id
    """)
    return cursor.fetchall()
