"""
learning_data.py — Single source of truth for "My Learning" card metadata.

Mirrors projects_data.py exactly: learning items live in the SQLite
`admin_learning` table (managed through the /admin dashboard), NOT as
hardcoded HTML. This module is the bridge between that database and the
public /my_learning page so every add/edit/delete/reorder from the admin
panel shows up immediately — no restart, no redeploy.

DEFAULT_LEARNING below is only a one-time SEED: the first time the app
runs and the admin_learning table is empty, these are inserted so the
existing learning cards show up immediately and are editable from the
dashboard. After that, the database is the only source of truth.
"""

from app.admin import admin_db

# category -> (icon class, display label). Used both for the little
# tag pill icon and the image-load-failure placeholder icon on each card.
CATEGORY_ICONS = {
    "ai-ml": ("fas fa-database", "AI/ML"),
    "python": ("fab fa-python", "Python"),
    "mysql": ("fas fa-database", "MySQL"),
    "statistics": ("fab fa-python", "Statistics"),
    "machine-learning": ("fab fa-python", "Machine Learning"),
    "maths-ml": ("fas fa-chart-simple", "Maths-ML"),
    "generative-ai": ("fas fa-robot", "Generative AI"),
    "cloud-devops": ("fas fa-cloud-upload-alt", "Cloud/DevOps"),
    "data-visualization": ("fas fa-chart-line", "Data Visualization"),
    "other": ("fas fa-graduation-cap", "Other"),
}

CATEGORY_LABELS = {key: label for key, (_, label) in CATEGORY_ICONS.items()}

