"""
admin_auth.py - Secure admin authentication module
Handles admin login, session management, and password hashing
"""

from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import session, redirect, url_for, request
import os
import secrets
import json
from datetime import datetime, timedelta

# Admin credentials file (absolute path, same pattern as db.py, so it always
# resolves to the project's data/ folder no matter what the current working
# directory is when Flask/Gunicorn starts the app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ADMIN_FILE = os.path.join(DATA_DIR, 'admin_credentials.json')

def init_admin_credentials(admin_email="admin@portfolio.com", admin_password=None):
    """Initialize admin credentials — but ONLY if they don't already exist.
    Safe to call on every app startup: it will never overwrite an existing
    password (that would lock you out on every restart)."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(ADMIN_FILE):
        # Already set up — do nothing so we never clobber an existing password.
        with open(ADMIN_FILE, 'r') as f:
            existing = json.load(f)
        return existing.get('email'), None

    if admin_password is None:
        # Generate a strong password if not provided
        admin_password = generate_strong_password()
    
    admin_data = {
        "email": admin_email,
        "password_hash": generate_password_hash(admin_password),
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "login_attempts": 0,
        "locked": False
    }
    
    with open(ADMIN_FILE, 'w') as f:
        json.dump(admin_data, f, indent=4)
    
    return admin_email, admin_password

def generate_strong_password(length=12):
    """Generate a strong random password"""
    # Ensure strong password with uppercase, lowercase, digits, and special chars
    import string
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*-_=+"
    return ''.join(secrets.choice(alphabet) for i in range(length))

def load_admin_credentials():
    """Load admin credentials from file"""
    if not os.path.exists(ADMIN_FILE):
        init_admin_credentials()
    
    with open(ADMIN_FILE, 'r') as f:
        return json.load(f)

def save_admin_credentials(admin_data):
    """Save admin credentials to file"""
    with open(ADMIN_FILE, 'w') as f:
        json.dump(admin_data, f, indent=4)

def verify_admin_password(email, password):
    """Verify admin email and password"""
    admin_data = load_admin_credentials()
    
    # Check if account is locked
    if admin_data.get('locked', False):
        return False, "Admin account is locked. Too many failed attempts."
    
    # Check email and password
    if admin_data['email'] == email and check_password_hash(admin_data['password_hash'], password):
        # Reset login attempts on successful login
        admin_data['login_attempts'] = 0
        admin_data['last_login'] = datetime.now().isoformat()
        save_admin_credentials(admin_data)
        return True, "Login successful"
    else:
        # Increment failed attempts
        admin_data['login_attempts'] = admin_data.get('login_attempts', 0) + 1
        if admin_data['login_attempts'] >= 5:
            admin_data['locked'] = True
        save_admin_credentials(admin_data)
        return False, "Invalid email or password"

def change_admin_password(old_password, new_password):
    """Change admin password"""
    admin_data = load_admin_credentials()
    
    if not check_password_hash(admin_data['password_hash'], old_password):
        return False, "Current password is incorrect"
    
    admin_data['password_hash'] = generate_password_hash(new_password)
    save_admin_credentials(admin_data)
    return True, "Password changed successfully"

def login_required(f):
    """Decorator to protect admin routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_admin_email():
    """Get current admin email from credentials"""
    admin_data = load_admin_credentials()
    return admin_data.get('email')


# ==================== FORGOT PASSWORD (EMAIL OTP) ====================

OTP_VALID_MINUTES = 10
OTP_MAX_ATTEMPTS = 5


def request_password_reset(email):
    """Generate a 6-digit OTP, store it (hashed) with an expiry, and email it
    to the admin's registered address. Returns (success, message).
    Always returns a generic success-shaped message even if the email doesn't
    match, so this endpoint can't be used to probe/confirm the admin email."""
    admin_data = load_admin_credentials()

    otp = f"{secrets.randbelow(1_000_000):06d}"

    if admin_data.get('email') == email:
        admin_data['reset_otp_hash'] = generate_password_hash(otp)
        admin_data['reset_otp_expires'] = (datetime.now() + timedelta(minutes=OTP_VALID_MINUTES)).isoformat()
        admin_data['reset_otp_attempts'] = 0
        save_admin_credentials(admin_data)

        import mailer
        mailer.send_email(
            email,
            "Your portfolio admin password reset code",
            f"Your one-time code is: {otp}\n\n"
            f"This code expires in {OTP_VALID_MINUTES} minutes. "
            f"If you didn't request this, you can safely ignore this email."
        )

    # Same message regardless of whether the email matched (avoids leaking
    # whether an account/email exists).
    return True, "If that email is registered, a reset code has been sent."


def verify_reset_otp_and_set_password(email, otp, new_password):
    """Verify the OTP and, if valid, set a new password. Returns (success, message)."""
    admin_data = load_admin_credentials()

    if admin_data.get('email') != email:
        return False, "Invalid email or code"

    otp_hash = admin_data.get('reset_otp_hash')
    expires_at = admin_data.get('reset_otp_expires')

    if not otp_hash or not expires_at:
        return False, "No reset code was requested. Please request a new one."

    if datetime.now() > datetime.fromisoformat(expires_at):
        return False, "This code has expired. Please request a new one."

    if admin_data.get('reset_otp_attempts', 0) >= OTP_MAX_ATTEMPTS:
        return False, "Too many incorrect attempts. Please request a new code."

    if not check_password_hash(otp_hash, otp):
        admin_data['reset_otp_attempts'] = admin_data.get('reset_otp_attempts', 0) + 1
        save_admin_credentials(admin_data)
        return False, "Invalid or expired code"

    if len(new_password) < 6:
        return False, "Password must be at least 6 characters"

    # Success: set new password, clear the OTP, and unlock the account
    # (a successful reset is proof of email ownership).
    admin_data['password_hash'] = generate_password_hash(new_password)
    admin_data.pop('reset_otp_hash', None)
    admin_data.pop('reset_otp_expires', None)
    admin_data['reset_otp_attempts'] = 0
    admin_data['login_attempts'] = 0
    admin_data['locked'] = False
    save_admin_credentials(admin_data)
    return True, "Password has been reset successfully. You can now log in."
