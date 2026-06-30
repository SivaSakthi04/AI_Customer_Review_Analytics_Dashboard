import sqlite3
import os

# Create database folder if it doesn't exist
os.makedirs("database", exist_ok=True)

conn = sqlite3.connect("database/sentiment.db")
cursor = conn.cursor()

# Admin table
cursor.execute("""
CREATE TABLE IF NOT EXISTS admin(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# Default admin
cursor.execute("""
INSERT OR IGNORE INTO admin(username, password)
VALUES('admin', 'admin123')
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS admin(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")
# Review history table
cursor.execute("""
CREATE TABLE IF NOT EXISTS history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review TEXT NOT NULL,
    sentiment TEXT NOT NULL,
    confidence REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("✅ Database Created Successfully!")