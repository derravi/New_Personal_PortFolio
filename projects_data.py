"""
projects_data.py — Single source of truth for project metadata.

Projects now live in the SQLite `admin_projects` table (managed through the
/admin dashboard), NOT as a hardcoded Python list. This module is the bridge
between that database and the rest of the app (public /projects page, REST
API, sitemap, PDF/DOCX resume export, recommendations, etc.) so every one of
those places automatically reflects whatever you add/edit/delete from the
admin panel — no restart, no redeploy.

DEFAULT_PROJECTS below is only a one-time SEED: the first time the app runs
and the admin_projects table is empty, these are inserted so your existing
18 projects show up immediately and are editable from the dashboard. After
that, the database is the only source of truth.
"""

import admin_db

CATEGORY_LABELS = {
    "ai-ml": "AI / Machine Learning",
    "data-analysis": "Data Analysis",
    "web-dev": "Web Development",
    "python-tools": "Python Tools",
    "mobile-app": "Mobile App",
    "other": "Other",
}

DEFAULT_PROJECTS = [
    {
        "slug": 'object-detection-distance-estimation',
        "title": 'AI-Powered Real-Time Object Detection and Distance Estimation System',
        "category": 'ai-ml',
        "tags": ['python', 'opencv', 'numpy', 'yolo', 'computer-vision'],
        "description": 'AI-powered real-time object detection using YOLOv8 for multi-object tracking with unique IDs and distance estimation — GPU-optimized for surveillance, robotics, and autonomous systems.',
        "image_url": 'https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/Object%20Detection%20Projects.png',
        "github_url": 'https://github.com/derravi/AI-Powered-Real-Time-Object-Detection-and-Distance-Estimation-System-',
    },
    {
        "slug": 'kisan-sathi-farmer-assistant',
        "title": 'AI Powerful Farmer Assistant',
        "category": 'ai-ml',
        "tags": ['python', 'gemini', 'genai'],
        "description": 'Kisan Saathi AI is a smart farming assistant providing weather updates, crop prices, schemes, and market access in multiple Indian languages using Google Gemini AI.',
        "image_url": 'https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/Kisan%20Sathi%20Image.png',
        "github_url": 'https://github.com/derravi/AI-Powerfull-Farmer-Assistant',
    },
    {
        "slug": 'credit-card-fraud-detection',
        "title": 'Credit Card Fraud Detection',
        "category": 'ai-ml',
        "tags": ['python', 'scikit-learn', 'knn', 'decision-tree'],
        "description": 'A credit card fraud detection project using K-Nearest Neighbors and Decision Tree classifiers. Covers data preprocessing, feature scaling, performance evaluation (confusion matrix, ROC curve), and a user input system to predict whether a transaction is fraudulent or genuine.',
        "image_url": 'https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/AI-Powered%20Credit%20Card%20Fraud%20Detection%20System.jpg',
        "github_url": 'https://github.com/derravi/Credit_Card_Fraud_Detection_using_KNN_-_Decision_Tree',
    },
    {
        "slug": 'diabetes-prediction-system',
        "title": 'Diabetes Prediction System',
        "category": 'ai-ml',
        "tags": ['python', 'scikit-learn', 'logistic-regression'],
        "description": 'A Machine Learning project that predicts diabetes risk using Logistic Regression. The system preprocesses data, trains a model on the Pima Indians Diabetes Dataset, evaluates performance, and allows users to input health metrics for prediction. Includes visual analysis & heatmaps.',
        "image_url": 'https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/Diabetes_prediction_system_using_logistic_regression.jpg',
        "github_url": 'https://github.com/derravi/Diabetes_Prediction_System_using_Logistic_Regression',
    },
    {
        "slug": 'student-success-prediction',
        "title": 'Student Success Prediction',
        "category": 'ai-ml',
        "tags": ['python', 'scikit-learn', 'logistic-regression'],
        "description": 'A machine learning project using Logistic Regression to predict student success (Pass/Fail) based on academic and behavioral features with data preprocessing, visualization, and interactive prediction.',
        "image_url": 'https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/Student_prediction.png',
        "github_url": 'https://github.com/derravi/Student_Success_Prediction',
    },
    {
        "slug": 'student-exam-score-prediction',
        "title": 'Student Exam Score Prediction',
        "category": 'ai-ml',
        "tags": ['python', 'scikit-learn', 'linear-regression'],
        "description": "Predicts students' final exam scores using linear regression based on factors like study hours, attendance, and past performance. Includes error metrics (MAE, MSE, RMSE, R²) and visualizations (histogram, scatter plot) to analyze the model's accuracy.",
        "image_url": 'https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/Student%20Exam%20Score%20Prediction.jpg',
        "github_url": 'https://github.com/derravi/Student-Exam-Score-Prediction-using-Linear-Regression',
    },
    {
        "slug": 'house-price-prediction',
        "title": 'House Price Prediction',
        "category": 'ai-ml',
        "tags": ['python', 'scikit-learn', 'linear-regression'],
        "description": 'A machine learning project that predicts house prices based on area, bedrooms, bathrooms, floors, and year built using Linear Regression. Includes model evaluation metrics, data visualization, and interactive price prediction.',
        "image_url": 'https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/House%20Price%20Prediction%20using%20Linear%20Regression.jpg',
        "github_url": 'https://github.com/derravi/House_Price_Prediction_using_Linear_Regression',
    },
    {
        "slug": 'pca-loan-dataset',
        "title": 'PCA Analysis on Loan Dataset',
        "category": 'data-analysis',
        "tags": ['python', 'scikit-learn', 'pca'],
        "description": 'This project performs data preprocessing, handles missing values, standardizes features, and applies Principal Component Analysis (PCA) on a loan dataset. It visualizes variance explained by components and scatter plots to explore dimensionality reduction and feature importance.',
        "image_url": 'https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/Principal%20Component%20Analysis%20%28PCA%29%20project%20on%20a%20loan%20dataset.jpg',
        "github_url": 'https://github.com/derravi/PCA_Analysis_on_Loan_Dataset',
    },
    {
        "slug": 'weather-insight-ml',
        "title": 'Weather Insight: AI/ML Powered Weather Prediction and Analysis',
        "category": 'ai-ml',
        "tags": ['python', 'scikit-learn', 'weather'],
        "description": 'ClimaCast: AI-Powered Weather Forecasting using Machine Learning',
        "image_url": 'https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/Weither%20Insights%20ML%20Ai.jpg',
        "github_url": 'https://github.com/derravi/Weather_Insight_ML-AI_Powered_Weather_Prediction_and_Analysis',
    },
    {
        "slug": 'covid19-analytics-dashboard',
        "title": 'COVID-19 Data Analytics Dashboard',
        "category": 'data-analysis',
        "tags": ['python', 'pandas', 'numpy', 'matplotlib'],
        "description": 'A Python-based COVID-19 Data Analytics Dashboard using Pandas, Matplotlib, and Seaborn. It visualizes global and country-level trends with line charts, pie charts, and bubble plots, providing insights on daily cases, deaths, regional distribution, and top affected countries.',
        "image_url": 'https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/COVID-19%20Data%20Analytics%20Dashboard.png',
        "github_url": 'https://github.com/derravi/COVID-19_Data_Analytics_Dashboard',
    },
    {
        "slug": 'air-quality-prediction',
        "title": 'AI Powered Air Quality Prediction – Monitoring System',
        "category": 'ai-ml',
        "tags": ['python', 'knn'],
        "description": 'To predict Air Quality Index (AQI) and classify the Air Pollution Level (Good, Moderate, Poor, etc.) using real-world environmental data.',
        "image_url": 'https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/Air%20Polution%20KNN%20Model.png',
        "github_url": 'https://github.com/derravi/AI_Powered_Air_Quality_Prediction_-_Monitoring_System',
    },
    {
        "slug": 'blinkit-sales-analysis',
        "title": 'Blinkit Sales Data Analysis – Visualization',
        "category": 'data-analysis',
        "tags": ['python', 'pandas', 'numpy', 'matplotlib'],
        "description": 'Data analysis project on Blinkit sales dataset. Includes data cleaning, handling missing values, outlier removal, and creating interactive visualizations with Matplotlib & Seaborn. Explores sales patterns by item type, MRP, outlet size, and establishment year for insights.',
        "image_url": 'https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/Blinkit%20Sales%20Data%20Analysis%20Project.png',
        "github_url": 'https://github.com/derravi/Blinkit_Sales_Data_Analysis_-_Visualization',
    },
    {
        "slug": 'netflix-data-visualization',
        "title": 'Netflix Data Cleaning & Visualization',
        "category": 'data-analysis',
        "tags": ['python', 'pandas', 'numpy', 'matplotlib'],
        "description": 'Netflix Data Cleaning & Visualization project using Python (Pandas, NumPy, Matplotlib, Seaborn). Includes handling missing values, outliers, duplicates, and generating insightful visualizations to explore trends in Movies & TV Shows.',
        "image_url": 'https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/Netflix%20Data%20Analysis%20%26%20Visualization%20%E2%80%93%20End-to-End%20Insights.png',
        "github_url": 'https://github.com/derravi/Netflix-Data-Cleaning-Visualization-Project-Full-Projects',
    },
    {
        "slug": 'live-weather-django',
        "title": 'Live Weather Website using Django',
        "category": 'web-dev',
        "tags": ['python', 'django', 'weather-api'],
        "description": 'A weather website built using Django that provides real-time weather updates and forecasts. It fetches data from weather APIs and displays it in an easy-to-understand format, offering users accurate weather information for their location.',
        "image_url": 'https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/Live%20Weather%20Web%20Application%20%E2%80%93%20Built%20with%20Django.png',
        "github_url": 'https://github.com/derravi/Live_Weather_Website_Using_Django',
    },
    {
        "slug": 'todo-list-django',
        "title": 'Todo List',
        "category": 'web-dev',
        "tags": ['python', 'html', 'css'],
        "description": 'A To-Do List allows users to add, update, delete, and track tasks. It lets you mark tasks as completed or incomplete to stay organized and manage your daily activities effectively.',
        "image_url": 'https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/todo%20list%20using%20the%20python%20django.png',
        "github_url": 'https://github.com/derravi/Todo-list-using-django',
    },
    {
        "slug": 'qr-code-generator',
        "title": 'QR Code Generator',
        "category": 'web-dev',
        "tags": ['python', 'django', 'qrcode'],
        "description": 'QR Code Generator Project: A user-friendly tool built with Python Django, using the QRCode and PIL libraries. Enter a link, click "OK," and instantly generate a downloadable QR code! Perfect for creating QR codes for websites, events, and more.',
        "image_url": 'https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/QR%20Code%20Generator%20Project%20Using%20Django.jpg',
        "github_url": 'https://github.com/derravi/QRcode_genorater--Using-Django',
    },
    {
        "slug": 'password-generator-django',
        "title": 'Password Generator',
        "category": 'web-dev',
        "tags": ['python', 'django'],
        "description": 'This project is a feature-rich password generator built with HTML, CSS, and JavaScript. It allows users to create secure passwords by including numbers, symbols, uppercase and lowercase characters, ensuring strong password security.',
        "image_url": 'https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/Auto%20Password%20Generator.jpg',
        "github_url": 'https://github.com/derravi/Password-Genorater-Using-Django',
    },
    {
        "slug": 'age-calculator-python',
        "title": 'Age Calculator using Python',
        "category": 'python-tools',
        "tags": ['python'],
        "description": "A simple desktop application built with Python's Tkinter library to calculate a person's age based on their date of birth. It provides an interactive GUI where users can input their name and birth date, and instantly see their current age.",
        "image_url": 'https://cdn.jsdelivr.net/gh/derravi/Portfolio_images@main/age_caleculator_using_python.png',
        "github_url": 'https://github.com/derravi/Age-Calculator-GUI-using-Python',
    },
]

