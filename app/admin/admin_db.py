"""
admin_db.py - Admin database module for managing portfolio projects
Handles CRUD operations for projects with SQLite
"""

import sqlite3
import json
from datetime import datetime, timezone
import os
from app.core import db  # shared SITE_REVIEW_SLUG constant

# Absolute path (same project data/ folder used by db.py), so this works no
# matter what directory the app is started from (local run, Docker, Gunicorn...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'portfolio.db')

def get_db_connection():
    """Get database connection"""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_admin_tables():
    """Initialize admin-related database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create admin projects table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            tags TEXT,
            github_url TEXT,
            image_url TEXT,
            demo_url TEXT,
            status TEXT DEFAULT 'published',
            featured BOOLEAN DEFAULT 0,
            view_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create admin activity log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            project_id INTEGER,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # blog_posts table already exists (created by db.py's schema). Add the
    # admin-facing columns it doesn't have yet so drafts/edits work here too.
    cursor.execute("PRAGMA table_info(blog_posts)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    if 'status' not in existing_columns:
        cursor.execute("ALTER TABLE blog_posts ADD COLUMN status TEXT DEFAULT 'published'")
    if 'updated_at' not in existing_columns:
        cursor.execute("ALTER TABLE blog_posts ADD COLUMN updated_at TIMESTAMP")

    # Add order column to admin_projects table if it doesn't exist
    cursor.execute("PRAGMA table_info(admin_projects)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    if 'display_order' not in existing_columns:
        cursor.execute("ALTER TABLE admin_projects ADD COLUMN display_order INTEGER DEFAULT 0")

    # Create admin learning table if it doesn't exist (My Learning cards,
    # managed the same way projects are: add/edit/delete/reorder from /admin)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_learning (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            full_text TEXT,
            category TEXT,
            tags TEXT,
            image_url TEXT,
            link_url TEXT,
            link_type TEXT DEFAULT 'linkedin',
            status TEXT DEFAULT 'published',
            featured BOOLEAN DEFAULT 0,
            view_count INTEGER DEFAULT 0,
            display_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create admin achievements table if it doesn't exist (Achievements &
    # Certifications cards, managed the same way projects/learning are)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            issuer TEXT,
            description TEXT,
            category TEXT,
            achievement_type TEXT,
            icon TEXT DEFAULT 'fas fa-trophy',
            date_label TEXT,
            skills TEXT,
            certificate_url TEXT,
            status TEXT DEFAULT 'published',
            featured BOOLEAN DEFAULT 0,
            view_count INTEGER DEFAULT 0,
            display_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add review moderation columns to project_reviews table if they don't exist
    cursor.execute("PRAGMA table_info(project_reviews)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    if 'status' not in existing_columns:
        cursor.execute("ALTER TABLE project_reviews ADD COLUMN status TEXT DEFAULT 'pending'")
    if 'reviewed_at' not in existing_columns:
        cursor.execute("ALTER TABLE project_reviews ADD COLUMN reviewed_at TEXT")
    if 'reviewed_by' not in existing_columns:
        cursor.execute("ALTER TABLE project_reviews ADD COLUMN reviewed_by TEXT")

    conn.commit()
    conn.close()


# ==================== BLOG POST MANAGEMENT ====================
# Same table (`blog_posts`) the public /blog pages read from - managed here
# so post creation/editing goes through the admin dashboard instead of the
# old standalone token-protected /blog/new form.

def _row_to_blog_post(row):
    post = dict(row)
    tags = post.get('tags') or ''
    post['tags'] = [t.strip() for t in tags.split(',') if t.strip()]
    post['status'] = post.get('status') or 'published'
    return post


def get_all_blog_posts(status='all'):
    """Get all blog posts (optionally filtered by status)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    if status == 'all':
        cursor.execute('SELECT * FROM blog_posts ORDER BY published_at DESC')
    else:
        cursor.execute('SELECT * FROM blog_posts WHERE status = ? ORDER BY published_at DESC', (status,))

    posts = [_row_to_blog_post(row) for row in cursor.fetchall()]
    conn.close()
    return posts


def get_blog_post_by_id(post_id):
    """Get a specific blog post by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM blog_posts WHERE id = ?', (post_id,))
    row = cursor.fetchone()
    conn.close()
    return _row_to_blog_post(row) if row else None


def get_blog_post_by_slug(slug):
    """Get a specific blog post by slug"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM blog_posts WHERE slug = ?', (slug,))
    row = cursor.fetchone()
    conn.close()
    return _row_to_blog_post(row) if row else None


