from flask import Flask, render_template, request, redirect, session, flash, url_for
from models.user import get_user, create_user
from database.db import get_db
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return redirect('/main')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/getstarted')
def get_started():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = get_user(request.form['username'], request.form['password'])
        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            if user['role'] == 'admin':
                return redirect('/admin_dashboard')
            else:
                return redirect('/dashboard')

        flash("Invalid credentials", "error")
        return render_template('login.html')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if create_user(username, password):
            flash("Registration successful, please login", "success")
            return redirect('/login')
        flash("User already exists", "error")
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    db = get_db()
    if not db:
        return "Failed to connect to database."
    
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM turfs WHERE available=1")
        turfs = cursor.fetchall()
    except mysql.connector.Error as err:
        return f"Error executing query: {err}"
    finally:
        cursor.close()
        db.close()

    return render_template('dashboard.html', username=session['username'], turfs=turfs)

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT b.booking_id, b.booking_date, b.start_time, b.end_time, t.turf_name, u.username
            FROM bookings b
            JOIN turfs t ON b.turf_id = t.turf_id
            JOIN users u ON b.user_id = u.user_id
            ORDER BY b.booking_date DESC
        """)
        bookings = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Error fetching bookings: {err}", "error")
        return redirect('/dashboard')
    finally:
        cursor.close()
        db.close()

    return render_template('admin_dashboard.html', bookings=bookings)

@app.route('/bookings')
def bookings():
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT b.booking_id, b.booking_date, b.start_time, b.end_time, t.turf_name
            FROM bookings b
            JOIN turfs t ON b.turf_id = t.turf_id
            WHERE b.user_id = %s
            ORDER BY b.booking_date DESC
        """, (session['user_id'],))
        bookings = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Error fetching bookings: {err}", "error")
        return redirect('/dashboard')
    finally:
        cursor.close()
        db.close()

    return render_template('bookings.html', bookings=bookings)

@app.route('/book', methods=['POST'])
def book():
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    turf_id = request.form.get('turf_id')
    date = request.form.get('date')
    time_slot = request.form.get('time_slot')  # Time slot now combines start and end time (e.g., 06:00-07:00)
    
    if not turf_id or not date or not time_slot:
        flash("Please fill all required fields", "error")
        return redirect('/dashboard')

    start, end = time_slot.split('-')  # Split time slot into start and end times

    # Check if the user has already booked this turf at the same time
    try:
        cursor.execute("""
            SELECT * FROM bookings
            WHERE user_id = %s AND turf_id = %s AND booking_date = %s 
            AND ((start_time BETWEEN %s AND %s) OR (end_time BETWEEN %s AND %s) OR 
            (start_time <= %s AND end_time >= %s))
        """, (session['user_id'], turf_id, date, start, end, start, end, start, end))

        existing_booking = cursor.fetchone()

        if existing_booking:
            flash("The selected slot is already booked. Please try another time slot.", "error")
            return redirect('/dashboard')

        # Insert the new booking if no conflicts found
        cursor.execute("""
            INSERT INTO bookings (user_id, turf_id, booking_date, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            session['user_id'],
            turf_id,
            date,
            start,
            end
        ))
        db.commit()
        flash("Booking successful!", "success")
    except Exception as e:
        db.rollback()
        flash(f"An error occurred: {e}", "error")
    finally:
        cursor.close()
        db.close()

    return redirect('/bookings')


@app.route('/delete_booking', methods=['POST'])
def delete_booking():
    if 'user_id' not in session:
        return redirect('/login')

    booking_id = request.form.get('booking_id')

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT user_id FROM bookings WHERE booking_id = %s", (booking_id,))
        result = cursor.fetchone()

        if result and result[0] == session['user_id']:
            cursor.execute("DELETE FROM bookings WHERE booking_id = %s", (booking_id,))
            db.commit()
            flash("Booking deleted successfully.", "success")
        else:
            flash("Unauthorized or booking not found.", "error")
    except Exception as e:
        db.rollback()
        flash(f"An error occurred: {e}", "error")
    finally:
        cursor.close()
        db.close()

    return redirect('/bookings')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT user_id, username, role FROM users WHERE user_id = %s", (session['user_id'],))
        user = cursor.fetchone()
    except mysql.connector.Error as err:
        flash(f"Error fetching user details: {err}", "error")
        return redirect('/dashboard')
    finally:
        cursor.close()
        db.close()

    return render_template('profile.html', user=user)

@app.route('/manage_turfs')
def manage_turfs():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM turfs")
        turfs = cursor.fetchall()
    except Exception as e:
        flash(f"Failed to load turfs: {e}", "error")
        turfs = []
    finally:
        cursor.close()
        db.close()

    return render_template('manage_turfs.html', turfs=turfs)

@app.route('/add_turf', methods=['POST'])
def add_turf():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')

    turf_name = request.form['turf_name']
    available = int(request.form['available'])

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("INSERT INTO turfs (turf_name, available) VALUES (%s, %s)", (turf_name, available))
        db.commit()
        flash("Turf added successfully", "success")
    except Exception as e:
        db.rollback()
        flash(f"Failed to add turf: {e}", "error")
    finally:
        cursor.close()
        db.close()

    return redirect('/manage_turfs')

@app.route('/delete_turf/<int:turf_id>', methods=['POST'])
def delete_turf(turf_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM turfs WHERE turf_id = %s", (turf_id,))
        db.commit()
        flash("Turf deleted successfully", "success")
    except Exception as e:
        db.rollback()
        flash(f"Failed to delete turf: {e}", "error")
    finally:
        cursor.close()
        db.close()

    return redirect('/manage_turfs')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "success")
    return redirect('/main')

if __name__ == '__main__':
    app.run(debug=True)
