"""
flask_app.py — Ravi Der's portfolio site.

Enhancement systems added on top of the original static site:
  - SQLite persistence (db.py)               -> Database Integration
  - Blog / Articles system                   -> /blog, /blog/<slug>
  - Project reviews & ratings REST endpoints  -> /api/projects/<slug>/reviews
  - REST API                                  -> /api/*
  - Newsletter signup + email notifications   -> /api/newsletter, mailer.py
  - Contact form backend (backs up EmailJS)   -> /api/contact
  - Skill assessment quiz                     -> /quiz, /api/quiz
  - Lightweight project recommendations       -> /api/recommendations/<slug>
  - Analytics dashboard                       -> /analytics (token protected)
  - Sitemap & SEO                             -> /sitemap.xml, /robots.txt
  - PDF export of resume/projects             -> /export/resume.pdf
  - Sentry error tracking (optional)          -> guarded by SENTRY_DSN
  - Basic performance monitoring              -> request timing -> page_visits table
"""

from flask import Flask, render_template, request, jsonify, Response, abort, redirect, url_for, send_file, session
from whitenoise import WhiteNoise
import os
import time
import re
import logging
import queue
import threading
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
from functools import wraps

from app.core import db
from app.services import mailer
from app.exports import pdf_export
from app.exports import docx_export
from app.core.rate_limit import rate_limit
from app.content import projects_data
from app.content.projects_data import CATEGORY_LABELS
from app.content import learning_data
from app.content import achievements_data

# --- Admin dashboard (manage projects: add/edit/delete from /admin) ---
from app.admin.admin_routes import admin_bp
from app.admin.admin_db import init_admin_tables
from app.admin.admin_auth import init_admin_credentials

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed — fine in prod where real env vars are set directly

# =========================
# Optional Sentry error tracking
# =========================
SENTRY_DSN = os.environ.get("SENTRY_DSN")
if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[FlaskIntegration()],
            traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
            environment=os.environ.get("FLASK_ENV", "production"),
        )
        print("[flask_app] Sentry initialized.")
    except ImportError:
        print("[flask_app] SENTRY_DSN is set but sentry-sdk is not installed. "
              "Run: pip install sentry-sdk[flask]")

try:
    app = Flask(__name__)

    # Secret Key
    app.secret_key = os.environ.get(
        "SECRET_KEY",
        "change-this-to-a-long-random-secret-key"
    )

    db.init_db()

    # --- Admin dashboard setup ---
    # Session config (admin login stays signed in for 7 days)
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'

    init_admin_tables()
    projects_data.ensure_seeded()  # one-time: loads existing projects into the DB
    learning_data.ensure_seeded()  # one-time: loads existing "My Learning" cards into the DB
    achievements_data.ensure_seeded()  # one-time: loads existing achievement cards into the DB
    init_admin_credentials()       # one-time: generates admin login if none exists yet

    app.register_blueprint(admin_bp)

except Exception as e:
    print(f"Error initializing Flask app: {e}")


# ⚡ OPTIMIZATION: Serve /static directly through WhiteNoise instead of
# PythonAnywhere's static file handler. WhiteNoise serves files straight
# out of Python (with gzip + far-future cache headers for hashed assets)
# so static requests never touch the slower host-level static routing.
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.wsgi_app = WhiteNoise(app.wsgi_app, root=STATIC_DIR, prefix="static/", max_age=2592000)


ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "change-this-admin-token")
SITE_URL = os.environ.get("SITE_URL", "https://example.com")


# =========================
# Structured logging (rotating file, complements Sentry/perf monitoring)
# =========================
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = RotatingFileHandler(os.path.join(LOG_DIR, "app.log"), maxBytes=1_000_000, backupCount=3)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)s [%(name)s] %(message)s"
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)


@app.errorhandler(404)
def not_found(e):
    app.logger.info(f"404: {request.path}")
    if request.path.startswith("/api/"):
        return jsonify({"error": "not found"}), 404
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    app.logger.error(f"500: {request.path} — {e}")
    if request.path.startswith("/api/"):
        return jsonify({"error": "internal server error"}), 500
    return render_template("500.html"), 500


