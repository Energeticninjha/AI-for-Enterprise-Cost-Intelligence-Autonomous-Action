import os
import imaplib
from dotenv import load_dotenv

load_dotenv()
IMAP_SERVER = os.getenv("IMAP_SERVER")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

print(f"Reading .env: USER={EMAIL_USER}, SERVER={IMAP_SERVER}")
try:
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    print("Connected to IMAP server successfully.")
    try:
        mail.login(EMAIL_USER, EMAIL_PASS)
        print("Logged in successfully. Connection is ACTIVE.")
        mail.select("inbox")
        status, msgs = mail.search(None, '(UNSEEN SUBJECT "PROCUREMENT_PR")')
        print(f"Connection active, unread PROCUREMENT_PR count: {len(msgs[0].split())}")
    except Exception as e:
        print(f"Auth Failure: {e}")
except Exception as e:
    print(f"Network Error: {e}")
