# app.py
import os
from flask import Flask, render_template
from dotenv import load_dotenv
from database.db import init_db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-in-production")

# ── MongoDB ──────────────────────────────────────
mongo = init_db(app)
app.mongo = mongo
app.db = mongo.db
app.config["DB"] = mongo.db

# ── Blueprints ───────────────────────────────────
from routes.auth_routes import auth_bp, google_bp
from routes.chat_routes import chat_bp
from routes.sentiment_routes import sentiment_bp
from routes.dashboard_routes import dashboard_bp

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(google_bp, url_prefix="/google_login")
app.register_blueprint(chat_bp)
app.register_blueprint(sentiment_bp)
app.register_blueprint(dashboard_bp)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/ping-db")
def ping_db():
    if app.db is None:
        return "❌ DB is not connected", 500
    try:
        app.db.command("ping")
        return "✅ MongoDB connected!", 200
    except Exception as e:
        return f"❌ MongoDB command failed: {e}", 500


if __name__ == "__main__":
    debug = os.getenv("FLASK_ENV", "production") == "development"
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=debug)