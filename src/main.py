from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os
from dotenv import load_dotenv
from checker import IPQS, GoogleSafeBrowsing

load_dotenv()

IPQS_KEY = os.getenv("IPQS_KEY")
GOOGLE_KEY = os.getenv("GOOGLE_KEY")

ipqs = IPQS(api_key=IPQS_KEY)
gsb = GoogleSafeBrowsing(api_key=GOOGLE_KEY)

app = FastAPI()

class EmailRequest(BaseModel):
    email_id: int

@app.post("/check_email_urls")
def check_email_urls(req: EmailRequest):
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

    c.execute('SELECT id FROM emails WHERE id = ?', (req.email_id,))
    email_row = c.fetchone()

    if not email_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Email not found")

    c.execute('SELECT url FROM urls WHERE email_id = ?', (req.email_id,))
    urls = c.fetchall()
    results = []

    for (url,) in urls:
        c.execute('SELECT url, is_safe, ipqs_result, gsb_result FROM url_checks WHERE url = ?', (url,))
        row = c.fetchone()
        if row:
            result = {
                "url": row[0],
                "is_safe": bool(row[1]),
                "ipqs_result": bool(row[2]),
                "gsb_result": bool(row[3])
            }
        else:
            ipqs_result = int(ipqs.check_url(url))
            gsb_result = int(gsb.check_url(url))
            is_safe = int(ipqs_result and gsb_result)
            c.execute('''
                INSERT OR REPLACE INTO url_checks (url, email_id, is_safe, ipqs_result, gsb_result)
                VALUES (?, ?, ?, ?, ?)
            ''', (url, req.email_id, is_safe, ipqs_result, gsb_result))
            conn.commit()
            result = {
                "url": url,
                "is_safe": bool(is_safe),
                "ipqs_result": bool(ipqs_result),
                "gsb_result": bool(gsb_result)
            }
        results.append(result)

    conn.close()
    # Print results to console logs
    print(f"Checked URLs for email_id={req.email_id}:")
    for res in results:
        print(res)
    return {"email_id": req.email_id, "results": results}