def create_blog_post(slug, title, summary, content, cover_image='', tags=None,
                      status='published', author='Ravi Der'):
    """Create a new blog post"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        tags_str = ','.join(tags) if isinstance(tags, list) else (tags or '')
        now = datetime.now(timezone.utc).isoformat()

        cursor.execute('''
            INSERT INTO blog_posts
                (slug, title, summary, content, cover_image, tags, author, published_at, views, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
        ''', (slug, title, summary, content, cover_image, tags_str, author, now, status, now))

        conn.commit()
        post_id = cursor.lastrowid
        log_activity('CREATE', post_id, f'Created blog post: {title}')

        conn.close()
        return True, "Blog post created successfully", post_id
    except sqlite3.IntegrityError:
        conn.close()
        return False, "A post with this slug already exists", None
    except Exception as e:
        conn.close()
        return False, f"Error creating blog post: {str(e)}", None


def update_blog_post(post_id, slug, title, summary, content, cover_image='', tags=None,
                      status='published'):
    """Update an existing blog post"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        tags_str = ','.join(tags) if isinstance(tags, list) else (tags or '')
        now = datetime.now(timezone.utc).isoformat()

        cursor.execute('''
            UPDATE blog_posts
            SET slug = ?, title = ?, summary = ?, content = ?, cover_image = ?,
                tags = ?, status = ?, updated_at = ?
            WHERE id = ?
        ''', (slug, title, summary, content, cover_image, tags_str, status, now, post_id))

        conn.commit()
        log_activity('UPDATE', post_id, f'Updated blog post: {title}')

        conn.close()
        return True, "Blog post updated successfully"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "A post with this slug already exists"
    except Exception as e:
        conn.close()
        return False, f"Error updating blog post: {str(e)}"


def delete_blog_post(post_id):
    """Delete a blog post"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT title FROM blog_posts WHERE id = ?', (post_id,))
        row = cursor.fetchone()
        post_title = row['title'] if row else 'Unknown'

        cursor.execute('DELETE FROM blog_posts WHERE id = ?', (post_id,))
        conn.commit()
        log_activity('DELETE', post_id, f'Deleted blog post: {post_title}')

        conn.close()
        return True, "Blog post deleted successfully"
    except Exception as e:
        conn.close()
        return False, f"Error deleting blog post: {str(e)}"


def get_blog_stats():
    """Get blog statistics for the dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()

    stats = {}
    cursor.execute('SELECT COUNT(*) as count FROM blog_posts')
    stats['total_posts'] = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM blog_posts WHERE status = 'published' OR status IS NULL")
    stats['published_posts'] = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM blog_posts WHERE status = 'draft'")
    stats['draft_posts'] = cursor.fetchone()['count']

    cursor.execute('SELECT SUM(views) as total FROM blog_posts')
    stats['total_views'] = cursor.fetchone()['total'] or 0

    conn.close()
    return stats


def search_blog_posts(query):
    """Search blog posts by title, summary, content, or tags"""
    conn = get_db_connection()
    cursor = conn.cursor()

    search_term = f"%{query}%"
    cursor.execute('''
        SELECT * FROM blog_posts
        WHERE title LIKE ? OR summary LIKE ? OR content LIKE ? OR tags LIKE ?
        ORDER BY published_at DESC
    ''', (search_term, search_term, search_term, search_term))

    posts = [_row_to_blog_post(row) for row in cursor.fetchall()]
    conn.close()
    return posts

def get_all_projects(status='all'):
    """Get all projects from admin database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if status == 'all':
        cursor.execute('SELECT * FROM admin_projects ORDER BY display_order ASC, created_at DESC')
    else:
        cursor.execute('SELECT * FROM admin_projects WHERE status = ? ORDER BY display_order ASC, created_at DESC', (status,))
    
    projects = [dict(row) for row in cursor.fetchall()]
    
    # Parse tags from JSON
    for project in projects:
        if project['tags']:
            try:
                project['tags'] = json.loads(project['tags'])
            except:
                project['tags'] = []
    
    conn.close()
    return projects

def get_project_by_slug(slug):
    """Get a specific project by slug"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM admin_projects WHERE slug = ?', (slug,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        project = dict(row)
        if project['tags']:
            try:
                project['tags'] = json.loads(project['tags'])
            except:
                project['tags'] = []
        return project
    return None

def get_project_by_id(project_id):
    """Get a specific project by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM admin_projects WHERE id = ?', (project_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        project = dict(row)
        if project['tags']:
            try:
                project['tags'] = json.loads(project['tags'])
            except:
                project['tags'] = []
        return project
    return None

def create_project(slug, title, description, category, tags, github_url, image_url, demo_url='', status='published', featured=False):
    """Create a new project"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Convert tags to JSON string
        tags_json = json.dumps(tags) if isinstance(tags, list) else tags
        
        cursor.execute('''
            INSERT INTO admin_projects (slug, title, description, category, tags, github_url, image_url, demo_url, status, featured)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (slug, title, description, category, tags_json, github_url, image_url, demo_url, status, featured))
        
        conn.commit()
        project_id = cursor.lastrowid
        
        # Log activity
        log_activity('CREATE', project_id, f'Created project: {title}')
        
        conn.close()
        return True, "Project created successfully", project_id
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Project with this slug already exists", None
    except Exception as e:
        conn.close()
        return False, f"Error creating project: {str(e)}", None

def update_project(project_id, slug, title, description, category, tags, github_url, image_url, demo_url='', status='published', featured=False):
    """Update an existing project"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Convert tags to JSON string
        tags_json = json.dumps(tags) if isinstance(tags, list) else tags
        
        cursor.execute('''
            UPDATE admin_projects 
            SET slug = ?, title = ?, description = ?, category = ?, tags = ?, 
                github_url = ?, image_url = ?, demo_url = ?, status = ?, featured = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (slug, title, description, category, tags_json, github_url, image_url, demo_url, status, featured, project_id))
        
        conn.commit()
        
        # Log activity
        log_activity('UPDATE', project_id, f'Updated project: {title}')
        
        conn.close()
        return True, "Project updated successfully"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "A project with this slug already exists"
    except Exception as e:
        conn.close()
        return False, f"Error updating project: {str(e)}"

