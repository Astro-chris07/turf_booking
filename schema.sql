CREATE DATABASE IF NOT EXISTS turf_booking;
USE turf_booking;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(100),
    is_admin BOOLEAN DEFAULT 0
);

CREATE TABLE turfs (
    turf_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    location VARCHAR(100),
    sport_type VARCHAR(50),
    rate_per_hour DECIMAL(10,2),
    available BOOLEAN DEFAULT 1
);

CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    turf_id INT,
    booking_date DATE,
    start_time TIME,
    end_time TIME,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (turf_id) REFERENCES turfs(turf_id)
);

INSERT INTO turfs (name, location, sport_type, rate_per_hour) VALUES
('Football Field A', 'Downtown', 'Football', 25.00),
('Tennis Court 1', 'West Side', 'Tennis', 15.00),
('Basketball Court B', 'East Arena', 'Basketball', 20.00);
