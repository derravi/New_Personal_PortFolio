"""
admin_routes.py - Flask blueprint for admin panel routes
Handles all admin dashboard API endpoints and page rendering
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, Response
from functools import wraps
from app.admin.admin_auth import (
    login_required, verify_admin_password, change_admin_password, get_admin_email,
    reset_password_with_passkey
)
from app.core import db
from app.admin.admin_db import (
    init_admin_tables, get_all_projects, get_project_by_slug, get_project_by_id,
    create_project, update_project, delete_project, get_project_stats,
    search_projects, log_activity, get_activity_log, increment_view_count,
    reorder_projects, bulk_update_status, bulk_delete_projects, duplicate_project,
    get_all_blog_posts, get_blog_post_by_id, get_blog_post_by_slug,
    create_blog_post, update_blog_post, delete_blog_post, get_blog_stats,
    search_blog_posts, get_all_reviews, get_reviews_by_project, update_review_status,
    delete_review, get_review_stats, get_site_review_summary,
    get_all_subscribers, get_subscriber_stats, delete_subscriber,
    get_all_learning_items, get_learning_item_by_slug, get_learning_item_by_id,
    create_learning_item, update_learning_item, delete_learning_item,
    reorder_learning_items, bulk_update_learning_status, bulk_delete_learning_items,
    duplicate_learning_item, get_learning_stats, search_learning_items,
    get_all_achievements, get_achievement_by_slug, get_achievement_by_id,
    create_achievement, update_achievement, delete_achievement,
    reorder_achievements, bulk_update_achievement_status, bulk_delete_achievements,
    duplicate_achievement, get_achievement_stats, search_achievements
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


# ==================== FORGOT / RESET PASSWORD (PASSKEY) ====================

@admin_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Recovery flow: admin enters the recovery passkey plus a new password,
    and if the passkey is correct the admin password is updated directly.
    No email is sent — everything happens in one step."""
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        passkey = (data.get('passkey') or '').strip()
        new_password = (data.get('new_password') or '').strip()
        confirm_password = (data.get('confirm_password') or '').strip()

        if not all([passkey, new_password, confirm_password]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400

        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match'}), 400

        success, message = reset_password_with_passkey(passkey, new_password)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': success, 'message': message,
                             'redirect': url_for('admin.login') if success else None}), (200 if success else 400)
        return render_template('admin_forgot_password.html', error=None if success else message)

    return render_template('admin_forgot_password.html', error=None)


@admin_bp.route('/reset-password')
def reset_password():
    """Old bookmarked link support: the two-step email flow was replaced by
    the single-step passkey flow above, so just send people there."""
    return redirect(url_for('admin.forgot_password'))