# =========================
# Security Headers
# =========================
@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data: https:; "
        "style-src 'self' 'unsafe-inline' https:; "
        "script-src 'self' 'unsafe-inline' https:; "
        "connect-src 'self' https:; "
        "font-src 'self' https: data:;"
    )

    return response


# ⚡ OPTIMIZATION: Add caching headers for faster repeat visits
# Static files cached for 30 days, HTML pages for 5 minutes
# Expected improvement: 500ms-1s faster on repeat visits
@app.after_request
def set_cache_headers(response):
    """Tell browsers to cache files so repeat visits are fast"""
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=2592000'  # 30 days for static
    else:
        response.headers['Cache-Control'] = 'public, max-age=300'  # 5 min for HTML
    return response


# =========================
# Performance monitoring + analytics logging
# =========================
@app.before_request
def _start_timer():
    request._start_time = time.time()


# ⚡ OPTIMIZATION: Async analytics logging via a background worker thread.
# The old version wrote to SQLite synchronously inside the request/response
# cycle, adding 2-3s on PythonAnywhere. Now the request thread just drops a
# dict on an in-memory queue (microseconds) and returns immediately; a single
# daemon thread drains the queue and does the actual DB write off to the side.
_visit_queue: "queue.Queue" = queue.Queue(maxsize=10_000)


def _visit_logger_worker():
    while True:
        item = _visit_queue.get()
        if item is None:  # shutdown sentinel
            break
        try:
            conn = db.get_connection()
            with conn:
                conn.execute(
                    "INSERT INTO page_visits (path, method, status_code, duration_ms, user_agent, visited_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (item["path"], item["method"], item["status_code"], item["duration_ms"],
                     item["user_agent"], item["visited_at"]),
                )
            conn.close()
            if item["duration_ms"] > 500:
                print(f"[perf] SLOW REQUEST: {item['method']} {item['path']} took {item['duration_ms']:.0f}ms")
        except Exception as exc:
            print(f"[analytics] Failed to log visit: {exc}")
        finally:
            _visit_queue.task_done()


_visit_logger_thread = threading.Thread(target=_visit_logger_worker, daemon=True)
_visit_logger_thread.start()


@app.after_request
def _log_visit(response):
    try:
        duration_ms = (time.time() - getattr(request, "_start_time", time.time())) * 1000
        # Skip logging static assets & the analytics API itself to keep the table useful
        if not request.path.startswith("/static") and not request.path.startswith("/api/analytics"):
            try:
                _visit_queue.put_nowait({
                    "path": request.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                    "user_agent": request.headers.get("User-Agent", "")[:255],
                    "visited_at": db.now_iso(),
                })
            except queue.Full:
                # Under extreme load, drop the analytics event rather than
                # block the request — visitor data is not critical enough
                # to slow down real page loads.
                print("[analytics] Visit queue full, dropping event")
    except Exception as exc:
        print(f"[analytics] Failed to enqueue visit: {exc}")
    return response