def delete_project(project_id):
    """Delete a project"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get project info for logging
        cursor.execute('SELECT title FROM admin_projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        project_title = row['title'] if row else 'Unknown'
        
        cursor.execute('DELETE FROM admin_projects WHERE id = ?', (project_id,))
        conn.commit()
        
        # Log activity
        log_activity('DELETE', project_id, f'Deleted project: {project_title}')
        
        conn.close()
        return True, "Project deleted successfully"
    except Exception as e:
        conn.close()
        return False, f"Error deleting project: {str(e)}"

def reorder_projects(order_list):
    """Update project display order
    order_list: list of dicts with 'id' and 'position' keys
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for item in order_list:
            project_id = item.get('id')
            position = item.get('position', 0)
            cursor.execute(
                'UPDATE admin_projects SET display_order = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (position, project_id)
            )
        conn.commit()
        
        # Log activity
        log_activity('REORDER', None, f'Reordered {len(order_list)} projects')
        
        conn.close()
        return True, "Project order updated successfully"
    except Exception as e:
        conn.close()
        return False, f"Error updating project order: {str(e)}"


def bulk_update_status(project_ids, status):
    """Bulk update status (publish/draft/archive) for multiple projects at once.
    project_ids: list of int project IDs
    status: one of 'published', 'draft', 'archived'
    """
    if not project_ids:
        return False, "No projects selected", 0

    valid_statuses = {'published', 'draft', 'archived'}
    if status not in valid_statuses:
        return False, f"Invalid status: {status}", 0

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        placeholders = ','.join('?' for _ in project_ids)
        cursor.execute(
            f'UPDATE admin_projects SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id IN ({placeholders})',
            (status, *project_ids)
        )
        conn.commit()
        affected = cursor.rowcount

        # Log activity
        log_activity('BULK_STATUS_UPDATE', None,
                      f'Updated status to "{status}" for {affected} project(s): {project_ids}')

        conn.close()
        return True, f"{affected} project(s) updated to {status}", affected
    except Exception as e:
        conn.close()
        return False, f"Error updating projects: {str(e)}", 0


def bulk_delete_projects(project_ids):
    """Bulk delete multiple projects at once.
    project_ids: list of int project IDs
    """
    if not project_ids:
        return False, "No projects selected", 0

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        placeholders = ','.join('?' for _ in project_ids)

        # Grab titles for logging before deleting
        cursor.execute(f'SELECT id, title FROM admin_projects WHERE id IN ({placeholders})', project_ids)
        titles = [row['title'] for row in cursor.fetchall()]

        cursor.execute(f'DELETE FROM admin_projects WHERE id IN ({placeholders})', project_ids)
        conn.commit()
        affected = cursor.rowcount

        # Log activity
        log_activity('BULK_DELETE', None,
                      f'Deleted {affected} project(s): {", ".join(titles) if titles else project_ids}')

        conn.close()
        return True, f"{affected} project(s) deleted successfully", affected
    except Exception as e:
        conn.close()
        return False, f"Error deleting projects: {str(e)}", 0


def duplicate_project(project_id):
    """Clone an existing project as a starting template.
    The duplicate gets a unique slug (appending '-copy', '-copy-2', etc.),
    a '(Copy)' suffix on the title, is always created as a draft, is never
    featured, and its view count resets to 0.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM admin_projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False, "Project not found", None

        original = dict(row)

        # Build a unique slug for the copy
        base_slug = f"{original['slug']}-copy"
        new_slug = base_slug
        suffix = 2
        while True:
            cursor.execute('SELECT 1 FROM admin_projects WHERE slug = ?', (new_slug,))
            if not cursor.fetchone():
                break
            new_slug = f"{base_slug}-{suffix}"
            suffix += 1

        new_title = f"{original['title']} (Copy)"

        cursor.execute('''
            INSERT INTO admin_projects
                (slug, title, description, category, tags, github_url, image_url,
                 demo_url, status, featured, view_count, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?)
        ''', (
            new_slug,
            new_title,
            original.get('description', ''),
            original.get('category', ''),
            original.get('tags', '[]'),
            original.get('github_url', ''),
            original.get('image_url', ''),
            original.get('demo_url', ''),
            'draft',
            original.get('display_order', 0),
        ))

        conn.commit()
        new_id = cursor.lastrowid

        # Log activity
        log_activity('DUPLICATE', new_id, f'Duplicated project "{original["title"]}" -> "{new_title}"')

        conn.close()
        return True, "Project duplicated successfully", new_id
    except Exception as e:
        conn.close()
        return False, f"Error duplicating project: {str(e)}", None

def get_project_stats():
    """Get portfolio statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # Total projects
    cursor.execute('SELECT COUNT(*) as count FROM admin_projects')
    stats['total_projects'] = cursor.fetchone()['count']
    
    # Published projects
    cursor.execute('SELECT COUNT(*) as count FROM admin_projects WHERE status = "published"')
    stats['published_projects'] = cursor.fetchone()['count']
    
    # Featured projects
    cursor.execute('SELECT COUNT(*) as count FROM admin_projects WHERE featured = 1')
    stats['featured_projects'] = cursor.fetchone()['count']
    
    # Total views
    cursor.execute('SELECT SUM(view_count) as total FROM admin_projects')
    stats['total_views'] = cursor.fetchone()['total'] or 0
    
    # Projects by category
    cursor.execute('SELECT category, COUNT(*) as count FROM admin_projects GROUP BY category')
    stats['by_category'] = {row['category']: row['count'] for row in cursor.fetchall()}
    
    conn.close()
    return stats

