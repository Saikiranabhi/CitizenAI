# chat_routes.py
from flask import Blueprint, render_template, request, session, redirect, url_for
from models.chat_model import generate_response

chat_bp = Blueprint("chat_bp", __name__)


@chat_bp.route("/chat", methods=["GET", "POST"])
def chat():
    """
    Chat interface route.
    - GET: Display chat page (with optional feedback results from session)
    - POST: Process user question and generate AI response
    """
    # Require authentication
    if not session.get("user_name"):
        return redirect(url_for("auth_bp.login"))
    
    if request.method == "POST":
        question = request.form.get("question")
        if question:
            response = generate_response(question)
            return render_template("chat.html", question=question, question_response=response)

    # Show after feedback submission (pulled from session)
    question = session.pop("question", None)
    response = session.pop("response", None)
    sentiment = session.pop("sentiment", None)

    return render_template("chat.html", question=question, question_response=response, sentiment=sentiment)