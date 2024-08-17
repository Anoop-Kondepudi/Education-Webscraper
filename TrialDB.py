import sqlite3

# Connect to the database
db = sqlite3.connect('trialUsers.db')
cursor = db.cursor()

# Fetch and display data
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

for row in rows:
    print(f"User ID: {row[0]}")

# Close the connection
db.close()
