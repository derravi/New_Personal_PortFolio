# 🎛️ Admin Dashboard Setup Guide

This comprehensive guide will help you integrate the admin dashboard into your Flask portfolio application.

## 📋 Overview

The admin dashboard provides:
- ✅ Secure admin login with password hashing
- ✅ Complete project management (Add, Edit, Delete)
- ✅ Dashboard with statistics and activity logs
- ✅ Project search, filtering, and sorting
- ✅ Settings management and password change
- ✅ Data export/import functionality
- ✅ Mobile-responsive design

## 📦 File Structure

```
Admin Panel Files:
├── admin_auth.py              # Authentication module
├── admin_db.py                # Database management
├── admin_routes.py            # Flask blueprint with routes
├── templates/
│   ├── admin_login.html       # Login page
│   ├── admin_dashboard.html   # Dashboard home
│   ├── admin_projects.html    # Projects list
│   ├── admin_project_form.html # Add/Edit project
│   └── admin_settings.html    # Settings & backup
└── ADMIN_SETUP_GUIDE.md       # This file
```

## 🚀 Installation Steps

### Step 1: Copy Admin Files to Your Project

1. Copy all admin Python files to your project root:
   - `admin_auth.py`
   - `admin_db.py`
   - `admin_routes.py`

2. Copy all template files to your `templates/` folder:
   - `admin_login.html`
   - `admin_dashboard.html`
   - `admin_projects.html`
   - `admin_project_form.html`
   - `admin_settings.html`

### Step 2: Update Flask Application

Edit your main `flask_app.py`:

```python
# At the top with other imports
from admin_routes import admin_bp
from admin_db import init_admin_tables
from admin_auth import init_admin_credentials

# After creating Flask app instance (around line 60)
app = Flask(__name__)

# Set session configuration (required for admin panel)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7  # 7 days

# Initialize admin tables
init_admin_tables()

# Register admin blueprint
app.register_blueprint(admin_bp)

# Initialize admin credentials if they don't exist
try:
    init_admin_credentials()
except:
    pass  # Already initialized
```

### Step 3: Generate Admin Credentials

When you first run the application, the admin credentials will be automatically generated. You can find them in:
- `data/admin_credentials.json`

**Important:** The first time you access `/admin/login`, a strong password will be generated for you.

To view or customize:
```python
# In Python shell or script:
from admin_auth import init_admin_credentials, load_admin_credentials

# Generate new credentials
email, password = init_admin_credentials("your-email@example.com", "your-password-here")
print(f"Admin Email: {email}")
print(f"Admin Password: {password}")

# View current credentials
creds = load_admin_credentials()
print(f"Admin Email: {creds['email']}")
```

### Step 4: Environment Variables (Recommended)

Add to your `.env` file:
```
SECRET_KEY=your-super-secret-key-change-this
FLASK_ENV=production
SESSION_TIMEOUT=604800  # 7 days in seconds
```

### Step 5: Restart Flask Application

```bash
python flask_app.py
```

or with Gunicorn:
```bash
gunicorn -w 4 flask_app:app
```

## 🔑 Admin Panel Access

Once set up, access the admin panel at:
```
https://yourdomain.com/admin/login
```

### Default Login

Email: `admin@portfolio.com`
Password: Check `data/admin_credentials.json` file

## 📖 Usage Guide

### Dashboard
- View overall statistics (total projects, published count, featured, views)
- See recent projects and activity log
- Quick access to create new project

### Manage Projects
- List all projects with filtering (All/Published/Draft/Archived)
- Search projects by title, tags, or description
- Sort by date, title, or view count
- Edit any project's details
- Delete projects with confirmation

### Add New Project
1. Click "New Project" button
2. Fill in basic information (title, slug, category)
3. Add description and links
4. Upload image URL and add tags
5. Set status and featured flag
6. Click "Create Project"

### Edit Project
1. Go to Projects list
2. Click "Edit" on any project
3. Modify any field
4. Click "Update Project"

### Settings
- Change admin password
- View account information
- Export all projects as JSON (for backup)
- Import projects from JSON (for migration)

## 🔒 Security Features

1. **Password Hashing**: Passwords are hashed using Werkzeug's security module
2. **Session Management**: Secure session handling with configurable timeout
3. **Login Attempts**: Account locks after 5 failed login attempts
4. **HTTPS**: Always use HTTPS in production
5. **Environment Variables**: Keep SECRET_KEY in environment, not in code

