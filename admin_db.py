"""
admin_db.py - Admin database module for managing portfolio projects
Handles CRUD operations for projects with SQLite
"""

import sqlite3
import json
from datetime import datetime, timezone
import os

# Absolute path (same project data/ folder used by db.py), so this works no
# matter what directory the app is started from (local run, Docker, Gunicorn...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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
