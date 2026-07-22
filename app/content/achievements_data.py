"""
achievements_data.py — Single source of truth for "Achievements &
Certifications" card metadata.

Mirrors projects_data.py / learning_data.py exactly: achievements live in
the SQLite `admin_achievements` table (managed through the /admin
dashboard), NOT as hardcoded HTML. This module is the bridge between that
database and the public /achievements page so every add/edit/delete/
reorder from the admin panel shows up immediately — no restart, no
redeploy.

DEFAULT_ACHIEVEMENTS below is only a one-time SEED: the first time the app
runs and the admin_achievements table is empty, these are inserted so the
existing achievement cards show up immediately and are editable from the
dashboard. After that, the database is the only source of truth.
"""

from app.admin import admin_db

# category -> display label used for the section/group heading on the
# public page (cards are grouped under these headings, in this order).
CATEGORY_LABELS = {
    "internship": "Internship",
    "certification": "Certifications",
    "bootcamp": "Bootcamps",
    "event": "Events",
    "award": "Awards",
    "other": "Other",
}

CATEGORY_ORDER = ["internship", "certification", "bootcamp", "event", "award", "other"]

DEFAULT_ACHIEVEMENTS = [
    {
        "slug": "ibm-csrbox-ai-intern",
        "title": "IBM CSRBOX",
        "issuer": "AI Intern",
        "category": "internship",
        "achievement_type": "Internship",
        "icon": "fas fa-graduation-cap",
        "date_label": "July - 2025",
        "description": "I Am completed 5 Week of the internship From the IMB as a AI Intern.",
        "skills": ["Python", "AI Agent(Basics)", "Multi Agent(Basics)"],
        "certificate_url": "https://github.com/derravi/demo/blob/main/IBM%20CSRBOX%20Ai%20Intern%20Internship%20Certifictes.jpg?raw=true",
    },
    {
        "slug": "imbuesoft-llp-python-developer",
        "title": "Imbuesoft LLP",
        "issuer": "Python Developer",
        "category": "internship",
        "achievement_type": "Internship",
        "icon": "fas fa-graduation-cap",
        "date_label": "June - 2025",
        "description": "I Am completed 6 Moth of the internship as a Python Developer.",
        "skills": ["Python", "RAG", "Web Scraping"],
        "certificate_url": "https://github.com/derravi/demo/blob/main/Imbuesoft%20LLP%20Internship%202025.jpg?raw=true",
    },
    {
        "slug": "bharat-intern-web-developer",
        "title": "Bharat Intern",
        "issuer": "Web Developer",
        "category": "internship",
        "achievement_type": "Internship",
        "icon": "fas fa-graduation-cap",
        "date_label": "Dec - 2023",
        "description": "I Am completed 1 Moth of the internship from the Bharat intern as a Web Developer.",
        "skills": ["HTML", "CSS"],
        "certificate_url": "https://github.com/derravi/demo/blob/main/Bharat%20Intern%202023.jpg?raw=true",
    },
    {
        "slug": "data-science-bootcamp-codingwise",
        "title": "Data Science Bootcamp",
        "issuer": "CodingWise",
        "category": "internship",
        "achievement_type": "Data Science Bootcamp",
        "icon": "fas fa-award",
        "date_label": "Aug - 2025",
        "description": "AProudly completed the 5-Day Python for Data Science Bootcamp by CodingWise, gaining hands-on experience in Python, NumPy, and Pandas to strengthen my foundation in Data Science and AI.",
        "skills": ["React", "UI/UX", "Innovation"],
        "certificate_url": "#",
    },
    {
        "slug": "introduction-to-python-infosys",
        "title": "Introduction To Python",
        "issuer": "Infosys Springboard",
        "category": "certification",
        "achievement_type": "Certification",
        "icon": "fas fa-certificate",
        "date_label": "Mar - 2025",
        "description": "Successfully completed the 24-hour Advanced Python course from Infosys Springboard, enhancing my skills in writing efficient, scalable Python applications through hands-on coding and real-world problem-solving.",
        "skills": ["Python"],
        "certificate_url": "https://github.com/derravi/demo/blob/main/Infosys%20Springbord%20Introduction%20to%20python%20march%202025.jpg?raw=true",
    },
    {
        "slug": "basics-of-python-infosys",
        "title": "Basics of Python",
        "issuer": "Infosys Springboard",
        "category": "certification",
        "achievement_type": "Certification",
        "icon": "fas fa-certificate",
        "date_label": "Feb - 2025",
        "description": "Successfully completed the Basic Python Course on Infosys Springboard, building a strong foundation in Python fundamentals, programming concepts, and data handling techniques.",
        "skills": ["Basic Python"],
        "certificate_url": "https://github.com/derravi/demo/blob/main/Infosys%20Spring%20bord%20Basics%20of%20python%20february%202025.jpg?raw=true",
    },
    {
        "slug": "introduction-to-mysql-infosys",
        "title": "Introduction To MySQL",
        "issuer": "Infosys Springboard",
        "category": "certification",
        "achievement_type": "Certification",
        "icon": "fas fa-certificate",
        "date_label": "Apr - 2025",
        "description": 'Successfully completed the "Introduction to MySQL" course from Infosys Springboard, gaining hands-on knowledge of SQL queries, joins, and real-world database operations.',
        "skills": ["MySQL"],
        "certificate_url": "https://github.com/derravi/demo/blob/main/Infosys%20Spring%20bord%20Basics%20of%20python%20february%202025.jpg?raw=true",
    },
    {
        "slug": "machine-learning-aws",
        "title": "Machine Learning",
        "issuer": "AWS ML Certificate",
        "category": "certification",
        "achievement_type": "Certification",
        "icon": "fas fa-code",
        "date_label": "Jan - 2024",
        "description": "Successfully completed the AWS Academy Machine Learning Foundation Course, gaining essential knowledge in ML concepts and earning my AWS certification.",
        "skills": ["Basics of ML"],
        "certificate_url": "https://github.com/derravi/demo/blob/main/AWS%20Machine%20learning%202024.jpg?raw=true",
    },
    {
        "slug": "abhigyan-event-atmiya",
        "title": "Abhigyan Event",
        "issuer": "Atmiya University",
        "category": "certification",
        "achievement_type": "Certification",
        "icon": "fas fa-code",
        "date_label": "Feb - 2023",
        "description": "Excited to have volunteered at a 3 days of event, contributing to a meaningful cause and looking forward to more opportunities to make a positive impact",
        "skills": ["Leadership", "Time Management"],
        "certificate_url": "https://github.com/derravi/demo/blob/main/Abhigyan%20event%202023.jpg?raw=true",
    },
    {
        "slug": "design-thinking-atmiya",
        "title": "Design Thinking",
        "issuer": "Atmiya University",
        "category": "certification",
        "achievement_type": "Certification",
        "icon": "fas fa-shield-alt",
        "date_label": "June - 2022",
        "description": "Successfully completed the Design Thinking Course and earned my certificate, enhancing my creative problem-solving and innovation skills!",
        "skills": ["Problem Solving", "Imagination"],
        "certificate_url": "https://github.com/derravi/demo/blob/main/SDG%20Course%202021%20.jpg?raw=true",
    },
]


