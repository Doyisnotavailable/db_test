# filepath: sqlite-email-populator/src/check_url.py
import sqlite3
from checker import IPQS, GoogleSafeBrowsing  
from dotenv import load_dotenv
import os
import subprocess
import sys

def main():
    # Populate the database first
    subprocess.run([sys.executable, "populate_db.py"], check=True)

    load_dotenv()  # Load variables from .env

    IPQS_KEY = os.getenv("IPQS_KEY")
    GOOGLE_KEY = os.getenv("GOOGLE_KEY")

    ipqs = IPQS(api_key=IPQS_KEY)
    gsb = GoogleSafeBrowsing(api_key=GOOGLE_KEY)

    conn = sqlite3.connect('emails.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS url_checks (
            url TEXT PRIMARY KEY,
            email_id TEXT,
            is_safe INTEGER,
            ipqs_result INTEGER,
            gsb_result INTEGER,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(email_id) REFERENCES emails(id)
        )
    ''')

    c.execute('SELECT id FROM emails ORDER BY rowid ASC LIMIT 1')
    email_row = c.fetchone()

    if email_row:
        email_id = email_row[0]
        print(f"📧 Scanning email ID: {email_id}")

        c.execute('SELECT url FROM urls WHERE email_id = ?', (email_id,))
        urls = c.fetchall()

        for (url,) in urls:
            c.execute('SELECT url FROM url_checks WHERE url = ?', (url,))
            if c.fetchone():
                print(f"⏩ Already scanned: {url}")
                continue

            print(f"🔍 Checking URL: {url}")
            ipqs_result = int(ipqs.check_url(url))
            gsb_result = int(gsb.check_url(url))
            is_safe = int(ipqs_result and gsb_result)

            c.execute('''
                INSERT OR REPLACE INTO url_checks (url, email_id, is_safe, ipqs_result, gsb_result)
                VALUES (?, ?, ?, ?, ?)
            ''', (url, email_id, is_safe, ipqs_result, gsb_result))
            conn.commit()

        print("✅ Done checking URLs for this email.")
        print("\nResults in url_checks table:")
        for row in c.execute('SELECT * FROM url_checks'):
            print(row)
    else:
        print("⚠️ No emails found in database.")

    conn.close()

if __name__ == "__main__":
    main()