def search_projects(query):
    """Search projects by title, description, or tags"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    search_term = f"%{query}%"
    cursor.execute('''
        SELECT * FROM admin_projects 
        WHERE title LIKE ? OR description LIKE ? OR tags LIKE ?
        ORDER BY created_at DESC
    ''', (search_term, search_term, search_term))
    
    projects = [dict(row) for row in cursor.fetchall()]
    
    # Parse tags
    for project in projects:
        if project['tags']:
            try:
                project['tags'] = json.loads(project['tags'])
            except:
                project['tags'] = []
    
    conn.close()
    return projects

def increment_view_count(slug):
    """Increment view count for a project"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE admin_projects SET view_count = view_count + 1 WHERE slug = ?', (slug,))
    conn.commit()
    conn.close()

def log_activity(action, project_id, details):
    """Log admin activity"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO admin_activity_log (action, project_id, details)
        VALUES (?, ?, ?)
    ''', (action, project_id, details))
    
    conn.commit()
    conn.close()

def get_activity_log(limit=50):
    """Get recent admin activities"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM admin_activity_log 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    
    activities = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return activities

def bulk_import_projects(projects_list):
    """Import multiple projects at once"""
    conn = get_db_connection()
    cursor = conn.cursor()
    imported = 0
    failed = 0
    
    for project in projects_list:
        try:
            tags_json = json.dumps(project.get('tags', []))
            cursor.execute('''
                INSERT OR REPLACE INTO admin_projects 
                (slug, title, description, category, tags, github_url, image_url, demo_url, status, featured)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project.get('slug'),
                project.get('title'),
                project.get('description', ''),
                project.get('category', ''),
                tags_json,
                project.get('github_url', ''),
                project.get('image_url', ''),
                project.get('demo_url', ''),
                project.get('status', 'published'),
                project.get('featured', False)
            ))
            imported += 1
        except Exception as e:
            failed += 1
    
    conn.commit()
    conn.close()
    return imported, failed


# ==================== MY LEARNING MANAGEMENT ====================
# Same CRUD pattern as admin_projects above, so "My Learning" cards get the
# exact same add/edit/delete/reorder/bulk/duplicate features as Projects.

def get_all_learning_items(status='all'):
    """Get all learning items from admin database"""
    conn = get_db_connection()
    cursor = conn.cursor()

    if status == 'all':
        cursor.execute('SELECT * FROM admin_learning ORDER BY display_order ASC, created_at DESC')
    else:
        cursor.execute('SELECT * FROM admin_learning WHERE status = ? ORDER BY display_order ASC, created_at DESC', (status,))

    items = [dict(row) for row in cursor.fetchall()]

    for item in items:
        if item['tags']:
            try:
                item['tags'] = json.loads(item['tags'])
            except Exception:
                item['tags'] = []
        else:
            item['tags'] = []

    conn.close()
    return items


def get_learning_item_by_slug(slug):
    """Get a specific learning item by slug"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM admin_learning WHERE slug = ?', (slug,))
    row = cursor.fetchone()
    conn.close()

    if row:
        item = dict(row)
        if item['tags']:
            try:
                item['tags'] = json.loads(item['tags'])
            except Exception:
                item['tags'] = []
        else:
            item['tags'] = []
        return item
    return None


def get_learning_item_by_id(item_id):
    """Get a specific learning item by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM admin_learning WHERE id = ?', (item_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        item = dict(row)
        if item['tags']:
            try:
                item['tags'] = json.loads(item['tags'])
            except Exception:
                item['tags'] = []
        else:
            item['tags'] = []
        return item
    return None


def create_learning_item(slug, title, description, full_text, category, tags, image_url,
                          link_url='', link_type='linkedin', status='published', featured=False):
    """Create a new My Learning item"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        tags_json = json.dumps(tags) if isinstance(tags, list) else tags

        cursor.execute('''
            INSERT INTO admin_learning (slug, title, description, full_text, category, tags,
                                         image_url, link_url, link_type, status, featured)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (slug, title, description, full_text, category, tags_json, image_url,
              link_url, link_type, status, featured))

        conn.commit()
        item_id = cursor.lastrowid

        log_activity('CREATE', item_id, f'Created learning item: {title}')

        conn.close()
        return True, "Learning item created successfully", item_id
    except sqlite3.IntegrityError:
        conn.close()
        return False, "A learning item with this slug already exists", None
    except Exception as e:
        conn.close()
        return False, f"Error creating learning item: {str(e)}", None