def _row_to_achievement(row):
    """Normalize a DB row (dict) into the shape the template expects."""
    skills = row.get("skills") or []
    if isinstance(skills, str):
        try:
            import json
            skills = json.loads(skills)
        except Exception:
            skills = []
    category = row.get("category") or "other"
    return {
        "id": row.get("id"),
        "slug": row.get("slug"),
        "title": row.get("title"),
        "issuer": row.get("issuer") or "",
        "category": category,
        "category_label": CATEGORY_LABELS.get(category, "Other"),
        "achievement_type": row.get("achievement_type") or CATEGORY_LABELS.get(category, ""),
        "icon": row.get("icon") or "fas fa-trophy",
        "date_label": row.get("date_label") or "",
        "description": row.get("description") or "",
        "skills": skills,
        "certificate_url": row.get("certificate_url") or "#",
        "status": row.get("status") or "published",
        "featured": bool(row.get("featured")),
        "view_count": row.get("view_count") or 0,
    }


def ensure_seeded():
    """Make sure the admin_achievements table exists and, the very first
    time, is pre-filled with the portfolio's existing achievement cards.
    Safe to call on every app startup — it only inserts seed data when the
    table is empty."""
    admin_db.init_admin_tables()
    existing = admin_db.get_all_achievements()
    if existing:
        return
    for item in DEFAULT_ACHIEVEMENTS:
        admin_db.create_achievement(
            slug=item["slug"],
            title=item["title"],
            issuer=item.get("issuer", ""),
            description=item.get("description", ""),
            category=item["category"],
            achievement_type=item.get("achievement_type", ""),
            icon=item.get("icon", "fas fa-trophy"),
            date_label=item.get("date_label", ""),
            skills=item.get("skills", []),
            certificate_url=item.get("certificate_url", "#"),
            status="published",
            featured=item.get("featured", False),
        )


def get_achievements(published_only=True):
    """Fresh list of achievements straight from the database (live —
    reflects any admin add/edit/delete immediately, no caching)."""
    status = "published" if published_only else "all"
    rows = admin_db.get_all_achievements(status=status)
    return [_row_to_achievement(r) for r in rows]


def get_achievements_grouped(published_only=True):
    """Achievements grouped by category, in CATEGORY_ORDER, for rendering
    under section headings on the public page. Categories with no items
    are omitted."""
    items = get_achievements(published_only)
    grouped = {}
    for item in items:
        grouped.setdefault(item["category"], []).append(item)

    ordered = []
    for cat in CATEGORY_ORDER:
        if cat in grouped:
            ordered.append({
                "category": cat,
                "label": CATEGORY_LABELS.get(cat, cat.title()),
                "achievements": grouped[cat],
            })
    # Any category not in the known order (custom values) still shows up
    for cat, cat_items in grouped.items():
        if cat not in CATEGORY_ORDER:
            ordered.append({
                "category": cat,
                "label": CATEGORY_LABELS.get(cat, cat.title()),
                "achievements": cat_items,
            })
    return ordered


def get_achievement(slug):
    """Look up a single achievement by slug (checked against ALL statuses
    so admin preview links to drafts still work)."""
    row = admin_db.get_achievement_by_slug(slug)
    return _row_to_achievement(row) if row else None
