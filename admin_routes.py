"""
admin_routes.py - Flask blueprint for admin panel routes
Handles all admin dashboard API endpoints and page rendering
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from functools import wraps
from admin_auth import (
    login_required, verify_admin_password, change_admin_password, get_admin_email,
    request_password_reset, verify_reset_otp_and_set_password
)
import db
from admin_db import (
    init_admin_tables, get_all_projects, get_project_by_slug, get_project_by_id,
    create_project, update_project, delete_project, get_project_stats,
    search_projects, log_activity, get_activity_log, increment_view_count,
    reorder_projects, bulk_update_status, bulk_delete_projects, duplicate_project,
    get_all_blog_posts, get_blog_post_by_id, get_blog_post_by_slug,
    create_blog_post, update_blog_post, delete_blog_post, get_blog_stats,
    search_blog_posts, get_all_reviews, get_reviews_by_project, update_review_status,
    delete_review, get_review_stats
)
import json
import re
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def slugify(text):
    text = (text or '').lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

# ==================== LOGIN / LOGOUT ====================

@admin_bp.route('/')
def index():
    """Convenience redirect: /admin -> dashboard (or login if not signed in)"""
    if 'admin_logged_in' in session:
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('admin.login'))


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        email = (data.get('email') or '').strip()
        password = (data.get('password') or '').strip()
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        success, message = verify_admin_password(email, password)
        
        if success:
            session['admin_logged_in'] = True
            session['admin_email'] = email
            session.permanent = True
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': message, 'redirect': '/admin/dashboard'})
            return redirect(url_for('admin.dashboard'))
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': message}), 401
            # For form submissions, we'll handle it in the template
            return render_template('admin_login.html', error=message), 401
    
    if 'admin_logged_in' in session:
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin_login.html')

@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    session.clear()
    return redirect(url_for('admin.login'))


# ==================== FORGOT / RESET PASSWORD (EMAIL OTP) ====================

@admin_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Step 1: admin enters their email, we email them a 6-digit OTP code."""
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        email = (data.get('email') or '').strip()

        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400

        success, message = request_password_reset(email)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': success, 'message': message,
                             'redirect': url_for('admin.reset_password', email=email)})
        return redirect(url_for('admin.reset_password', email=email))

    return render_template('admin_forgot_password.html')


@admin_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Step 2: admin enters the OTP code + new password."""
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        email = (data.get('email') or '').strip()
        otp = (data.get('otp') or '').strip()
        new_password = (data.get('new_password') or '').strip()
        confirm_password = (data.get('confirm_password') or '').strip()

        if not all([email, otp, new_password, confirm_password]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400

        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match'}), 400

        success, message = verify_reset_otp_and_set_password(email, otp, new_password)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': success, 'message': message,
                             'redirect': url_for('admin.login') if success else None}), (200 if success else 400)
        return render_template('admin_reset_password.html', email=email,
                                error=None if success else message)

    email = request.args.get('email', '')
    return render_template('admin_reset_password.html', email=email, error=None)

# ==================== DASHBOARD ====================

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Main admin dashboard"""
    stats = get_project_stats()
    blog_stats = get_blog_stats()
    review_stats = get_review_stats()
    recent_projects = get_all_projects()[:5]
    recent_posts = get_all_blog_posts()[:5]
    activities = get_activity_log(10)
    
    # Get analytics data
    conn = db.get_connection()
    total_visits = conn.execute("SELECT COUNT(*) c FROM page_visits").fetchone()["c"]
    avg_duration = conn.execute("SELECT AVG(duration_ms) a FROM page_visits").fetchone()["a"] or 0
    top_pages = conn.execute(
        "SELECT path, COUNT(*) c FROM page_visits GROUP BY path ORDER BY c DESC LIMIT 5"
    ).fetchall()
    subscribers = conn.execute("SELECT COUNT(*) c FROM newsletter_subscribers").fetchone()["c"]
    messages = conn.execute("SELECT COUNT(*) c FROM contact_messages").fetchone()["c"]
    quiz_attempts = conn.execute("SELECT COUNT(*) c FROM quiz_results").fetchone()["c"]
    conn.close()
    
    analytics = {
        "total_visits": total_visits,
        "avg_response_ms": round(avg_duration, 1),
        "top_pages": [dict(r) for r in top_pages],
        "newsletter_subscribers": subscribers,
        "contact_messages": messages,
        "quiz_attempts": quiz_attempts
    }
    
    return render_template('admin_dashboard.html', 
                         stats=stats, 
                         blog_stats=blog_stats,
                         review_stats=review_stats,
                         analytics=analytics,
                         recent_projects=recent_projects,
                         recent_posts=recent_posts,
                         activities=activities,
                         admin_email=get_admin_email())

