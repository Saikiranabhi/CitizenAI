# auth_routes.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_dance.contrib.google import make_google_blueprint, google
import os
from database.user_model import User
from flask import current_app

auth_bp = Blueprint("auth_bp", __name__)

# ──────────────────────────────────────────────────
# Google OAuth Blueprint
# ──────────────────────────────────────────────────
google_bp = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "your-google-client-id"),
    client_secret=os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "your-google-client-secret"),
    scope=["profile", "email"],
    redirect_url="/google_login/callback"
)


@auth_bp.route("/google_login")
def google_login():
    """Redirect to Google OAuth login."""
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info from Google.", "error")
        return redirect(url_for("auth_bp.login"))
    info = resp.json()
    email = info["email"]
    name = info.get("name", email.split("@")[0])
    user = User.find_by_email(current_app.config["DB"], email)
    if not user:
        user = User(name, email, "")
        user.save(current_app.config["DB"])
    session["user_id"] = str(user["_id"])
    session["user_name"] = user["name"]
    flash("Logged in with Google!", "success")
    return redirect(url_for("index"))


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """User signup with email and password."""
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.find_by_email(current_app.config["DB"], email)
        if existing_user:
            flash("Email already registered!", "error")
            return redirect(url_for("auth_bp.signup"))

        user = User(name, email, password)
        user.save(current_app.config["DB"])

        flash("Account created successfully!", "success")
        return redirect(url_for("auth_bp.login"))

    return render_template("signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login with email and password."""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.find_by_email(current_app.config["DB"], email)
        if user and User.verify_password(user["password"], password):
            session["user_id"] = str(user["_id"])
            session["user_name"] = user["name"]
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password!", "error")
            return redirect(url_for("auth_bp.login"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """Clear session and logout user."""
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for("auth_bp.login"))