def update_learning_item(item_id, slug, title, description, full_text, category, tags, image_url,
                          link_url='', link_type='linkedin', status='published', featured=False):
    """Update an existing My Learning item"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        tags_json = json.dumps(tags) if isinstance(tags, list) else tags

        cursor.execute('''
            UPDATE admin_learning
            SET slug = ?, title = ?, description = ?, full_text = ?, category = ?, tags = ?,
                image_url = ?, link_url = ?, link_type = ?, status = ?, featured = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (slug, title, description, full_text, category, tags_json, image_url,
              link_url, link_type, status, featured, item_id))

        conn.commit()

        log_activity('UPDATE', item_id, f'Updated learning item: {title}')

        conn.close()
        return True, "Learning item updated successfully"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "A learning item with this slug already exists"
    except Exception as e:
        conn.close()
        return False, f"Error updating learning item: {str(e)}"


def delete_learning_item(item_id):
    """Delete a My Learning item"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT title FROM admin_learning WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        item_title = row['title'] if row else 'Unknown'

        cursor.execute('DELETE FROM admin_learning WHERE id = ?', (item_id,))
        conn.commit()

        log_activity('DELETE', item_id, f'Deleted learning item: {item_title}')

        conn.close()
        return True, "Learning item deleted successfully"
    except Exception as e:
        conn.close()
        return False, f"Error deleting learning item: {str(e)}"


def reorder_learning_items(order_list):
    """Update learning item display order
    order_list: list of dicts with 'id' and 'position' keys
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        for item in order_list:
            item_id = item.get('id')
            position = item.get('position', 0)
            cursor.execute(
                'UPDATE admin_learning SET display_order = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (position, item_id)
            )
        conn.commit()

        log_activity('REORDER', None, f'Reordered {len(order_list)} learning items')

        conn.close()
        return True, "Learning item order updated successfully"
    except Exception as e:
        conn.close()
        return False, f"Error updating learning item order: {str(e)}"


def bulk_update_learning_status(item_ids, status):
    """Bulk update status (publish/draft/archive) for multiple learning items at once."""
    if not item_ids:
        return False, "No learning items selected", 0

    valid_statuses = {'published', 'draft', 'archived'}
    if status not in valid_statuses:
        return False, f"Invalid status: {status}", 0

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        placeholders = ','.join('?' for _ in item_ids)
        cursor.execute(
            f'UPDATE admin_learning SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id IN ({placeholders})',
            (status, *item_ids)
        )
        conn.commit()
        affected = cursor.rowcount

        log_activity('BULK_STATUS_UPDATE', None,
                      f'Updated status to "{status}" for {affected} learning item(s): {item_ids}')

        conn.close()
        return True, f"{affected} learning item(s) updated to {status}", affected
    except Exception as e:
        conn.close()
        return False, f"Error updating learning items: {str(e)}", 0


def bulk_delete_learning_items(item_ids):
    """Bulk delete multiple learning items at once."""
    if not item_ids:
        return False, "No learning items selected", 0

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        placeholders = ','.join('?' for _ in item_ids)

        cursor.execute(f'SELECT id, title FROM admin_learning WHERE id IN ({placeholders})', item_ids)
        titles = [row['title'] for row in cursor.fetchall()]

        cursor.execute(f'DELETE FROM admin_learning WHERE id IN ({placeholders})', item_ids)
        conn.commit()
        affected = cursor.rowcount

        log_activity('BULK_DELETE', None,
                      f'Deleted {affected} learning item(s): {", ".join(titles) if titles else item_ids}')

        conn.close()
        return True, f"{affected} learning item(s) deleted successfully", affected
    except Exception as e:
        conn.close()
        return False, f"Error deleting learning items: {str(e)}", 0


def duplicate_learning_item(item_id):
    """Clone an existing learning item as a starting template.
    The duplicate gets a unique slug (appending '-copy', '-copy-2', etc.),
    a '(Copy)' suffix on the title, is always created as a draft, is never
    featured, and its view count resets to 0.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM admin_learning WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False, "Learning item not found", None

        original = dict(row)

        base_slug = f"{original['slug']}-copy"
        new_slug = base_slug
        suffix = 2
        while True:
            cursor.execute('SELECT 1 FROM admin_learning WHERE slug = ?', (new_slug,))
            if not cursor.fetchone():
                break
            new_slug = f"{base_slug}-{suffix}"
            suffix += 1

        new_title = f"{original['title']} (Copy)"

        cursor.execute('''
            INSERT INTO admin_learning
                (slug, title, description, full_text, category, tags, image_url,
                 link_url, link_type, status, featured, view_count, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?)
        ''', (
            new_slug,
            new_title,
            original.get('description', ''),
            original.get('full_text', ''),
            original.get('category', ''),
            original.get('tags', '[]'),
            original.get('image_url', ''),
            original.get('link_url', ''),
            original.get('link_type', 'linkedin'),
            'draft',
            original.get('display_order', 0),
        ))

        conn.commit()
        new_id = cursor.lastrowid

        log_activity('DUPLICATE', new_id, f'Duplicated learning item "{original["title"]}" -> "{new_title}"')

        conn.close()
        return True, "Learning item duplicated successfully", new_id
    except Exception as e:
        conn.close()
        return False, f"Error duplicating learning item: {str(e)}", None