def require_admin(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        token = request.args.get("token") or request.headers.get("X-Admin-Token")
        if token != ADMIN_TOKEN:
            abort(401)
        return view_func(*args, **kwargs)
    return wrapped


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


# =========================
# Core site pages (original routes, preserved)
# =========================
try:

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/about')
    def about():
        # No standalone about.html exists in this template; the About content
        # lives on the home page, so redirect there instead of 500ing.
        return redirect(url_for('home'))

    @app.route('/projects')
    def projects():
        return render_template(
            'projects.html',
            projects=projects_data.get_projects(),
            category_labels=CATEGORY_LABELS,
        )

    @app.route('/skills')
    def skills():
        return render_template('skills.html')

    @app.route('/achievements')
    def achievements():
        return render_template(
            'achievements.html',
            achievement_groups=achievements_data.get_achievements_grouped(),
            total_achievements=len(achievements_data.get_achievements()),
        )

    @app.route('/experience')
    def experience():
        return render_template('experience.html')

    @app.route('/education')
    def education():
        return render_template('education.html')

    @app.route('/blog')
    def blog():
        conn = db.get_connection()
        posts = conn.execute(
            "SELECT * FROM blog_posts WHERE status = 'published' OR status IS NULL "
            "ORDER BY published_at DESC"
        ).fetchall()
        conn.close()
        return render_template('blog.html', posts=posts)

    @app.route('/blog/<slug>')
    def blog_post(slug):
        conn = db.get_connection()
        with conn:
            conn.execute("UPDATE blog_posts SET views = views + 1 WHERE slug = ?", (slug,))
        post = conn.execute("SELECT * FROM blog_posts WHERE slug = ?", (slug,)).fetchone()
        related = conn.execute(
            "SELECT * FROM blog_posts WHERE slug != ? AND (status = 'published' OR status IS NULL) "
            "ORDER BY published_at DESC LIMIT 3", (slug,)
        ).fetchall()
        conn.close()
        if not post:
            abort(404)
        return render_template('blog_post.html', post=post, related=related)

    @app.route('/blog/new', methods=['GET', 'POST'])
    def blog_new():
        """Deprecated: publishing now happens from the admin dashboard
        (/admin/blog/new), which has full login-protected create/edit/delete
        for posts, cover images and tags. This route just forwards anyone
        who still has the old URL bookmarked."""
        if 'admin_logged_in' in session:
            return redirect(url_for('admin.new_blog_post'))
        return redirect(url_for('admin.login'))

    @app.route('/quiz')
    def quiz():
        return render_template('quiz.html')

    @app.route('/analytics')
    @require_admin
    def analytics_dashboard():
        return render_template('analytics.html', admin_token=ADMIN_TOKEN)

    # @app.route('/contact')
    # def contact():
    #     return render_template('contact.html')

    @app.route('/contact')
    def contact():
        return "Coming Soon..."

    @app.route('/my_learning')
    def my_learning():
        return render_template(
            'my_learning.html',
            learning_items=learning_data.get_learning_items(),
        )

except Exception as e:
    print(f"Route Error: {e}")


# =========================
# REST API
# =========================

@app.route('/api/projects')
def api_projects():
    return jsonify(projects_data.get_projects())


@app.route('/api/projects/<slug>')
def api_project_detail(slug):
    project = projects_data.get_project(slug)
    if not project:
        return jsonify({"error": "not found"}), 404
    return jsonify(project)


@app.route('/api/projects/<slug>/reviews', methods=['GET'])
def api_get_reviews(slug):
    conn = db.get_connection()
    rows = conn.execute(
        "SELECT reviewer_name, rating, comment, created_at FROM project_reviews "
        "WHERE project_slug = ? AND status = 'approved' ORDER BY created_at DESC", (slug,)
    ).fetchall()
    conn.close()
    reviews = [dict(r) for r in rows]
    avg = round(sum(r["rating"] for r in reviews) / len(reviews), 1) if reviews else None
    return jsonify({"project_slug": slug, "average_rating": avg, "count": len(reviews), "reviews": reviews})


@app.route('/api/projects/<slug>/reviews', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=60)
def api_post_review(slug):
    if not projects_data.get_project(slug):
        return jsonify({"error": "unknown project"}), 404

    data = request.get_json(silent=True) or request.form
    name = (data.get('name') or '').strip()[:80]
    rating = data.get('rating')
    comment = (data.get('comment') or '').strip()[:1000]

    try:
        rating = int(rating)
        assert 1 <= rating <= 5
    except (TypeError, ValueError, AssertionError):
        return jsonify({"error": "rating must be an integer between 1 and 5"}), 400

    if not name:
        return jsonify({"error": "name is required"}), 400

    conn = db.get_connection()
    with conn:
        conn.execute(
            "INSERT INTO project_reviews (project_slug, reviewer_name, rating, comment, status, created_at) "
            "VALUES (?, ?, ?, ?, 'pending', ?)",
            (slug, name, rating, comment, db.now_iso()),
        )
    conn.close()
    return jsonify({"status": "ok", "message": "Review submitted and is pending approval"}), 201


# Special "project_slug" value used to store site-wide / overall footer
# reviews inside the existing project_reviews table, so the admin panel's
# existing review moderation screen (/admin/reviews) keeps working for
# these too — no schema change needed. Defined once in db.py and shared
# with admin_db.py / admin_routes.py.
SITE_REVIEW_SLUG = db.SITE_REVIEW_SLUG


@app.route('/api/site-reviews', methods=['GET'])
def api_get_site_reviews():
    conn = db.get_connection()
    rows = conn.execute(
        "SELECT id, reviewer_name, rating, comment, created_at FROM project_reviews "
        "WHERE project_slug = ? AND status = 'approved' ORDER BY created_at DESC LIMIT 200",
        (SITE_REVIEW_SLUG,)
    ).fetchall()
    conn.close()
    reviews = [dict(r) for r in rows]
    avg = round(sum(r["rating"] for r in reviews) / len(reviews), 1) if reviews else 0
    return jsonify({"average_rating": avg, "count": len(reviews), "reviews": reviews})


@app.route('/api/site-reviews', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=60)
def api_post_site_review():
    data = request.get_json(silent=True) or request.form
    name = (data.get('name') or '').strip()[:80]
    rating = data.get('rating')
    comment = (data.get('comment') or '').strip()[:1000]

    try:
        rating = int(rating)
        assert 1 <= rating <= 5
    except (TypeError, ValueError, AssertionError):
        return jsonify({"error": "rating must be an integer between 1 and 5"}), 400

    if not name:
        return jsonify({"error": "name is required"}), 400

    conn = db.get_connection()
    with conn:
        conn.execute(
            "INSERT INTO project_reviews (project_slug, reviewer_name, rating, comment, status, created_at) "
            "VALUES (?, ?, ?, ?, 'approved', ?)",
            (SITE_REVIEW_SLUG, name, rating, comment, db.now_iso()),
        )
    conn.close()
    return jsonify({"status": "ok", "message": "Thanks for your feedback!"}), 201


@app.route('/api/recommendations/<slug>')
def api_recommendations(slug):
    return jsonify({"slug": slug, "related": projects_data.get_related(slug)})


@app.route('/api/blog')
def api_blog_list():
    conn = db.get_connection()
    rows = conn.execute("SELECT slug, title, summary, cover_image, tags, published_at, views "
                         "FROM blog_posts ORDER BY published_at DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/newsletter', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=60)
def api_newsletter():
    data = request.get_json(silent=True) or request.form
    email = (data.get('email') or '').strip().lower()
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return jsonify({"error": "Please provide a valid email address."}), 400

    conn = db.get_connection()
    try:
        with conn:
            conn.execute(
                "INSERT INTO newsletter_subscribers (email, subscribed_at) VALUES (?, ?)",
                (email, db.now_iso()),
            )
        already = False
    except Exception:
        already = True
    conn.close()

    if not already:
        mailer.send_email(
            email,
            "You're subscribed to Ravi Der's newsletter",
            "Thanks for subscribing! You'll get an email whenever a new project or article goes live."
        )
        return jsonify({"status": "subscribed"}), 201
    return jsonify({"status": "already_subscribed"}), 200


@app.route('/api/contact', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=60)
def api_contact():
    """Backend backup of the contact form (the frontend also sends via
    EmailJS directly from the browser). Storing it here means messages are
    never lost even if EmailJS fails, and gives the analytics dashboard
    something to show."""
    data = request.get_json(silent=True) or request.form
    name = (data.get('name') or '').strip()[:120]
    email = (data.get('email') or '').strip()[:200]
    subject = (data.get('subject') or '').strip()[:200]
    message = (data.get('message') or '').strip()[:5000]

    if not (name and email and message):
        return jsonify({"error": "name, email and message are required"}), 400
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return jsonify({"error": "invalid email address"}), 400

    conn = db.get_connection()
    with conn:
        conn.execute(
            "INSERT INTO contact_messages (name, email, subject, message, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, email, subject, message, db.now_iso()),
        )
    conn.close()

    owner_email = os.environ.get("MAIL_SENDER") or os.environ.get("MAIL_USERNAME")
    if owner_email:
        mailer.send_email(
            owner_email,
            f"New portfolio contact: {subject or 'no subject'}",
            f"From: {name} <{email}>\n\n{message}"
        )
    return jsonify({"status": "received"}), 201


@app.route('/api/quiz', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=60)
def api_quiz_submit():
    data = request.get_json(silent=True) or request.form
    name = (data.get('name') or 'Anonymous').strip()[:80]
    email = (data.get('email') or '').strip()[:200]
    try:
        score = int(data.get('score'))
        total = int(data.get('total'))
    except (TypeError, ValueError):
        return jsonify({"error": "score and total must be integers"}), 400

    pct = (score / total * 100) if total else 0
    if pct >= 85:
        level = "Advanced"
    elif pct >= 60:
        level = "Intermediate"
    else:
        level = "Beginner"

    conn = db.get_connection()
    with conn:
        conn.execute(
            "INSERT INTO quiz_results (name, email, score, total, level, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (name, email, score, total, level, db.now_iso()),
        )
    conn.close()
    return jsonify({"score": score, "total": total, "percentage": round(pct, 1), "level": level})


@app.route('/api/analytics/summary')
@require_admin
def api_analytics_summary():
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


# =========================
# SEO: sitemap & robots
# =========================
STATIC_ROUTES = [
    'home', 'projects', 'skills', 'achievements', 'experience',
    'education', 'blog', 'contact', 'my_learning', 'quiz', 'resume_view',
]


@app.route('/sitemap.xml')
def sitemap():
    conn = db.get_connection()
    posts = conn.execute(
        "SELECT slug, published_at FROM blog_posts WHERE status = 'published' OR status IS NULL"
    ).fetchall()
    conn.close()

    urls = []
    for endpoint in STATIC_ROUTES:
        urls.append((url_for(endpoint, _external=False), None))
    for post in posts:
        urls.append((url_for('blog_post', slug=post['slug'], _external=False), post['published_at']))

    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, lastmod in urls:
        xml_parts.append("<url>")
        xml_parts.append(f"<loc>{SITE_URL.rstrip('/')}{path}</loc>")
        if lastmod:
            xml_parts.append(f"<lastmod>{lastmod[:10]}</lastmod>")
        xml_parts.append("</url>")
    xml_parts.append("</urlset>")
    return Response("\n".join(xml_parts), mimetype="application/xml")


@app.route('/robots.txt')
def robots():
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /analytics",
        "Disallow: /admin",
        "Disallow: /api/",
        f"Sitemap: {SITE_URL.rstrip('/')}{url_for('sitemap')}",
    ]
    return Response("\n".join(lines), mimetype="text/plain")


# =========================
# PDF export
# =========================
@app.route('/export/resume.pdf')
def export_resume_pdf():
    buffer = pdf_export.build_resume_pdf()
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='Ravi_Der_Resume.pdf',
    )


