import sqlite3
from faker import Faker
import re

# Initialize Faker to generate fake data
fake = Faker()

# Create a new SQLite database (or connect to it if it exists)
conn = sqlite3.connect('emails.db')
c = conn.cursor()

# Add a message column to the emails table
c.execute('''
    CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        message TEXT
    )
''')

# Create a urls table to store URLs per email
c.execute('''
    CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id INTEGER,
        url TEXT,
        FOREIGN KEY(email_id) REFERENCES emails(id)
    )
''')

def generate_message_with_links():
    # Generate a message with 1-3 fake URLs
    num_links = fake.random_int(min=1, max=1)
    links = [fake.url() for _ in range(num_links)]
    message = fake.paragraph(nb_sentences=3)
    # Insert links into the message
    for link in links:
        message += f" Please visit {link}."
    return message, links

# Populate the emails table with fake email entries
for _ in range(5):  # Generate 100 fake email entries
    email = fake.email()
    message, links = generate_message_with_links()
    try:
        c.execute('INSERT INTO emails (email, message) VALUES (?, ?)', (email, message))
        email_id = c.lastrowid
        print(f"Email: {email}\nMessage: {message}\n")
        # Insert URLs into urls table
        for url in links:
            c.execute('INSERT INTO urls (email_id, url) VALUES (?, ?)', (email_id, url))
    except sqlite3.IntegrityError:
        # If the email already exists, skip it
        continue

# Commit the changes and close the connection
conn.commit()
conn.close()