def get_learning_stats():
    """Get My Learning statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()

    stats = {}

    cursor.execute('SELECT COUNT(*) as count FROM admin_learning')
    stats['total_learning'] = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM admin_learning WHERE status = "published"')
    stats['published_learning'] = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM admin_learning WHERE featured = 1')
    stats['featured_learning'] = cursor.fetchone()['count']

    cursor.execute('SELECT SUM(view_count) as total FROM admin_learning')
    stats['total_views'] = cursor.fetchone()['total'] or 0

    cursor.execute('SELECT category, COUNT(*) as count FROM admin_learning GROUP BY category')
    stats['by_category'] = {row['category']: row['count'] for row in cursor.fetchall()}

    conn.close()
    return stats


def search_learning_items(query):
    """Search learning items by title, description, or tags"""
    conn = get_db_connection()
    cursor = conn.cursor()

    search_term = f"%{query}%"
    cursor.execute('''
        SELECT * FROM admin_learning
        WHERE title LIKE ? OR description LIKE ? OR tags LIKE ?
        ORDER BY created_at DESC
    ''', (search_term, search_term, search_term))

    items = [dict(row) for row in cursor.fetchall()]

    for item in items:
        if item['tags']:
            try:
                item['tags'] = json.loads(item['tags'])
            except Exception:
                item['tags'] = []
        else:
            item['tags'] = []

    conn.close()
    return items


# ==================== ACHIEVEMENTS MANAGEMENT ====================
# Same CRUD pattern as admin_projects / admin_learning above, so
# "Achievements & Certifications" cards get the same add/edit/delete/
# reorder/bulk/duplicate features.

def get_all_achievements(status='all'):
    """Get all achievements from admin database"""
    conn = get_db_connection()
    cursor = conn.cursor()

    if status == 'all':
        cursor.execute('SELECT * FROM admin_achievements ORDER BY display_order ASC, created_at DESC')
    else:
        cursor.execute('SELECT * FROM admin_achievements WHERE status = ? ORDER BY display_order ASC, created_at DESC', (status,))

    items = [dict(row) for row in cursor.fetchall()]

    for item in items:
        if item['skills']:
            try:
                item['skills'] = json.loads(item['skills'])
            except Exception:
                item['skills'] = []
        else:
            item['skills'] = []

    conn.close()
    return items


def get_achievement_by_slug(slug):
    """Get a specific achievement by slug"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM admin_achievements WHERE slug = ?', (slug,))
    row = cursor.fetchone()
    conn.close()

    if row:
        item = dict(row)
        if item['skills']:
            try:
                item['skills'] = json.loads(item['skills'])
            except Exception:
                item['skills'] = []
        else:
            item['skills'] = []
        return item
    return None


def get_achievement_by_id(item_id):
    """Get a specific achievement by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM admin_achievements WHERE id = ?', (item_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        item = dict(row)
        if item['skills']:
            try:
                item['skills'] = json.loads(item['skills'])
            except Exception:
                item['skills'] = []
        else:
            item['skills'] = []
        return item
    return None


def create_achievement(slug, title, issuer, description, category, achievement_type, icon,
                        date_label, skills, certificate_url='', status='published', featured=False):
    """Create a new achievement"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        skills_json = json.dumps(skills) if isinstance(skills, list) else skills

        cursor.execute('''
            INSERT INTO admin_achievements (slug, title, issuer, description, category, achievement_type,
                                             icon, date_label, skills, certificate_url, status, featured)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (slug, title, issuer, description, category, achievement_type, icon, date_label,
              skills_json, certificate_url, status, featured))

        conn.commit()
        item_id = cursor.lastrowid

        log_activity('CREATE', item_id, f'Created achievement: {title}')

        conn.close()
        return True, "Achievement created successfully", item_id
    except sqlite3.IntegrityError:
        conn.close()
        return False, "An achievement with this slug already exists", None
    except Exception as e:
        conn.close()
        return False, f"Error creating achievement: {str(e)}", None


def update_achievement(item_id, slug, title, issuer, description, category, achievement_type, icon,
                        date_label, skills, certificate_url='', status='published', featured=False):
    """Update an existing achievement"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        skills_json = json.dumps(skills) if isinstance(skills, list) else skills

        cursor.execute('''
            UPDATE admin_achievements
            SET slug = ?, title = ?, issuer = ?, description = ?, category = ?, achievement_type = ?,
                icon = ?, date_label = ?, skills = ?, certificate_url = ?, status = ?, featured = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (slug, title, issuer, description, category, achievement_type, icon, date_label,
              skills_json, certificate_url, status, featured, item_id))

        conn.commit()

        log_activity('UPDATE', item_id, f'Updated achievement: {title}')

        conn.close()
        return True, "Achievement updated successfully"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "An achievement with this slug already exists"
    except Exception as e:
        conn.close()
        return False, f"Error updating achievement: {str(e)}"


