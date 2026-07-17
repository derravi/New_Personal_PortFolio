"""
db.py — Lightweight SQLite data layer for the portfolio site.

Uses Python's built-in sqlite3 module only (no extra dependency like
Flask-SQLAlchemy needed), so it works with nothing more than `pip install flask`.

Tables:
    blog_posts           -> Blog / Articles system
    project_reviews      -> Project reviews & ratings
    newsletter_subscribers -> Newsletter system
    contact_messages     -> Contact form submissions (backup of EmailJS)
    quiz_results          -> Skill assessment quiz results
    page_visits           -> Analytics dashboard data
"""

import sqlite3
import os
import time
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "portfolio.db")


def get_connection():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS blog_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    content TEXT NOT NULL,
    cover_image TEXT,
    tags TEXT,
    author TEXT DEFAULT 'Ravi Der',
    published_at TEXT NOT NULL,
    views INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS project_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_slug TEXT NOT NULL,
    reviewer_name TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('approved', 'pending', 'hidden', 'deleted')),
    created_at TEXT NOT NULL,
    reviewed_at TEXT,
    reviewed_by TEXT
);

CREATE TABLE IF NOT EXISTS newsletter_subscribers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    subscribed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS contact_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    score INTEGER NOT NULL,
    total INTEGER NOT NULL,
    level TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS page_visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL,
    method TEXT NOT NULL,
    status_code INTEGER,
    duration_ms REAL,
    user_agent TEXT,
    visited_at TEXT NOT NULL
);
"""

SEED_POSTS = [
    {
        "slug": "getting-started-with-ml-pipelines",
        "title": "Getting Started with End-to-End ML Pipelines",
        "summary": "A practical walkthrough of taking a model from a Jupyter notebook to a production-ready pipeline.",
        "content": (
            "Building a machine learning model is only half the job — the real "
            "engineering challenge is turning that notebook experiment into a "
            "reliable pipeline. In this article I walk through the stages I use "
            "on almost every project: data validation, feature engineering, "
            "model training with reproducible seeds, evaluation gates, and "
            "packaging the final artifact so it can be served behind an API.\n\n"
            "The biggest lesson: treat your pipeline like software, not a script. "
            "Version your data, log your experiments, and write tests for your "
            "preprocessing code just like you would for any other function."
        ),
        "cover_image": "mllifecycle.png",
        "tags": "machine-learning,mlops,python",
    },
    {
        "slug": "why-i-switched-to-fastapi",
        "title": "Why I Reach for FastAPI for New Backend Projects",
        "summary": "Async support, automatic docs, and type-driven validation make FastAPI my default choice.",
        "content": (
            "For a long time Flask was my default framework for every backend. "
            "It's still a great tool, but for new API-first projects I now reach "
            "for FastAPI more often. The combination of Pydantic-based validation, "
            "automatic OpenAPI documentation, and native async support removes a "
            "lot of boilerplate I used to write by hand.\n\n"
            "That said, for content-heavy, server-rendered sites like this "
            "portfolio, Flask's simplicity and mature templating still win."
        ),
        "cover_image": "patterns_of_python.png",
        "tags": "backend,fastapi,flask",
    },
    {
        "slug": "handling-imbalanced-datasets",
        "title": "Practical Techniques for Handling Imbalanced Datasets",
        "summary": "Resampling, class weights, and the metrics that actually matter for skewed classification problems.",
        "content": (
            "Fraud detection, medical diagnosis, churn prediction — a huge share "
            "of real-world classification problems come with heavily imbalanced "
            "classes. Accuracy stops being a useful metric the moment your "
            "positive class is 2% of the data.\n\n"
            "In this post I cover the techniques I reach for most: class-weighted "
            "loss functions, SMOTE-style oversampling, and why precision/recall "
            "and the ROC/PR curves tell a much more honest story than a single "
            "accuracy number."
        ),
        "cover_image": "imbalance datasets.jpg",
        "tags": "machine-learning,data-science",
    },
]


def init_db():
    """Create tables if they do not exist yet and seed sample content once."""
    conn = get_connection()
    with conn:
        conn.executescript(SCHEMA)

        existing = conn.execute("SELECT COUNT(*) AS c FROM blog_posts").fetchone()["c"]
        if existing == 0:
            now = datetime.now(timezone.utc).isoformat()
            for post in SEED_POSTS:
                conn.execute(
                    """INSERT INTO blog_posts
                       (slug, title, summary, content, cover_image, tags, author, published_at, views)
                       VALUES (?, ?, ?, ?, ?, ?, 'Ravi Der', ?, 0)""",
                    (
                        post["slug"], post["title"], post["summary"], post["content"],
                        post["cover_image"], post["tags"], now,
                    ),
                )
    conn.close()


def now_iso():
    return datetime.now(timezone.utc).isoformat()
