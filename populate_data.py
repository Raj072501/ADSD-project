'''import sqlite3
import random
import os

# Connect to the SQLite database
sqlite_connection = sqlite3.connect('vehicles.db')
cursor = sqlite_connection.cursor()

# Create a new table with the desired structure
cursor.execute(
    "CREATE TABLE IF NOT EXISTS vehicles_new (id INTEGER PRIMARY KEY, name TEXT, category TEXT, make TEXT, model TEXT, year INTEGER, engine_type TEXT, origin TEXT, image_file_path TEXT)"
)

# Copy the data from the old table to the new table
cursor.execute("SELECT * FROM vehicles")
rows = cursor.fetchall()
for row in rows:
    cursor.execute(
        "INSERT INTO vehicles_new (name, category, make, model, year, engine_type, origin) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (row[1], row[2], row[3], row[4], row[5], row[6], row[7])
    )

# Drop the old table
cursor.execute("DROP TABLE vehicles")

# Rename the new table to the old table name
cursor.execute("ALTER TABLE vehicles_new RENAME TO vehicles")

# Commit the changes and close the connection
sqlite_connection.commit()
sqlite_connection.close()

# Now you can run your original code to populate the data
'''

import sqlite3
import random
import os

# Connect to the SQLite database
sqlite_connection = sqlite3.connect('vehicles.db')
cursor = sqlite_connection.cursor()

# Sample data for vehicles
categories = ['Car', 'Truck', 'Bike']
makes = ['Toyota', 'Ford', 'Honda', 'Chevrolet', 'BMW', 'Kawasaki', 'Harley-Davidson', 'Ducati']
models = ['Model A', 'Model B', 'Model C', 'Model D', 'Model E']
engine_types = ['Petrol', 'Diesel', 'Electric', 'Hybrid']
origins = ['USA', 'Japan', 'Germany', 'Italy', 'India']

# Path to the images directory
images_dir = "static/images"

# Function to generate random vehicle data
def generate_random_vehicle_data(num_entries):
    # Get a list of all image files in the images directory
    if not os.path.exists(images_dir):
        print(f"Error: The directory '{images_dir}' does not exist.")
        return
    
    image_files = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))]

    if not image_files:
        print(f"Error: No image files found in the directory '{images_dir}'.")
        return
    
    for _ in range(num_entries):
        category = random.choice(categories)
        make = random.choice(makes)
        model = random.choice(models)
        year = random.randint(2000, 2023)  # Random year between 2000 and 2023
        engine_type = random.choice(engine_types)
        origin = random.choice(origins)
        
        # Generate a name for the vehicle
        car_name = f"{make} {model} ({year})"

        # Select a random image file from the list
        image_file_path = random.choice(image_files)

        # Insert the random vehicle data into the database
        cursor.execute(
            "INSERT INTO vehicles (car_name, category, make, model, year, engine_type, origin, image_file_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
            (car_name, category, make, model, year, engine_type, origin, image_file_path)
        )

# Generate random data
generate_random_vehicle_data(6)  # Change the number to generate more or fewer entries

# Commit the changes and close the connection
sqlite_connection.commit()
sqlite_connection.close()

print("Random vehicle data added successfully!")
