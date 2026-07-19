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


# ==================== FORGOT PASSWORD (PASSKEY) ====================
# Simple recovery flow: instead of emailing a one-time code, the admin
# proves ownership by entering a fixed recovery passkey. Anyone who knows
# the passkey can set a new password, so keep it private the same way
# you'd keep a password private.

RESET_PASSKEY = "769833"
RESET_MAX_ATTEMPTS = 5


def verify_reset_passkey(passkey):
    """Check a submitted passkey against the recovery passkey. Tracks failed
    attempts and temporarily locks recovery after too many wrong tries, so
    the 6-digit key can't just be brute-forced. Returns (success, message)."""
    admin_data = load_admin_credentials()

    if admin_data.get('reset_attempts', 0) >= RESET_MAX_ATTEMPTS:
        return False, "Too many incorrect passkey attempts. Please try again later."

    if (passkey or '').strip() != RESET_PASSKEY:
        admin_data['reset_attempts'] = admin_data.get('reset_attempts', 0) + 1
        save_admin_credentials(admin_data)
        return False, "Incorrect passkey."

    admin_data['reset_attempts'] = 0
    save_admin_credentials(admin_data)
    return True, "Passkey verified."


def reset_password_with_passkey(passkey, new_password):
    """Verify the recovery passkey and, if valid, set a new admin password.
    Returns (success, message)."""
    ok, message = verify_reset_passkey(passkey)
    if not ok:
        return False, message

    if len(new_password) < 6:
        return False, "Password must be at least 6 characters"

    admin_data = load_admin_credentials()
    admin_data['password_hash'] = generate_password_hash(new_password)
    admin_data['reset_attempts'] = 0
    admin_data['login_attempts'] = 0
    admin_data['locked'] = False
    save_admin_credentials(admin_data)
    return True, "Password has been reset successfully. You can now log in."
