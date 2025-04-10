from database.db import get_db

# Function to get all turfs from the database
def get_all_turfs():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT turf_id, name, location, rate_per_hour, available FROM turfs")
    results = cursor.fetchall()

    # Convert the results to a list of dictionaries
    turfs = []
    for row in results:
        turf = {
            'id': row[0],
            'name': row[1],
            'location': row[2],
            'rate_per_hour': row[3],
            'available': row[4]
        }
        turfs.append(turf)
    
    return turfs


# Optionally, you can create a Turf class if needed for object representation
class Turf:
    def __init__(self, turf_id, name, location, sport_type):
        self.turf_id = turf_id
        self.name = name
        self.location = location
        self.sport_type = sport_type

    def __repr__(self):
        return f"<Turf {self.name} - {self.sport_type}>"
