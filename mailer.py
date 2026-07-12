"""
mailer.py — Minimal email sending using Python's stdlib smtplib.

No extra dependency (no Flask-Mail) is required. If SMTP credentials are
not configured via environment variables, send_email() simply logs the
message and returns False instead of raising, so the site keeps working
in local/dev environments without any mail server configured.

Required env vars for real sending:
    MAIL_SERVER   e.g. smtp.gmail.com
    MAIL_PORT     e.g. 587
    MAIL_USERNAME your_email@gmail.com
    MAIL_PASSWORD an app password (NOT your normal password)
    MAIL_SENDER   optional, defaults to MAIL_USERNAME
"""

import os
import smtplib
import ssl
from email.message import EmailMessage


def mail_configured():
    return bool(os.environ.get("MAIL_USERNAME") and os.environ.get("MAIL_PASSWORD"))


def send_email(to_address, subject, body):
    if not mail_configured():
        print(f"[mailer] SMTP not configured — skipping real send. "
              f"Would have emailed '{subject}' to {to_address}.")
        return False

    server = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    port = int(os.environ.get("MAIL_PORT", "587"))
    username = os.environ["MAIL_USERNAME"]
    password = os.environ["MAIL_PASSWORD"]
    sender = os.environ.get("MAIL_SENDER", username)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_address
    msg.set_content(body)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(server, port, timeout=10) as smtp:
            smtp.starttls(context=context)
            smtp.login(username, password)
            smtp.send_message(msg)
        return True
    except Exception as exc:
        print(f"[mailer] Failed to send email: {exc}")
        return False