def delete_achievement(item_id):
    """Delete an achievement"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT title FROM admin_achievements WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        item_title = row['title'] if row else 'Unknown'

        cursor.execute('DELETE FROM admin_achievements WHERE id = ?', (item_id,))
        conn.commit()

        log_activity('DELETE', item_id, f'Deleted achievement: {item_title}')

        conn.close()
        return True, "Achievement deleted successfully"
    except Exception as e:
        conn.close()
        return False, f"Error deleting achievement: {str(e)}"


def reorder_achievements(order_list):
    """Update achievement display order
    order_list: list of dicts with 'id' and 'position' keys
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        for item in order_list:
            item_id = item.get('id')
            position = item.get('position', 0)
            cursor.execute(
                'UPDATE admin_achievements SET display_order = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (position, item_id)
            )
        conn.commit()

        log_activity('REORDER', None, f'Reordered {len(order_list)} achievements')

        conn.close()
        return True, "Achievement order updated successfully"
    except Exception as e:
        conn.close()
        return False, f"Error updating achievement order: {str(e)}"


def bulk_update_achievement_status(item_ids, status):
    """Bulk update status (publish/draft/archive) for multiple achievements at once."""
    if not item_ids:
        return False, "No achievements selected", 0

    valid_statuses = {'published', 'draft', 'archived'}
    if status not in valid_statuses:
        return False, f"Invalid status: {status}", 0

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        placeholders = ','.join('?' for _ in item_ids)
        cursor.execute(
            f'UPDATE admin_achievements SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id IN ({placeholders})',
            (status, *item_ids)
        )
        conn.commit()
        affected = cursor.rowcount

        log_activity('BULK_STATUS_UPDATE', None,
                      f'Updated status to "{status}" for {affected} achievement(s): {item_ids}')

        conn.close()
        return True, f"{affected} achievement(s) updated to {status}", affected
    except Exception as e:
        conn.close()
        return False, f"Error updating achievements: {str(e)}", 0


def bulk_delete_achievements(item_ids):
    """Bulk delete multiple achievements at once."""
    if not item_ids:
        return False, "No achievements selected", 0

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        placeholders = ','.join('?' for _ in item_ids)

        cursor.execute(f'SELECT id, title FROM admin_achievements WHERE id IN ({placeholders})', item_ids)
        titles = [row['title'] for row in cursor.fetchall()]

        cursor.execute(f'DELETE FROM admin_achievements WHERE id IN ({placeholders})', item_ids)
        conn.commit()
        affected = cursor.rowcount

        log_activity('BULK_DELETE', None,
                      f'Deleted {affected} achievement(s): {", ".join(titles) if titles else item_ids}')

        conn.close()
        return True, f"{affected} achievement(s) deleted successfully", affected
    except Exception as e:
        conn.close()
        return False, f"Error deleting achievements: {str(e)}", 0


def duplicate_achievement(item_id):
    """Clone an existing achievement as a starting template.
    The duplicate gets a unique slug (appending '-copy', '-copy-2', etc.),
    a '(Copy)' suffix on the title, is always created as a draft, is never
    featured, and its view count resets to 0.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM admin_achievements WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False, "Achievement not found", None

        original = dict(row)

        base_slug = f"{original['slug']}-copy"
        new_slug = base_slug
        suffix = 2
        while True:
            cursor.execute('SELECT 1 FROM admin_achievements WHERE slug = ?', (new_slug,))
            if not cursor.fetchone():
                break
            new_slug = f"{base_slug}-{suffix}"
            suffix += 1

        new_title = f"{original['title']} (Copy)"

        cursor.execute('''
            INSERT INTO admin_achievements
                (slug, title, issuer, description, category, achievement_type, icon, date_label,
                 skills, certificate_url, status, featured, view_count, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?)
        ''', (
            new_slug,
            new_title,
            original.get('issuer', ''),
            original.get('description', ''),
            original.get('category', ''),
            original.get('achievement_type', ''),
            original.get('icon', 'fas fa-trophy'),
            original.get('date_label', ''),
            original.get('skills', '[]'),
            original.get('certificate_url', ''),
            'draft',
            original.get('display_order', 0),
        ))

        conn.commit()
        new_id = cursor.lastrowid

        log_activity('DUPLICATE', new_id, f'Duplicated achievement "{original["title"]}" -> "{new_title}"')

        conn.close()
        return True, "Achievement duplicated successfully", new_id
    except Exception as e:
        conn.close()
        return False, f"Error duplicating achievement: {str(e)}", None


def get_achievement_stats():
    """Get achievements statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()

    stats = {}

    cursor.execute('SELECT COUNT(*) as count FROM admin_achievements')
    stats['total_achievements'] = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM admin_achievements WHERE status = "published"')
    stats['published_achievements'] = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM admin_achievements WHERE featured = 1')
    stats['featured_achievements'] = cursor.fetchone()['count']

    cursor.execute('SELECT SUM(view_count) as total FROM admin_achievements')
    stats['total_views'] = cursor.fetchone()['total'] or 0

    cursor.execute('SELECT category, COUNT(*) as count FROM admin_achievements GROUP BY category')
    stats['by_category'] = {row['category']: row['count'] for row in cursor.fetchall()}

    conn.close()
    return stats


