from werkzeug.security import generate_password_hash
import sqlite3

# Connect to your database
conn = sqlite3.connect('vehicles.db')
cursor = conn.cursor()

# Update the password for the 'admin' user
username = 'admin'
new_password = 'admin123'  # The plain text password you want to hash
hashed_password = generate_password_hash(new_password)

cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (hashed_password, username))
conn.commit()

# Update the password for the 'user' user
username = 'user'
new_password = 'user123'  # The plain text password you want to hash
hashed_password = generate_password_hash(new_password)

cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (hashed_password, username))
conn.commit()

conn.close()