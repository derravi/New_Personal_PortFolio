"""
projects_data.py — Single source of truth for project metadata.

The project cards themselves stay hand-written in templates/projects.html
(so the existing hand-tuned design/markup is untouched), but this list gives
the backend (REST API, ratings, recommendations, sitemap, PDF export) a
slug + category + tags to work with, matching the data-project-id /
data-category attributes added to each card.
"""

PROJECTS = [
    {
        "slug": "object-detection-distance-estimation",
        "title": "AI-Powered Real-Time Object Detection and Distance Estimation System",
        "category": "ai-ml",
        "tags": ["python", "opencv", "numpy", "yolo", "computer-vision"],
        "github": "https://github.com/derravi/AI-Powered-Real-Time-Object-Detection-and-Distance-Estimation-System-",
    },
    {
        "slug": "kisan-sathi-farmer-assistant",
        "title": "AI Powerful Farmer Assistant",
        "category": "ai-ml",
        "tags": ["python", "gemini", "genai"],
        "github": "https://github.com/derravi/AI-Powerfull-Farmer-Assistant",
    },
    {
        "slug": "credit-card-fraud-detection",
        "title": "Credit Card Fraud Detection",
        "category": "ai-ml",
        "tags": ["python", "scikit-learn", "knn", "decision-tree"],
        "github": "https://github.com/derravi/Credit_Card_Fraud_Detection_using_KNN_-_Decision_Tree",
    },
    {
        "slug": "diabetes-prediction-system",
        "title": "Diabetes Prediction System",
        "category": "ai-ml",
        "tags": ["python", "scikit-learn", "logistic-regression"],
        "github": "#",
    },
    {
        "slug": "student-success-prediction",
        "title": "Student Success Prediction",
        "category": "ai-ml",
        "tags": ["python", "scikit-learn", "logistic-regression"],
        "github": "#",
    },
    {
        "slug": "student-exam-score-prediction",
        "title": "Student Exam Score Prediction",
        "category": "ai-ml",
        "tags": ["python", "scikit-learn", "linear-regression"],
        "github": "#",
    },
    {
        "slug": "house-price-prediction",
        "title": "House Price Prediction",
        "category": "ai-ml",
        "tags": ["python", "scikit-learn", "linear-regression"],
        "github": "#",
    },
    {
        "slug": "pca-loan-dataset",
        "title": "PCA Analysis on Loan Dataset",
        "category": "data-analysis",
        "tags": ["python", "scikit-learn", "pca"],
        "github": "#",
    },
    {
        "slug": "weather-insight-ml",
        "title": "Weather Insight: AI/ML Powered Weather Prediction and Analysis",
        "category": "ai-ml",
        "tags": ["python", "scikit-learn", "weather"],
        "github": "#",
    },
    {
        "slug": "covid19-analytics-dashboard",
        "title": "COVID-19 Data Analytics Dashboard",
        "category": "data-analysis",
        "tags": ["python", "pandas", "numpy", "matplotlib"],
        "github": "#",
    },
    {
        "slug": "air-quality-prediction",
        "title": "AI Powered Air Quality Prediction – Monitoring System",
        "category": "ai-ml",
        "tags": ["python", "knn"],
        "github": "#",
    },
    {
        "slug": "blinkit-sales-analysis",
        "title": "Blinkit Sales Data Analysis – Visualization",
        "category": "data-analysis",
        "tags": ["python", "pandas", "numpy", "matplotlib"],
        "github": "#",
    },
    {
        "slug": "netflix-data-visualization",
        "title": "Netflix Data Cleaning & Visualization",
        "category": "data-analysis",
        "tags": ["python", "pandas", "numpy", "matplotlib"],
        "github": "#",
    },
    {
        "slug": "live-weather-django",
        "title": "Live Weather Website using Django",
        "category": "web-dev",
        "tags": ["python", "django", "weather-api"],
        "github": "#",
    },
    {
        "slug": "todo-list-django",
        "title": "Todo List",
        "category": "web-dev",
        "tags": ["python", "html", "css"],
        "github": "#",
    },
    {
        "slug": "qr-code-generator",
        "title": "QR Code Generator",
        "category": "web-dev",
        "tags": ["python", "django", "qrcode"],
        "github": "#",
    },
    {
        "slug": "password-generator-django",
        "title": "Password Generator",
        "category": "web-dev",
        "tags": ["python", "django"],
        "github": "#",
    },
    {
        "slug": "age-calculator-python",
        "title": "Age Calculator using Python",
        "category": "python-tools",
        "tags": ["python"],
        "github": "#",
    },
]

PROJECTS_BY_SLUG = {p["slug"]: p for p in PROJECTS}

CATEGORY_LABELS = {
    "ai-ml": "AI / Machine Learning",
    "data-analysis": "Data Analysis",
    "web-dev": "Web Development",
    "python-tools": "Python Tools",
}


def get_related(slug, limit=3):
    """Very lightweight content-based recommendation: rank other projects
    by tag overlap (Jaccard-style) with the given project. This is a simple
    heuristic, not a trained ML model — good enough for 'related projects'
    on a portfolio site without pulling in scikit-learn just for this."""
    base = PROJECTS_BY_SLUG.get(slug)
    if not base:
        return []
    base_tags = set(base["tags"])
    scored = []
    for p in PROJECTS:
        if p["slug"] == slug:
            continue
        overlap = len(base_tags & set(p["tags"]))
        same_category = 1 if p["category"] == base["category"] else 0
        score = overlap * 2 + same_category
        if score > 0:
            scored.append((score, p))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:limit]]