DEFAULT_LEARNING = [
    {
        "slug": "feature-engineering",
        "title": "Feature Engineering",
        "category": "ai-ml",
        "tags": ["AI/ML"],
        "description": "Create meaningful features, remove irrelevant ones, and identify the most important variables to improve data quality and model learning.",
        "full_text": "Well-engineered features help increase accuracy, reduce overfitting, speed up training, and make Machine Learning models more reliable. Feature Engineering transforms raw data into valuable insights, enabling models to deliver better predictions and real-world business value.",
        "image_url": "https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/feture_engineering.png",
        "link_url": "https://www.linkedin.com/posts/ravi-der_machinelearning-artificialintelligence-featureengineering-activity-7478431826966147072-yAgT?utm_source=share&utm_medium=member_desktop&rcm=ACoAAE-fhkcB96hONfHtYNilNy2eN4jm8f6hO9A",
        "link_type": "linkedin",
    },
    {
        "slug": "ml-for-business",
        "title": "Business First in ML",
        "category": "ai-ml",
        "tags": ["AI/ML"],
        "description": "Start by understanding the business problem, project goals, and available data before selecting any Machine Learning algorithm.",
        "full_text": "Analyze the dataset, identify the right features and target variable, then choose the model that best fits the problem—not just the one with the highest accuracy. The true success of a Machine Learning project lies in delivering business value by solving real-world problems with meaningful and reliable predictions.",
        "image_url": "https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/buisness_before_ml.png",
        "link_url": "https://www.linkedin.com/posts/ravi-der_machinelearning-artificialintelligence-datascience-activity-7477341417254764544-Hwg_?utm_source=share&utm_medium=member_desktop&rcm=ACoAAE-fhkcB96hONfHtYNilNy2eN4jm8f6hO9A",
        "link_type": "linkedin",
    },
    {
        "slug": "ml-lifecycle",
        "title": "ML Lifecycle",
        "category": "mysql",
        "tags": ["MySQL"],
        "description": "Define the problem, collect quality data, and use EDA to transform raw data into actionable insights.",
        "full_text": "Prepare the data, build and compare multiple Machine Learning models, and select the best one using proper evaluation metrics. Fine-tune, deploy, and monitor the model to ensure accurate, scalable, and reliable real-world predictions.",
        "image_url": "https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/mllifecycle.png",
        "link_url": "https://www.linkedin.com/posts/ravi-der_machinelearning-datascience-artificialintelligence-activity-7475394975451660288-GsEm?utm_source=share&utm_medium=member_desktop&rcm=ACoAAE-fhkcB96hONfHtYNilNy2eN4jm8f6hO9A",
        "link_type": "linkedin",
    },
    {
        "slug": "window-functions",
        "title": "Window Functions",
        "category": "mysql",
        "tags": ["MySQL"],
        "description": "Window Functions in MySQL make data analysis more powerful by allowing calculations like ranking, running totals, and row comparisons without losing original rows.",
        "full_text": "They are widely used in dashboards, reports, and business analysis to solve complex problems with cleaner and smarter SQL queries. Examples: ROW_NUMBER(), RANK(), SUM() OVER() etc. Highly efficient for analytical queries and performance optimization.",
        "image_url": "https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/Windows_function.jpg",
        "link_url": "https://www.linkedin.com/posts/ravi-der_mysql-sql-windowfunctions-activity-7458827166093393920-cRa4?utm_source=share&utm_medium=member_desktop",
        "link_type": "linkedin",
    },
    {
        "slug": "hypothesis-testing",
        "title": "Hypothesis Testing",
        "category": "statistics",
        "tags": ["Statistics"],
        "description": "Hypothesis Testing is a statistical technique used to check whether an assumption is true or false using real data.",
        "full_text": "It helps us make decisions based on evidence instead of guesswork. By analyzing sample data and calculating probability (p-value), we decide whether to accept or reject the assumption. It is widely used in Machine Learning, Business Analytics, Healthcare, and A/B Testing. Core concepts: Null vs Alternate hypothesis, significance level, p-value interpretation.",
        "image_url": "https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/hypothesis%20testing.jpg",
        "link_url": "https://www.linkedin.com/posts/ravi-der_datascience-machinelearning-artificialintelligence-activity-7454391165308751872-Pgq8?utm_source=share&utm_medium=member_desktop&rcm=ACoAAE-fhkcB96hONfHtYNilNy2eN4jm8f6hO9A",
        "link_type": "linkedin",
    },
    {
        "slug": "imbalanced-data-ml",
        "title": "Imbalanced Data in ML",
        "category": "machine-learning",
        "tags": ["Machine Learning"],
        "description": "In machine learning, not all classes have equal data distribution.",
        "full_text": "When one class has significantly more samples than another, it creates an imbalanced dataset. This can make models biased toward the majority class and reduce performance on important minority cases like fraud detection or disease prediction. Techniques: resampling (SMOTE), class weights, anomaly detection frameworks, and ensemble methods.",
        "image_url": "https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/imbalance%20datasets.jpg",
        "link_url": "https://www.linkedin.com/posts/ravi-der_machinelearning-datascience-artificialintelligence-activity-7452603451261460480-H9H_?utm_source=share&utm_medium=member_desktop",
        "link_type": "linkedin",
    },
    {
        "slug": "precision-vs-recall",
        "title": "Precision vs Recall",
        "category": "maths-ml",
        "tags": ["Maths-ML"],
        "description": "Precision → Measures how many predicted positive cases are actually correct.",
        "full_text": "Recall → Measures how many actual positive cases the model successfully identifies. Balance Matters → A good ML model often needs the right balance between Precision and Recall depending on the problem (F1 Score, PR curve). High precision = low false positives; high recall = low false negatives.",
        "image_url": "https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/precision%20vs%20recall.jpg",
        "link_url": "https://www.linkedin.com/posts/ravi-der_machinelearning-artificialintelligence-ai-activity-7452229914386259968-dkOj?utm_source=share&utm_medium=member_desktop&rcm=ACoAAE-fhkcB96hONfHtYNilNy2eN4jm8f6hO9A",
        "link_type": "linkedin",
    },
    {
        "slug": "cheat-sheets-pandas-numpy-matplotlib",
        "title": "Cheat Sheets",
        "category": "python",
        "tags": ["Pandas", "NumPy", "Matplotlib"],
        "description": "I created these cheat sheets to serve as a quick-reference resource for Data Science learners.",
        "full_text": "My goal is to make commonly used concepts, functions, and visualizations easier to understand and revise. Feel free to explore, use, and share them with others in the community.",
        "image_url": "https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/cheet_sheet_pandas_numpy_matplotlib.png",
        "link_url": "https://www.linkedin.com/posts/ravi-der_github-derravi-python-data-science-cheat-sheets-basics-of-pandas-numpy-matplotlib-activity-7369035981334683650-jkVz?utm_source=share&utm_medium=member_desktop&rcm=ACoAAE-fhkcB96hONfHtYNilNy2eN4jm8f6hO9A",
        "link_type": "linkedin",
    },
    {
        "slug": "star-patterns-python",
        "title": "Star Patterns Collection",
        "category": "python",
        "tags": ["Python"],
        "description": "A curated collection of Python patterns, from basic to advanced, designed to help beginners and learners improve coding skills,",
        "full_text": "understand programming concepts, and enhance problem-solving abilities. A practical resource for mastering Python step by step.",
        "image_url": "https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/patterns_of_python.png",
        "link_url": "https://github.com/derravi/Creative_Python_Pattern_Printing_Collection",
        "link_type": "github",
    },
    {
        "slug": "prompt-engineering-llm-apps",
        "title": "Prompt Engineering & LLM Apps",
        "category": "generative-ai",
        "tags": ["Generative AI"],
        "description": "Built intelligent assistants using OpenAI, LangChain, vector databases, and RAG pipelines.",
        "full_text": "Developed Q&A chatbot over custom documents using ChromaDB, semantic search, and agent-based workflows. Implemented retrieval-augmented generation (RAG) for domain-specific knowledge. Explored chain-of-thought prompting and fine-tuning LLMs for specialized tasks.",
        "image_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&h=400&fit=crop",
        "link_url": "#",
        "link_type": "linkedin",
    },
    {
        "slug": "aws-devops-essentials",
        "title": "AWS & DevOps Essentials",
        "category": "cloud-devops",
        "tags": ["Cloud/DevOps"],
        "description": "Hands-on with EC2, S3, Lambda, CI/CD pipelines, and infrastructure as code (Terraform).",
        "full_text": "Deployed serverless apps using Lambda + API Gateway, automated with GitHub Actions, managed ECS, Terraform provisioning. Configured monitoring with CloudWatch, optimized cost and performance. Built end-to-end deployment pipelines for containerized apps.",
        "image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&h=400&fit=crop",
        "link_url": "#",
        "link_type": "linkedin",
    },
    {
        "slug": "dashboard-design-storytelling",
        "title": "Dashboard Design & Storytelling",
        "category": "data-visualization",
        "tags": ["Data Visualization"],
        "description": "Mastered Tableau, Power BI, and advanced matplotlib/seaborn for interactive dashboards.",
        "full_text": "Built executive dashboards uncovering sales insights, KPI tracking, real-time data integration, and predictive analytics views. Storytelling with data, creating compelling narratives that drive business decisions. Advanced DAX and calculated fields.",
        "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&h=400&fit=crop",
        "link_url": "#",
        "link_type": "linkedin",
    },
]