def _row_to_project(row):
    """Normalize a DB row (dict) into the shape the rest of the app expects."""
    tags = row.get("tags") or []
    if isinstance(tags, str):
        try:
            import json
            tags = json.loads(tags)
        except Exception:
            tags = []
    return {
        "id": row.get("id"),
        "slug": row.get("slug"),
        "title": row.get("title"),
        "category": row.get("category"),
        "tags": tags,
        "description": row.get("description") or "",
        "image_url": row.get("image_url") or "",
        "demo_url": row.get("demo_url") or "",
        "github": row.get("github_url") or "#",       # kept for backward compatibility
        "github_url": row.get("github_url") or "#",
        "status": row.get("status") or "published",
        "featured": bool(row.get("featured")),
        "view_count": row.get("view_count") or 0,
    }


def ensure_seeded():
    """Make sure the admin_projects table exists and, the very first time,
    is pre-filled with the portfolio's existing projects. Safe to call on
    every app startup — it only inserts seed data when the table is empty."""
    admin_db.init_admin_tables()
    existing = admin_db.get_all_projects()
    if existing:
        return
    for p in DEFAULT_PROJECTS:
        admin_db.create_project(
            slug=p["slug"],
            title=p["title"],
            description=p.get("description", ""),
            category=p["category"],
            tags=p.get("tags", []),
            github_url=p.get("github_url", "#"),
            image_url=p.get("image_url", ""),
            demo_url=p.get("demo_url", ""),
            status="published",
            featured=p.get("featured", False),
        )


def get_projects(published_only=True):
    """Fresh list of projects straight from the database (live — reflects
    any admin add/edit/delete immediately, no caching)."""
    status = "published" if published_only else "all"
    rows = admin_db.get_all_projects(status=status)
    return [_row_to_project(r) for r in rows]


def get_projects_by_slug(published_only=True):
    return {p["slug"]: p for p in get_projects(published_only)}


def get_project(slug):
    """Look up a single project by slug (checked against ALL statuses so
    admin preview links to drafts still work)."""
    row = admin_db.get_project_by_slug(slug)
    return _row_to_project(row) if row else None


def get_related(slug, limit=3):
    """Lightweight content-based recommendation: rank other published
    projects by tag overlap (Jaccard-style) with the given project."""
    base = get_project(slug)
    if not base:
        return []
    base_tags = set(base["tags"])
    all_projects = get_projects()
    scored = []
    for p in all_projects:
        if p["slug"] == slug:
            continue
        overlap = len(base_tags & set(p["tags"]))
        same_category = 1 if p["category"] == base["category"] else 0
        score = overlap * 2 + same_category
        if score > 0:
            scored.append((score, p))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:limit]]