# ==================== PROJECTS MANAGEMENT ====================

@admin_bp.route('/projects')
@login_required
def projects_list():
    """List all projects"""
    status = request.args.get('status', 'all')
    projects = get_all_projects(status)
    
    return render_template('admin_projects.html', 
                         projects=projects,
                         selected_status=status)

@admin_bp.route('/project/new')
@login_required
def new_project():
    """Create new project page"""
    return render_template('admin_project_form.html', project=None)

@admin_bp.route('/project/<int:project_id>')
@login_required
def edit_project(project_id):
    """Edit project page"""
    project = get_project_by_id(project_id)
    if not project:
        return "Project not found", 404
    return render_template('admin_project_form.html', project=project)

@admin_bp.route('/project/<int:project_id>/view')
@login_required
def view_project(project_id):
    """View project details"""
    project = get_project_by_id(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    return jsonify(project)

# ==================== BLOG POST MANAGEMENT ====================
# Replaces the old separate token-protected /blog/new form - post
# create/edit/delete now happens from this same admin dashboard.

@admin_bp.route('/blog')
@login_required
def blog_list():
    """List all blog posts"""
    status = request.args.get('status', 'all')
    posts = get_all_blog_posts(status)

    return render_template('admin_blog.html',
                         posts=posts,
                         selected_status=status)

@admin_bp.route('/blog/new')
@login_required
def new_blog_post():
    """Create new blog post page"""
    return render_template('admin_blog_form.html', post=None)

@admin_bp.route('/blog/<int:post_id>')
@login_required
def edit_blog_post(post_id):
    """Edit blog post page"""
    post = get_blog_post_by_id(post_id)
    if not post:
        return "Blog post not found", 404
    return render_template('admin_blog_form.html', post=post)

@admin_bp.route('/blog/<int:post_id>/view')
@login_required
def view_blog_post(post_id):
    """View blog post details"""
    post = get_blog_post_by_id(post_id)
    if not post:
        return jsonify({'error': 'Blog post not found'}), 404
    return jsonify(post)

# ==================== API ENDPOINTS ====================

@admin_bp.route('/api/projects', methods=['GET'])
@login_required
def api_get_projects():
    """API: Get all projects"""
    status = request.args.get('status', 'all')
    search = request.args.get('search', '').strip()
    
    if search:
        projects = search_projects(search)
    else:
        projects = get_all_projects(status)
    
    return jsonify(projects)

@admin_bp.route('/api/project', methods=['POST'])
@login_required
def api_create_project():
    """API: Create new project"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['slug', 'title', 'category']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    # Parse tags
    tags = data.get('tags', [])
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
    
    success, message, project_id = create_project(
        slug=data.get('slug'),
        title=data.get('title'),
        description=data.get('description', ''),
        category=data.get('category'),
        tags=tags,
        github_url=data.get('github_url', ''),
        image_url=data.get('image_url', ''),
        demo_url=data.get('demo_url', ''),
        status=data.get('status', 'published'),
        featured=data.get('featured', False)
    )
    
    return jsonify({
        'success': success,
        'message': message,
        'project_id': project_id
    }), (200 if success else 400)

@admin_bp.route('/api/project/<int:project_id>', methods=['PUT'])
@login_required
def api_update_project(project_id):
    """API: Update project"""
    data = request.get_json()
    
    project = get_project_by_id(project_id)
    if not project:
        return jsonify({'success': False, 'message': 'Project not found'}), 404
    
    # Parse tags
    tags = data.get('tags', [])
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
    
    success, message = update_project(
        project_id=project_id,
        slug=data.get('slug', project['slug']),
        title=data.get('title', project['title']),
        description=data.get('description', project['description']),
        category=data.get('category', project['category']),
        tags=tags if tags else project.get('tags', []),
        github_url=data.get('github_url', project['github_url']),
        image_url=data.get('image_url', project['image_url']),
        demo_url=data.get('demo_url', project['demo_url']),
        status=data.get('status', project['status']),
        featured=data.get('featured', project['featured'])
    )
    
    return jsonify({
        'success': success,
        'message': message
    }), (200 if success else 400)

@admin_bp.route('/api/project/<int:project_id>', methods=['DELETE'])
@login_required
def api_delete_project(project_id):
    """API: Delete project"""
    success, message = delete_project(project_id)
    return jsonify({
        'success': success,
        'message': message
    }), (200 if success else 400)

@admin_bp.route('/api/projects/reorder', methods=['POST'])
def api_reorder_projects():
    """API: Reorder projects (public endpoint for drag-and-drop)"""
    try:
        data = request.get_json()
        order_list = data.get('order', [])
        
        if not order_list:
            return jsonify({'success': False, 'message': 'No order data provided'}), 400
        
        success, message = reorder_projects(order_list)
        return jsonify({
            'success': success,
            'message': message
        }), (200 if success else 400)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error reordering projects: {str(e)}'
        }), 400

@admin_bp.route('/api/projects/bulk-status', methods=['POST'])
@login_required
def api_bulk_update_status():
    """API: Bulk publish/draft/archive multiple projects at once"""
    try:
        data = request.get_json() or {}
        project_ids = data.get('project_ids', [])
        status = data.get('status', '')

        if not project_ids:
            return jsonify({'success': False, 'message': 'No projects selected'}), 400

        # Ensure IDs are ints
        try:
            project_ids = [int(pid) for pid in project_ids]
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Invalid project IDs'}), 400

        if status not in ('published', 'draft', 'archived'):
            return jsonify({'success': False, 'message': 'Invalid status value'}), 400

        success, message, affected = bulk_update_status(project_ids, status)
        return jsonify({
            'success': success,
            'message': message,
            'affected': affected
        }), (200 if success else 400)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating projects: {str(e)}'
        }), 400

@admin_bp.route('/api/projects/bulk-delete', methods=['POST'])
@login_required
def api_bulk_delete_projects():
    """API: Bulk delete multiple projects at once"""
    try:
        data = request.get_json() or {}
        project_ids = data.get('project_ids', [])

        if not project_ids:
            return jsonify({'success': False, 'message': 'No projects selected'}), 400

        try:
            project_ids = [int(pid) for pid in project_ids]
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Invalid project IDs'}), 400

        success, message, affected = bulk_delete_projects(project_ids)
        return jsonify({
            'success': success,
            'message': message,
            'affected': affected
        }), (200 if success else 400)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting projects: {str(e)}'
        }), 400

@admin_bp.route('/api/project/<int:project_id>/duplicate', methods=['POST'])
@login_required
def api_duplicate_project(project_id):
    """API: Duplicate/clone an existing project as a starting template"""
    success, message, new_id = duplicate_project(project_id)
    return jsonify({
        'success': success,
        'message': message,
        'project_id': new_id
    }), (200 if success else 400)

# ==================== BLOG POST API ENDPOINTS ====================

@admin_bp.route('/api/blog', methods=['GET'])
@login_required
def api_get_blog_posts():
    """API: Get all blog posts"""
    status = request.args.get('status', 'all')
    search = request.args.get('search', '').strip()

    if search:
        posts = search_blog_posts(search)
    else:
        posts = get_all_blog_posts(status)

    return jsonify(posts)

@admin_bp.route('/api/blog', methods=['POST'])
@login_required
def api_create_blog_post():
    """API: Create new blog post"""
    data = request.get_json()

    title = (data.get('title') or '').strip()
    summary = (data.get('summary') or '').strip()
    content = (data.get('content') or '').strip()
    if not (title and summary and content):
        return jsonify({'success': False, 'message': 'Title, summary and content are required'}), 400

    tags = data.get('tags', [])
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(',') if tag.strip()]

    slug = (data.get('slug') or '').strip() or slugify(title)
    slug = slugify(slug)

    success, message, post_id = create_blog_post(
        slug=slug,
        title=title,
        summary=summary,
        content=content,
        cover_image=data.get('cover_image', ''),
        tags=tags,
        status=data.get('status', 'published'),
    )

    return jsonify({
        'success': success,
        'message': message,
        'post_id': post_id
    }), (200 if success else 400)

@admin_bp.route('/api/blog/<int:post_id>', methods=['PUT'])
@login_required
def api_update_blog_post(post_id):
    """API: Update blog post"""
    data = request.get_json()

    post = get_blog_post_by_id(post_id)
    if not post:
        return jsonify({'success': False, 'message': 'Blog post not found'}), 404

    tags = data.get('tags', [])
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(',') if tag.strip()]

    title = data.get('title', post['title'])
    slug = (data.get('slug') or '').strip() or post['slug']
    slug = slugify(slug)

    success, message = update_blog_post(
        post_id=post_id,
        slug=slug,
        title=title,
        summary=data.get('summary', post['summary']),
        content=data.get('content', post['content']),
        cover_image=data.get('cover_image', post['cover_image']),
        tags=tags if tags else post.get('tags', []),
        status=data.get('status', post['status']),
    )

    return jsonify({
        'success': success,
        'message': message
    }), (200 if success else 400)

@admin_bp.route('/api/blog/<int:post_id>', methods=['DELETE'])
@login_required
def api_delete_blog_post(post_id):
    """API: Delete blog post"""
    success, message = delete_blog_post(post_id)
    return jsonify({
        'success': success,
        'message': message
    }), (200 if success else 400)

# ==================== REVIEWS MANAGEMENT ====================

@admin_bp.route('/reviews')
@login_required
def reviews_list():
    """List all project reviews"""
    status = request.args.get('status', 'all')
    reviews = get_all_reviews(status)
    
    return render_template('admin_reviews.html', 
                         reviews=reviews,
                         selected_status=status)

@admin_bp.route('/api/reviews', methods=['GET'])
@login_required
def api_get_reviews():
    """API: Get all reviews"""
    status = request.args.get('status', 'all')
    reviews = get_all_reviews(status)
    return jsonify(reviews)

@admin_bp.route('/api/review/<int:review_id>/status', methods=['PUT'])
@login_required
def api_update_review_status(review_id):
    """API: Update review status"""
    data = request.get_json()
    new_status = (data.get('status') or '').strip()
    
    if new_status not in ['approved', 'pending', 'hidden', 'deleted']:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    
    admin_email = session.get('admin_email', 'unknown')
    success, message = update_review_status(review_id, new_status, admin_email)
    
    return jsonify({
        'success': success,
        'message': message
    }), (200 if success else 400)

@admin_bp.route('/api/review/<int:review_id>', methods=['DELETE'])
@login_required
def api_delete_review(review_id):
    """API: Delete review"""
    success, message = delete_review(review_id)
    return jsonify({
        'success': success,
        'message': message
    }), (200 if success else 400)

@admin_bp.route('/api/review-stats')
@login_required
def api_get_review_stats():
    """API: Get review statistics"""
    stats = get_review_stats()
    return jsonify(stats)

# ==================== STATISTICS & ANALYTICS ====================

@admin_bp.route('/analytics')
@login_required
def analytics():
    """Admin analytics dashboard page"""
    conn = db.get_connection()
    total_visits = conn.execute("SELECT COUNT(*) c FROM page_visits").fetchone()["c"]
    avg_duration = conn.execute("SELECT AVG(duration_ms) a FROM page_visits").fetchone()["a"] or 0
    top_pages = conn.execute(
        "SELECT path, COUNT(*) c FROM page_visits GROUP BY path ORDER BY c DESC LIMIT 10"
    ).fetchall()
    subscribers = conn.execute("SELECT COUNT(*) c FROM newsletter_subscribers").fetchone()["c"]
    messages = conn.execute("SELECT COUNT(*) c FROM contact_messages").fetchone()["c"]
    reviews = conn.execute("SELECT COUNT(*) c FROM project_reviews").fetchone()["c"]
    quiz_attempts = conn.execute("SELECT COUNT(*) c FROM quiz_results").fetchone()["c"]
    recent_visits = conn.execute(
        "SELECT path, method, status_code, duration_ms, visited_at FROM page_visits "
        "ORDER BY id DESC LIMIT 50"
    ).fetchall()
    conn.close()
    
    analytics_data = {
        "total_visits": total_visits,
        "avg_response_ms": round(avg_duration, 1),
        "top_pages": [dict(r) for r in top_pages],
        "newsletter_subscribers": subscribers,
        "contact_messages": messages,
        "project_reviews": reviews,
        "quiz_attempts": quiz_attempts,
        "recent_visits": [dict(r) for r in recent_visits],
    }
    
    return render_template('admin_analytics.html', analytics=analytics_data)

@admin_bp.route('/api/stats')
@login_required
def api_get_stats():
    """API: Get dashboard statistics"""
    stats = get_project_stats()
    return jsonify(stats)

@admin_bp.route('/api/blog-stats')
@login_required
def api_get_blog_stats():
    """API: Get blog statistics"""
    stats = get_blog_stats()
    return jsonify(stats)

@admin_bp.route('/api/activities')
@login_required
def api_get_activities():
    """API: Get activity log"""
    limit = request.args.get('limit', 50, type=int)
    activities = get_activity_log(limit)
    return jsonify(activities)

# ==================== SETTINGS ====================

@admin_bp.route('/settings')
@login_required
def settings():
    """Admin settings page"""
    return render_template('admin_settings.html', admin_email=get_admin_email())

@admin_bp.route('/api/change-password', methods=['POST'])
@login_required
def api_change_password():
    """API: Change admin password"""
    data = request.get_json()
    
    old_password = data.get('old_password', '').strip()
    new_password = data.get('new_password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    
    if not all([old_password, new_password, confirm_password]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'New passwords do not match'}), 400
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
    
    success, message = change_admin_password(old_password, new_password)
    return jsonify({
        'success': success,
        'message': message
    }), (200 if success else 400)

# ==================== EXPORT/IMPORT ====================

@admin_bp.route('/api/export-projects', methods=['GET'])
@login_required
def api_export_projects():
    """API: Export projects as JSON"""
    projects = get_all_projects()
    
    # Make sure tags are properly formatted
    for project in projects:
        if isinstance(project.get('tags'), str):
            try:
                project['tags'] = json.loads(project['tags'])
            except:
                project['tags'] = []
    
    return jsonify({
        'success': True,
        'projects': projects,
        'exported_at': datetime.now().isoformat()
    })

@admin_bp.route('/api/import-projects', methods=['POST'])
@login_required
def api_import_projects():
    """API: Import projects from JSON"""
    data = request.get_json()
    projects = data.get('projects', [])
    
    if not projects:
        return jsonify({'success': False, 'message': 'No projects to import'}), 400
    
    imported = 0
    failed = 0
    
    for project in projects:
        try:
            tags = project.get('tags', [])
            success, message, _ = create_project(
                slug=project.get('slug'),
                title=project.get('title'),
                description=project.get('description', ''),
                category=project.get('category', ''),
                tags=tags,
                github_url=project.get('github_url', ''),
                image_url=project.get('image_url', ''),
                demo_url=project.get('demo_url', ''),
                status=project.get('status', 'published'),
                featured=project.get('featured', False)
            )
            if success:
                imported += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
    
    return jsonify({
        'success': True,
        'imported': imported,
        'failed': failed,
        'message': f'Imported {imported} projects, {failed} failed'
    })

@admin_bp.route('/api/analytics', methods=['GET'])
@login_required
def api_analytics_data():
    """API: Get analytics data for admin dashboard"""
    conn = db.get_connection()
    total_visits = conn.execute("SELECT COUNT(*) c FROM page_visits").fetchone()["c"]
    top_pages = conn.execute(
        "SELECT path, COUNT(*) c FROM page_visits GROUP BY path ORDER BY c DESC LIMIT 10"
    ).fetchall()
    avg_duration = conn.execute("SELECT AVG(duration_ms) a FROM page_visits").fetchone()["a"] or 0
    subscribers = conn.execute("SELECT COUNT(*) c FROM newsletter_subscribers").fetchone()["c"]
    messages = conn.execute("SELECT COUNT(*) c FROM contact_messages").fetchone()["c"]
    reviews = conn.execute("SELECT COUNT(*) c FROM project_reviews").fetchone()["c"]
    quiz_attempts = conn.execute("SELECT COUNT(*) c FROM quiz_results").fetchone()["c"]
    recent_visits = conn.execute(
        "SELECT path, method, status_code, duration_ms, visited_at FROM page_visits "
        "ORDER BY id DESC LIMIT 25"
    ).fetchall()
    conn.close()

    return jsonify({
        "total_visits": total_visits,
        "avg_response_ms": round(avg_duration, 1),
        "top_pages": [dict(r) for r in top_pages],
        "newsletter_subscribers": subscribers,
        "contact_messages": messages,
        "project_reviews": reviews,
        "quiz_attempts": quiz_attempts,
        "recent_visits": [dict(r) for r in recent_visits],
    })
