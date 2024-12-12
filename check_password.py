'''import sqlite3

# Connect to your database
conn = sqlite3.connect('vehicles.db')
cursor = conn.cursor()

# Query the user
username = 'admin'  # Change this to the username you are testing
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
user = cursor.fetchone()

if user:
    print(f"User  found: {user}")
else:
    print("User  not found.")

conn.close()'''

import sqlite3

# Connect to your database
conn = sqlite3.connect('vehicles.db')
cursor = conn.cursor()

# Check the schema of the users table
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()

for column in columns:
    print(column)

conn.close()