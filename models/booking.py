from database.db import get_db
from datetime import datetime

class Booking:
    def __init__(self, id, user_id, turf_id, booking_date, start_time, end_time, total_cost):
        self.id = id
        self.user_id = user_id
        self.turf_id = turf_id
        self.booking_date = booking_date
        self.start_time = start_time
        self.end_time = end_time
        self.total_cost = total_cost

    def __repr__(self):
        return f"<Booking {self.id} by User {self.user_id} for Turf {self.turf_id}>"

def create_booking(user_id, turf_id, booking_date, start_time, end_time):
    db = get_db()
    cursor = db.cursor()

    # Get hourly_rate from the turfs table
    cursor.execute("SELECT hourly_rate FROM turfs WHERE turf_id = %s", (turf_id,))
    result = cursor.fetchone()
    if not result:
        return False  # Turf not found

    hourly_rate = float(result[0])

    # Calculate duration and total cost
    fmt = "%H:%M"
    start = datetime.strptime(str(start_time), fmt)
    end = datetime.strptime(str(end_time), fmt)
    hours = (end - start).seconds / 3600  # convert to float hours
    total_cost = round(hours * hourly_rate, 2)

    # Insert booking into the database
    query = """
        INSERT INTO bookings (user_id, turf_id, booking_date, start_time, end_time, total_cost)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (user_id, turf_id, booking_date, start_time, end_time, total_cost))
    db.commit()
    return True

def get_user_bookings(user_id):
    db = get_db()
    cursor = db.cursor()
    query = """
        SELECT b.*, t.name AS turf_name, t.location, t.sport_type
        FROM bookings b
        JOIN turfs t ON b.turf_id = t.turf_id
        WHERE b.user_id = %s
        ORDER BY b.booking_date DESC
    """
    cursor.execute(query, (user_id,))
    return cursor.fetchall()