def search_achievements(query):
    """Search achievements by title, issuer, description, or skills"""
    conn = get_db_connection()
    cursor = conn.cursor()

    search_term = f"%{query}%"
    cursor.execute('''
        SELECT * FROM admin_achievements
        WHERE title LIKE ? OR issuer LIKE ? OR description LIKE ? OR skills LIKE ?
        ORDER BY created_at DESC
    ''', (search_term, search_term, search_term, search_term))

    items = [dict(row) for row in cursor.fetchall()]

    for item in items:
        if item['skills']:
            try:
                item['skills'] = json.loads(item['skills'])
            except Exception:
                item['skills'] = []
        else:
            item['skills'] = []

    conn.close()
    return items


# ==================== REVIEW MODERATION ====================

def get_all_reviews(status='all'):
    """Get all project reviews, optionally filtered by status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if status == 'all':
        cursor.execute('SELECT * FROM project_reviews ORDER BY created_at DESC')
    else:
        cursor.execute('SELECT * FROM project_reviews WHERE status = ? ORDER BY created_at DESC', (status,))
    
    reviews = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return reviews


def get_reviews_by_project(project_slug, status='approved'):
    """Get reviews for a specific project (public-facing, only approved)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM project_reviews WHERE project_slug = ? AND status = ? ORDER BY created_at DESC',
        (project_slug, status)
    )
    reviews = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return reviews


def update_review_status(review_id, new_status, reviewed_by_email):
    """Update review status and mark as reviewed"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            '''UPDATE project_reviews 
               SET status = ?, reviewed_at = ?, reviewed_by = ? 
               WHERE id = ?''',
            (new_status, datetime.now(timezone.utc).isoformat(), reviewed_by_email, review_id)
        )
        conn.commit()
        success = cursor.rowcount > 0
        message = "Review updated successfully" if success else "Review not found"
    except Exception as e:
        success = False
        message = str(e)
    finally:
        conn.close()
    
    return success, message


def delete_review(review_id):
    """Permanently delete a review"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM project_reviews WHERE id = ?', (review_id,))
        conn.commit()
        success = cursor.rowcount > 0
        message = "Review deleted successfully" if success else "Review not found"
    except Exception as e:
        success = False
        message = str(e)
    finally:
        conn.close()
    
    return success, message


def get_review_stats():
    """Get statistics about reviews"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    total = cursor.execute("SELECT COUNT(*) c FROM project_reviews").fetchone()["c"]
    approved = cursor.execute("SELECT COUNT(*) c FROM project_reviews WHERE status = 'approved'").fetchone()["c"]
    pending = cursor.execute("SELECT COUNT(*) c FROM project_reviews WHERE status = 'pending'").fetchone()["c"]
    hidden = cursor.execute("SELECT COUNT(*) c FROM project_reviews WHERE status = 'hidden'").fetchone()["c"]
    deleted = cursor.execute("SELECT COUNT(*) c FROM project_reviews WHERE status = 'deleted'").fetchone()["c"]
    avg_rating = cursor.execute("SELECT AVG(rating) a FROM project_reviews WHERE status = 'approved'").fetchone()["a"] or 0
    
    conn.close()
    
    return {
        "total": total,
        "approved": approved,
        "pending": pending,
        "hidden": hidden,
        "deleted": deleted,
        "avg_rating": round(avg_rating, 2)
    }


def get_site_review_summary():
    """Average rating & count for just the site-wide/overall footer
    reviews (project_slug == db.SITE_REVIEW_SLUG), kept separate from the
    per-project review averages returned by get_review_stats()."""
    conn = get_db_connection()
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT COUNT(*) c, AVG(rating) a FROM project_reviews "
        "WHERE project_slug = ? AND status = 'approved'",
        (db.SITE_REVIEW_SLUG,)
    ).fetchone()
    conn.close()
    return {
        "count": row["c"] or 0,
        "average": round(row["a"], 2) if row["a"] else 0
    }


# ==================== NEWSLETTER SUBSCRIBERS ====================

def get_all_subscribers():
    """Get all newsletter subscribers, newest first"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM newsletter_subscribers ORDER BY subscribed_at DESC')
    subscribers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return subscribers


def get_subscriber_stats():
    """Get subscriber count"""
    conn = get_db_connection()
    cursor = conn.cursor()
    total = cursor.execute("SELECT COUNT(*) c FROM newsletter_subscribers").fetchone()["c"]
    conn.close()
    return {"total": total}


def delete_subscriber(subscriber_id):
    """Remove a newsletter subscriber (unsubscribe from admin side)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM newsletter_subscribers WHERE id = ?', (subscriber_id,))
        conn.commit()
        success = cursor.rowcount > 0
        message = "Subscriber removed successfully" if success else "Subscriber not found"
    except Exception as e:
        success = False
        message = str(e)
    finally:
        conn.close()

    return success, message