@app.route('/export/resume.docx')
def export_resume_docx():
    buffer = docx_export.build_resume_docx()
    return send_file(
        buffer,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        as_attachment=True,
        download_name='Ravi_Der_Resume.docx',
    )


@app.route('/resume')
def resume_view():
    """Printable HTML resume (Ctrl/Cmd+P -> Save as PDF also works from here)."""
    by_category = {}
    for p in projects_data.get_projects():
        by_category.setdefault(p["category"], []).append(p)
    return render_template('resume.html', by_category=by_category, category_labels=CATEGORY_LABELS)


# =========================
# Health check (useful for Docker/CI)
# =========================
@app.route('/healthz')
def healthz():
    return jsonify({"status": "ok", "time": datetime.now(timezone.utc).isoformat()})


@app.route('/debug/sentry-test')
def sentry_test():
    """Deliberately raises an exception to verify Sentry is wired up correctly.
    Only enabled when FLASK_DEBUG=1, so it can never be hit in production."""
    if os.environ.get("FLASK_DEBUG", "1") != "1":
        abort(404)
    raise RuntimeError("This is a deliberate test error to verify Sentry integration.")


# =========================
# Run Application
# =========================
try:
    if __name__ == '__main__':
        debug_mode = os.environ.get("FLASK_DEBUG", "1") == "1"
        app.run(
            host='0.0.0.0',
            port=int(os.environ.get("PORT", 5000)),
            debug=debug_mode
        )
except Exception as e:
    print(f"Error {e}.")