def _row_to_learning_item(row):
    """Normalize a DB row (dict) into the shape the template expects."""
    tags = row.get("tags") or []
    if isinstance(tags, str):
        try:
            import json
            tags = json.loads(tags)
        except Exception:
            tags = []
    category = row.get("category") or "other"
    icon, default_label = CATEGORY_ICONS.get(category, CATEGORY_ICONS["other"])
    return {
        "id": row.get("id"),
        "slug": row.get("slug"),
        "title": row.get("title"),
        "category": category,
        "category_label": default_label,
        "icon": icon,
        "tags": tags or [default_label],
        "description": row.get("description") or "",
        "full_text": row.get("full_text") or "",
        "image_url": row.get("image_url") or "",
        "link_url": row.get("link_url") or "#",
        "link_type": row.get("link_type") or "linkedin",
        "status": row.get("status") or "published",
        "featured": bool(row.get("featured")),
        "view_count": row.get("view_count") or 0,
    }


def ensure_seeded():
    """Make sure the admin_learning table exists and, the very first time,
    is pre-filled with the portfolio's existing learning cards. Safe to call
    on every app startup — it only inserts seed data when the table is empty."""
    admin_db.init_admin_tables()
    existing = admin_db.get_all_learning_items()
    if existing:
        return
    for item in DEFAULT_LEARNING:
        admin_db.create_learning_item(
            slug=item["slug"],
            title=item["title"],
            description=item.get("description", ""),
            full_text=item.get("full_text", ""),
            category=item["category"],
            tags=item.get("tags", []),
            image_url=item.get("image_url", ""),
            link_url=item.get("link_url", "#"),
            link_type=item.get("link_type", "linkedin"),
            status="published",
            featured=item.get("featured", False),
        )


def get_learning_items(published_only=True):
    """Fresh list of learning items straight from the database (live —
    reflects any admin add/edit/delete immediately, no caching)."""
    status = "published" if published_only else "all"
    rows = admin_db.get_all_learning_items(status=status)
    return [_row_to_learning_item(r) for r in rows]


def get_learning_item(slug):
    """Look up a single learning item by slug (checked against ALL statuses
    so admin preview links to drafts still work)."""
    row = admin_db.get_learning_item_by_slug(slug)
    return _row_to_learning_item(row) if row else None
