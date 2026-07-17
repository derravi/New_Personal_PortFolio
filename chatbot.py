"""
chatbot.py — Portfolio AI assistant.

If OPENAI_API_KEY is set in the environment, questions are answered by
calling the OpenAI Chat Completions API with a short system prompt that
gives the model context about Ravi Der's portfolio.

If no key is configured (the default, out of the box), a small rule-based
fallback answers common questions (skills, projects, contact, experience)
using keyword matching against the same context, so the chat widget is
still genuinely useful with zero setup.
"""

import os
import json
import urllib.request
import urllib.error

import projects_data
from projects_data import CATEGORY_LABELS

SITE_CONTEXT = """
You are the portfolio assistant for Ravi Der, a B.Tech IT graduate currently
pursuing an M.Tech in AI, Machine Learning and Data Science. He is from
Mandvi, District Bhavnagar, India. He has completed 3 internships and built
20+ projects spanning AI/ML, data analysis, and Python/Django web apps.
Core skills: Python, Scikit-Learn, Pandas, NumPy, Matplotlib, FastAPI, MySQL,
HTML/CSS/JavaScript, Bootstrap 5, Git/GitHub, CI/CD concepts, Docker.
Answer questions about his background, skills, and projects concisely and
in a friendly, professional tone. If asked something unrelated to the
portfolio, politely redirect to portfolio-related topics. Keep answers
under 120 words.
"""


def _openai_reply(message, history):
    api_key = os.environ.get("OPENAI_API_KEY")
    messages = [{"role": "system", "content": SITE_CONTEXT}]
    for turn in history[-6:]:
        role = "user" if turn.get("role") == "user" else "assistant"
        messages.append({"role": role, "content": turn.get("content", "")[:1000]})
    messages.append({"role": "user", "content": message})

    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": messages,
        "max_tokens": 220,
        "temperature": 0.6,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip()


def _rule_based_reply(message):
    text = message.lower()

    if any(w in text for w in ["hi", "hello", "hey"]):
        return "Hey! I'm the portfolio assistant. Ask me about Ravi's skills, projects, experience, or how to get in touch."

    if any(w in text for w in ["project", "portfolio", "work", "built"]):
        names = ", ".join(p["title"] for p in projects_data.get_projects()[:5])
        return f"Ravi has built 20+ projects across {', '.join(CATEGORY_LABELS.values())}. A few examples: {names}. Check out the Projects page for the full list."

    if any(w in text for w in ["skill", "tech", "stack", "language", "tool"]):
        return ("Core skills include Python, Scikit-Learn, Pandas, NumPy, Matplotlib, "
                "FastAPI, MySQL, HTML/CSS/JS, Bootstrap 5, Git/GitHub and Docker. "
                "See the Skills page for the full breakdown by category.")

    if any(w in text for w in ["contact", "email", "hire", "reach", "connect"]):
        return "You can reach out through the Contact page — there's a form right there, and it emails Ravi directly."

    if any(w in text for w in ["experience", "internship", "job", "work history"]):
        return "Ravi has completed 3 internships and roughly a year of hands-on experience. Details are on the Experience page."

    if any(w in text for w in ["education", "degree", "college", "study", "m.tech", "b.tech"]):
        return "Ravi completed a B.Tech in Information Technology and is currently pursuing an M.Tech in AI, Machine Learning & Data Science."

    if any(w in text for w in ["resume", "cv", "pdf"]):
        return "You can download a PDF summary of the resume from the '/export/resume.pdf' link (also linked from the site footer)."

    return ("I can answer questions about Ravi's projects, skills, experience, and education, "
            "or point you to the contact form. Try asking something like 'What projects has Ravi built?'")


def get_reply(message, history=None):
    history = history or []
    if os.environ.get("OPENAI_API_KEY"):
        try:
            return _openai_reply(message, history), "openai"
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, TimeoutError, Exception) as exc:
            print(f"[chatbot] OpenAI call failed, falling back to rule-based reply: {exc}")
    return _rule_based_reply(message), "rule-based"