# ==================== DASHBOARD ====================

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Main admin dashboard"""
    stats = get_project_stats()
    blog_stats = get_blog_stats()
    review_stats = get_review_stats()
    site_review_summary = get_site_review_summary()
    subscriber_stats = get_subscriber_stats()
    learning_stats = get_learning_stats()
    achievement_stats = get_achievement_stats()
    recent_projects = get_all_projects()[:5]
    recent_posts = get_all_blog_posts()[:5]
    recent_learning = get_all_learning_items()[:5]
    recent_achievements = get_all_achievements()[:5]
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
                         site_review_summary=site_review_summary,
                         subscriber_stats=subscriber_stats,
                         learning_stats=learning_stats,
                         achievement_stats=achievement_stats,
                         analytics=analytics,
                         recent_projects=recent_projects,
                         recent_posts=recent_posts,
                         recent_learning=recent_learning,
                         recent_achievements=recent_achievements,
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

# ==================== MY LEARNING MANAGEMENT ====================

@admin_bp.route('/learning')
@login_required
def learning_list():
    """List all My Learning items"""
    status = request.args.get('status', 'all')
    items = get_all_learning_items(status)

    return render_template('admin_learning.html',
                         learning_items=items,
                         selected_status=status)

@admin_bp.route('/learning/new')
@login_required
def new_learning_item():
    """Create new My Learning item page"""
    return render_template('admin_learning_form.html', item=None)

@admin_bp.route('/learning/<int:item_id>')
@login_required
def edit_learning_item(item_id):
    """Edit My Learning item page"""
    item = get_learning_item_by_id(item_id)
    if not item:
        return "Learning item not found", 404
    return render_template('admin_learning_form.html', item=item)

@admin_bp.route('/learning/<int:item_id>/view')
@login_required
def view_learning_item(item_id):
    """View My Learning item details"""
    item = get_learning_item_by_id(item_id)
    if not item:
        return jsonify({'error': 'Learning item not found'}), 404
    return jsonify(item)

# ==================== ACHIEVEMENTS MANAGEMENT ====================

@admin_bp.route('/achievements')
@login_required
def achievements_list():
    """List all achievements"""
    status = request.args.get('status', 'all')
    items = get_all_achievements(status)

    return render_template('admin_achievements.html',
                         achievements=items,
                         selected_status=status)

@admin_bp.route('/achievement/new')
@login_required
def new_achievement():
    """Create new achievement page"""
    return render_template('admin_achievement_form.html', achievement=None)

@admin_bp.route('/achievement/<int:item_id>')
@login_required
def edit_achievement(item_id):
    """Edit achievement page"""
    item = get_achievement_by_id(item_id)
    if not item:
        return "Achievement not found", 404
    return render_template('admin_achievement_form.html', achievement=item)

@admin_bp.route('/achievement/<int:item_id>/view')
@login_required
def view_achievement(item_id):
    """View achievement details"""
    item = get_achievement_by_id(item_id)
    if not item:
        return jsonify({'error': 'Achievement not found'}), 404
    return jsonify(item)

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

# ==================== MY LEARNING API ENDPOINTS ====================

@admin_bp.route('/api/learning', methods=['GET'])
@login_required
def api_get_learning_items():
    """API: Get all My Learning items"""
    status = request.args.get('status', 'all')
    search = request.args.get('search', '').strip()

    if search:
        items = search_learning_items(search)
    else:
        items = get_all_learning_items(status)

    return jsonify(items)

@admin_bp.route('/api/learning', methods=['POST'])
@login_required
def api_create_learning_item():
    """API: Create new My Learning item"""
    data = request.get_json()

    required_fields = ['slug', 'title', 'category']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    tags = data.get('tags', [])
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(',') if tag.strip()]

    success, message, item_id = create_learning_item(
        slug=data.get('slug'),
        title=data.get('title'),
        description=data.get('description', ''),
        full_text=data.get('full_text', ''),
        category=data.get('category'),
        tags=tags,
        image_url=data.get('image_url', ''),
        link_url=data.get('link_url', ''),
        link_type=data.get('link_type', 'linkedin'),
        status=data.get('status', 'published'),
        featured=data.get('featured', False)
    )

    return jsonify({
        'success': success,
        'message': message,
        'item_id': item_id
    }), (200 if success else 400)

@admin_bp.route('/api/learning/<int:item_id>', methods=['PUT'])
@login_required
def api_update_learning_item(item_id):
    """API: Update My Learning item"""
    data = request.get_json()

    item = get_learning_item_by_id(item_id)
    if not item:
        return jsonify({'success': False, 'message': 'Learning item not found'}), 404

    tags = data.get('tags', [])
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(',') if tag.strip()]

    success, message = update_learning_item(
        item_id=item_id,
        slug=data.get('slug', item['slug']),
        title=data.get('title', item['title']),
        description=data.get('description', item['description']),
        full_text=data.get('full_text', item['full_text']),
        category=data.get('category', item['category']),
        tags=tags if tags else item.get('tags', []),
        image_url=data.get('image_url', item['image_url']),
        link_url=data.get('link_url', item['link_url']),
        link_type=data.get('link_type', item['link_type']),
        status=data.get('status', item['status']),
        featured=data.get('featured', item['featured'])
    )

    return jsonify({
        'success': success,
        'message': message
    }), (200 if success else 400)

@admin_bp.route('/api/learning/<int:item_id>', methods=['DELETE'])
@login_required
def api_delete_learning_item(item_id):
    """API: Delete My Learning item"""
    success, message = delete_learning_item(item_id)
    return jsonify({
        'success': success,
        'message': message
    }), (200 if success else 400)

@admin_bp.route('/api/learning/reorder', methods=['POST'])
def api_reorder_learning_items():
    """API: Reorder learning items (public endpoint for drag-and-drop)"""
    try:
        data = request.get_json()
        order_list = data.get('order', [])

        if not order_list:
            return jsonify({'success': False, 'message': 'No order data provided'}), 400

        success, message = reorder_learning_items(order_list)
        return jsonify({
            'success': success,
            'message': message
        }), (200 if success else 400)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error reordering learning items: {str(e)}'
        }), 400

@admin_bp.route('/api/learning/bulk-status', methods=['POST'])
@login_required
def api_bulk_update_learning_status():
    """API: Bulk publish/draft/archive multiple learning items at once"""
    try:
        data = request.get_json() or {}
        item_ids = data.get('item_ids', [])
        status = data.get('status', '')

        if not item_ids:
            return jsonify({'success': False, 'message': 'No learning items selected'}), 400

        try:
            item_ids = [int(iid) for iid in item_ids]
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Invalid learning item IDs'}), 400

        if status not in ('published', 'draft', 'archived'):
            return jsonify({'success': False, 'message': 'Invalid status value'}), 400

        success, message, affected = bulk_update_learning_status(item_ids, status)
        return jsonify({
            'success': success,
            'message': message,
            'affected': affected
        }), (200 if success else 400)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating learning items: {str(e)}'
        }), 400

@admin_bp.route('/api/learning/bulk-delete', methods=['POST'])
@login_required
def api_bulk_delete_learning_items():
    """API: Bulk delete multiple learning items at once"""
    try:
        data = request.get_json() or {}
        item_ids = data.get('item_ids', [])

        if not item_ids:
            return jsonify({'success': False, 'message': 'No learning items selected'}), 400

        try:
            item_ids = [int(iid) for iid in item_ids]
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Invalid learning item IDs'}), 400

        success, message, affected = bulk_delete_learning_items(item_ids)
        return jsonify({
            'success': success,
            'message': message,
            'affected': affected
        }), (200 if success else 400)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting learning items: {str(e)}'
        }), 400

@admin_bp.route('/api/learning/<int:item_id>/duplicate', methods=['POST'])
@login_required
def api_duplicate_learning_item(item_id):
    """API: Duplicate/clone an existing learning item as a starting template"""
    success, message, new_id = duplicate_learning_item(item_id)
    return jsonify({
        'success': success,
        'message': message,
        'item_id': new_id
    }), (200 if success else 400)

@admin_bp.route('/api/learning-stats', methods=['GET'])
@login_required
def api_get_learning_stats():
    """API: Get My Learning statistics"""
    stats = get_learning_stats()
    return jsonify(stats)

# ==================== ACHIEVEMENTS API ENDPOINTS ====================

@admin_bp.route('/api/achievements', methods=['GET'])
@login_required
def api_get_achievements():
    """API: Get all achievements"""
    status = request.args.get('status', 'all')
    search = request.args.get('search', '').strip()

    if search:
        items = search_achievements(search)
    else:
        items = get_all_achievements(status)

    return jsonify(items)

@admin_bp.route('/api/achievement', methods=['POST'])
@login_required
def api_create_achievement():
    """API: Create new achievement"""
    data = request.get_json()

    required_fields = ['slug', 'title', 'category']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    skills = data.get('skills', [])
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(',') if s.strip()]

    success, message, item_id = create_achievement(
        slug=data.get('slug'),
        title=data.get('title'),
        issuer=data.get('issuer', ''),
        description=data.get('description', ''),
        category=data.get('category'),
        achievement_type=data.get('achievement_type', ''),
        icon=data.get('icon', 'fas fa-trophy'),
        date_label=data.get('date_label', ''),
        skills=skills,
        certificate_url=data.get('certificate_url', ''),
        status=data.get('status', 'published'),
        featured=data.get('featured', False)
    )

    return jsonify({
        'success': success,
        'message': message,
        'item_id': item_id
    }), (200 if success else 400)

@admin_bp.route('/api/achievement/<int:item_id>', methods=['PUT'])
@login_required
def api_update_achievement(item_id):
    """API: Update achievement"""
    data = request.get_json()

    item = get_achievement_by_id(item_id)
    if not item:
        return jsonify({'success': False, 'message': 'Achievement not found'}), 404

    skills = data.get('skills', [])
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(',') if s.strip()]

    success, message = update_achievement(
        item_id=item_id,
        slug=data.get('slug', item['slug']),
        title=data.get('title', item['title']),
        issuer=data.get('issuer', item['issuer']),
        description=data.get('description', item['description']),
        category=data.get('category', item['category']),
        achievement_type=data.get('achievement_type', item['achievement_type']),
        icon=data.get('icon', item['icon']),
        date_label=data.get('date_label', item['date_label']),
        skills=skills if skills else item.get('skills', []),
        certificate_url=data.get('certificate_url', item['certificate_url']),
        status=data.get('status', item['status']),
        featured=data.get('featured', item['featured'])
    )

    return jsonify({
        'success': success,
        'message': message
    }), (200 if success else 400)

@admin_bp.route('/api/achievement/<int:item_id>', methods=['DELETE'])
@login_required
def api_delete_achievement(item_id):
    """API: Delete achievement"""
    success, message = delete_achievement(item_id)
    return jsonify({
        'success': success,
        'message': message
    }), (200 if success else 400)

@admin_bp.route('/api/achievements/reorder', methods=['POST'])
def api_reorder_achievements():
    """API: Reorder achievements (public endpoint for drag-and-drop)"""
    try:
        data = request.get_json()
        order_list = data.get('order', [])

        if not order_list:
            return jsonify({'success': False, 'message': 'No order data provided'}), 400

        success, message = reorder_achievements(order_list)
        return jsonify({
            'success': success,
            'message': message
        }), (200 if success else 400)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error reordering achievements: {str(e)}'
        }), 400

@admin_bp.route('/api/achievements/bulk-status', methods=['POST'])
@login_required
def api_bulk_update_achievement_status():
    """API: Bulk publish/draft/archive multiple achievements at once"""
    try:
        data = request.get_json() or {}
        item_ids = data.get('item_ids', [])
        status = data.get('status', '')

        if not item_ids:
            return jsonify({'success': False, 'message': 'No achievements selected'}), 400

        try:
            item_ids = [int(iid) for iid in item_ids]
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Invalid achievement IDs'}), 400

        if status not in ('published', 'draft', 'archived'):
            return jsonify({'success': False, 'message': 'Invalid status value'}), 400

        success, message, affected = bulk_update_achievement_status(item_ids, status)
        return jsonify({
            'success': success,
            'message': message,
            'affected': affected
        }), (200 if success else 400)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating achievements: {str(e)}'
        }), 400

@admin_bp.route('/api/achievements/bulk-delete', methods=['POST'])
@login_required
def api_bulk_delete_achievements():
    """API: Bulk delete multiple achievements at once"""
    try:
        data = request.get_json() or {}
        item_ids = data.get('item_ids', [])

        if not item_ids:
            return jsonify({'success': False, 'message': 'No achievements selected'}), 400

        try:
            item_ids = [int(iid) for iid in item_ids]
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Invalid achievement IDs'}), 400

        success, message, affected = bulk_delete_achievements(item_ids)
        return jsonify({
            'success': success,
            'message': message,
            'affected': affected
        }), (200 if success else 400)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting achievements: {str(e)}'
        }), 400

@admin_bp.route('/api/achievement/<int:item_id>/duplicate', methods=['POST'])
@login_required
def api_duplicate_achievement(item_id):
    """API: Duplicate/clone an existing achievement as a starting template"""
    success, message, new_id = duplicate_achievement(item_id)
    return jsonify({
        'success': success,
        'message': message,
        'item_id': new_id
    }), (200 if success else 400)

@admin_bp.route('/api/achievement-stats', methods=['GET'])
@login_required
def api_get_achievement_stats():
    """API: Get achievements statistics"""
    stats = get_achievement_stats()
    return jsonify(stats)

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
    """List all reviews. Supports an extra ?source= filter to separate the
    site-wide 'Overall Reviews' footer widget from per-project reviews,
    since both live in the same project_reviews table."""
    status = request.args.get('status', 'all')
    source = request.args.get('source', 'all')  # all | overall | projects
    reviews = get_all_reviews(status)

    if source == 'overall':
        reviews = [r for r in reviews if r['project_slug'] == db.SITE_REVIEW_SLUG]
    elif source == 'projects':
        reviews = [r for r in reviews if r['project_slug'] != db.SITE_REVIEW_SLUG]

    review_stats = get_review_stats()
    site_review_summary = get_site_review_summary()

    return render_template('admin_reviews.html', 
                         reviews=reviews,
                         selected_status=status,
                         selected_source=source,
                         site_review_slug=db.SITE_REVIEW_SLUG,
                         review_stats=review_stats,
                         site_review_summary=site_review_summary)

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

# ==================== NEWSLETTER SUBSCRIBERS MANAGEMENT ====================

@admin_bp.route('/subscribers')
@login_required
def subscribers_list():
    """List all newsletter subscribers"""
    subscribers = get_all_subscribers()
    stats = get_subscriber_stats()

    return render_template('admin_subscribers.html',
                         subscribers=subscribers,
                         stats=stats)

@admin_bp.route('/api/subscribers', methods=['GET'])
@login_required
def api_get_subscribers():
    """API: Get all newsletter subscribers"""
    return jsonify(get_all_subscribers())

@admin_bp.route('/api/subscriber/<int:subscriber_id>', methods=['DELETE'])
@login_required
def api_delete_subscriber(subscriber_id):
    """API: Remove/unsubscribe a newsletter subscriber"""
    success, message = delete_subscriber(subscriber_id)
    return jsonify({
        'success': success,
        'message': message
    }), (200 if success else 400)

@admin_bp.route('/api/subscribers/export', methods=['GET'])
@login_required
def api_export_subscribers():
    """API: Export all subscribers as a downloadable CSV file"""
    subscribers = get_all_subscribers()
    lines = ['email,subscribed_at']
    for s in subscribers:
        email = (s.get('email') or '').replace('"', '""')
        subscribed_at = (s.get('subscribed_at') or '').replace('"', '""')
        lines.append(f'"{email}","{subscribed_at}"')
    csv_data = '\n'.join(lines)

    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=newsletter_subscribers.csv'}
    )

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