## 🛠️ Customization

### Change Admin Email

```python
from admin_auth import init_admin_credentials

init_admin_credentials("new-email@example.com", "new-password")
```

### Add More Project Categories

Edit the select options in `admin_project_form.html` line ~140:
```html
<select id="category" name="category" required>
    <option value="">Select a category...</option>
    <option value="ai-ml">AI & Machine Learning</option>
    <option value="web-dev">Web Development</option>
    <!-- Add your custom categories here -->
    <option value="custom-category">Custom Category</option>
</select>
```

### Customize Colors

Edit the CSS in templates to match your brand:
```css
/* Primary gradient color */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Change to your colors */
background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
```

## 🐛 Troubleshooting

### "Session timeout" errors
- Increase `PERMANENT_SESSION_LIFETIME` in flask_app.py
- Ensure `SECRET_KEY` is set in environment variables

### Database errors
- Check that `data/` directory exists and is writable
- Run `init_admin_tables()` again to recreate tables

### Login not working
- Verify credentials in `data/admin_credentials.json`
- Check if account is locked (5+ failed attempts)
- Clear browser cookies and try again

### CSS/JavaScript not loading
- Ensure static files path is correct in Flask configuration
- Clear browser cache
- Restart Flask application

## 📱 Mobile Optimization

The admin panel is fully responsive:
- **Desktop**: Full sidebar navigation with grid layouts
- **Tablet**: Optimized grid with mobile-friendly controls
- **Mobile**: Collapsible sidebar and single-column layouts

## 🔄 Database Schema

### admin_projects table
```
id              INTEGER PRIMARY KEY
slug            TEXT UNIQUE NOT NULL
title           TEXT NOT NULL
description     TEXT
category        TEXT
tags            TEXT (JSON format)
github_url      TEXT
image_url       TEXT
demo_url        TEXT
status          TEXT (published/draft/archived)
featured        BOOLEAN
view_count      INTEGER
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

### admin_activity_log table
```
id              INTEGER PRIMARY KEY
action          TEXT
project_id      INTEGER
details         TEXT
timestamp       TIMESTAMP
```

### admin_credentials.json file
```json
{
    "email": "admin@portfolio.com",
    "password_hash": "werkzeug-hashed-password",
    "created_at": "ISO timestamp",
    "last_login": "ISO timestamp",
    "login_attempts": 0,
    "locked": false
}
```

## 🚀 Deployment Checklist

- [ ] Set `SECRET_KEY` environment variable
- [ ] Set `FLASK_ENV=production`
- [ ] Use HTTPS only
- [ ] Configure session timeout
- [ ] Backup database regularly
- [ ] Set up database backups
- [ ] Configure email for notifications (optional)
- [ ] Monitor admin access logs
- [ ] Keep admin credentials secure
- [ ] Update password regularly

## 📝 API Endpoints

All endpoints require admin authentication.

### Projects
- `GET /admin/api/projects` - Get all projects
- `POST /admin/api/project` - Create project
- `PUT /admin/api/project/<id>` - Update project
- `DELETE /admin/api/project/<id>` - Delete project

### Settings
- `POST /admin/api/change-password` - Change admin password

### Data
- `GET /admin/api/export-projects` - Export all projects
- `POST /admin/api/import-projects` - Import projects

### Analytics
- `GET /admin/api/stats` - Get dashboard statistics
- `GET /admin/api/activities` - Get activity log

## 🎓 Advanced Features

### Custom Validators
You can add custom validation in `admin_routes.py`:
```python
@admin_bp.route('/api/project', methods=['POST'])
@login_required
def api_create_project():
    # Add custom validation here
    if not is_valid_project(data):
        return jsonify({'success': False, 'message': 'Invalid data'}), 400
```

### Email Notifications
Extend `admin_routes.py` to send email notifications when projects are created:
```python
from mailer import send_email
# Send notification when project is created
```

### Advanced Analytics
Add more analytics endpoints to track user behavior:
```python
@admin_bp.route('/api/analytics/views')
@login_required
def api_analytics_views():
    # Return view statistics
```

## 📞 Support & Contributions

For issues or improvements, check:
- Browser console for JavaScript errors
- Flask logs for backend errors
- Database logs for SQL issues

## 📄 License

This admin panel is part of your portfolio project.

---

**Last Updated**: 2024
**Version**: 1.0
