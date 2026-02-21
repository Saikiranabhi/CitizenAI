# dashboard_routes.py
from flask import Blueprint, render_template, current_app, session, redirect, url_for

dashboard_bp = Blueprint("dashboard_bp", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    """
    Analytics dashboard showing sentiment statistics.
    Displays counts and percentages for Positive, Neutral, and Negative feedback.
    """
    # Require authentication
    if not session.get("user_name"):
        return redirect(url_for("auth_bp.login"))
    
    db = current_app.db
    feedbacks = list(db.feedbacks.find())

    # Count sentiment categories
    positive = db.feedbacks.count_documents({"sentiment": "Positive"})
    neutral = db.feedbacks.count_documents({"sentiment": "Neutral"})
    negative = db.feedbacks.count_documents({"sentiment": "Negative"})
    total = positive + neutral + negative
    
    # Calculate percentages
    if total > 0:
        positive_pct = round(positive / total * 100, 1)
        neutral_pct = round(neutral / total * 100, 1)
        negative_pct = round(negative / total * 100, 1)
    else:
        positive_pct = neutral_pct = negative_pct = 0

    return render_template(
        "dashboard.html",
        positive=positive,
        neutral=neutral,
        negative=negative,
        positive_pct=positive_pct,
        neutral_pct=neutral_pct,
        negative_pct=negative_pct,
        feedbacks=feedbacks
    )