# sentiment_routes.py
from flask import Blueprint, request, session, redirect, url_for, current_app
from models.sentiment_model import analyze_sentiment
from datetime import datetime

sentiment_bp = Blueprint("sentiment_bp", __name__)


@sentiment_bp.route("/sentiment", methods=["POST"])
def sentiment():
    """
    Process user feedback and analyze sentiment.
    Stores feedback in MongoDB and sets session variables for display.
    """
    question = request.form.get("question")
    response = request.form.get("response")
    feedback = request.form.get("feedback")

    if feedback:
        sentiment_result = analyze_sentiment(feedback)

        # Store in session to show in chat
        session["question"] = question
        session["response"] = response
        session["sentiment"] = sentiment_result

        # ✅ Save to MongoDB
        current_app.db.feedbacks.insert_one({
            "question": question,
            "response": response,
            "feedback": feedback,
            "sentiment": sentiment_result,
            "timestamp": datetime.utcnow()
        })

    return redirect(url_for("chat_bp.chat"))