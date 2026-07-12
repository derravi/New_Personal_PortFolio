"""
test_app.py — Automated tests for the portfolio Flask app.

Run with: pytest -v
Also run automatically by .github/workflows/ci-cd.yml on every push/PR.
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("ADMIN_TOKEN", "test-admin-token")


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Point the SQLite DB at a temp directory so tests never touch real data.
    import db
    monkeypatch.setattr(db, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))

    from flask_app import app
    app.config["TESTING"] = True
    db.init_db()
    with app.test_client() as c:
        yield c


PUBLIC_PAGES = [
    "/", "/about", "/projects", "/skills", "/achievements", "/experience",
    "/education", "/blog", "/contact", "/my_learning", "/quiz", "/resume",
    "/sitemap.xml", "/robots.txt", "/healthz",
]


@pytest.mark.parametrize("path", PUBLIC_PAGES)
def test_public_pages_load(client, path):
    resp = client.get(path)
    assert resp.status_code < 400, f"{path} returned {resp.status_code}"


def test_blog_post_detail(client):
    resp = client.get("/blog/getting-started-with-ml-pipelines")
    assert resp.status_code == 200
    assert b"ML Pipelines" in resp.data or b"pipeline" in resp.data.lower()


def test_api_projects_list(client):
    resp = client.get("/api/projects")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list) and len(data) > 0


def test_review_submit_and_fetch(client):
    slug = "credit-card-fraud-detection"
    post_resp = client.post(f"/api/projects/{slug}/reviews", json={
        "name": "Tester", "rating": 4, "comment": "Solid project"
    })
    assert post_resp.status_code == 201

    get_resp = client.get(f"/api/projects/{slug}/reviews")
    data = get_resp.get_json()
    assert data["count"] == 1
    assert data["average_rating"] == 4.0


def test_review_rejects_bad_rating(client):
    resp = client.post("/api/projects/credit-card-fraud-detection/reviews", json={
        "name": "Tester", "rating": 9
    })
    assert resp.status_code == 400


def test_newsletter_signup(client):
    resp = client.post("/api/newsletter", json={"email": "someone@example.com"})
    assert resp.status_code == 201
    # Second signup with the same email should not error, just report already-subscribed
    resp2 = client.post("/api/newsletter", json={"email": "someone@example.com"})
    assert resp2.status_code == 200


def test_newsletter_rejects_invalid_email(client):
    resp = client.post("/api/newsletter", json={"email": "not-an-email"})
    assert resp.status_code == 400


def test_contact_requires_fields(client):
    resp = client.post("/api/contact", json={"name": "A"})
    assert resp.status_code == 400


def test_quiz_scoring(client):
    resp = client.post("/api/quiz", json={"name": "T", "score": 5, "total": 5})
    data = resp.get_json()
    assert data["percentage"] == 100.0
    assert data["level"] == "Advanced"


def test_chatbot_fallback_reply(client):
    resp = client.post("/api/chatbot", json={"message": "what skills does ravi have?"})
    assert resp.status_code == 200
    assert "reply" in resp.get_json()


def test_analytics_requires_token(client):
    resp = client.get("/api/analytics/summary")
    assert resp.status_code == 401

    resp2 = client.get("/api/analytics/summary?token=test-admin-token")
    assert resp2.status_code == 200


def test_pdf_export(client):
    resp = client.get("/export/resume.pdf")
    assert resp.status_code == 200
    assert resp.mimetype == "application/pdf"


def test_docx_export(client):
    resp = client.get("/export/resume.docx")
    assert resp.status_code == 200


def test_404_page(client):
    resp = client.get("/this-route-does-not-exist")
    assert resp.status_code == 404


def test_rate_limit_kicks_in(client):
    # newsletter limit is 5/min — the 6th quick submission should be throttled
    for i in range(5):
        client.post("/api/newsletter", json={"email": f"user{i}@example.com"})
    resp = client.post("/api/newsletter", json={"email": "onemore@example.com"})
    assert resp.status_code == 429
