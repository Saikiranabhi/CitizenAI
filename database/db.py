# db.py
import os
from flask_pymongo import PyMongo


def init_db(app):
    """
    Initialize MongoDB connection.
    URI is read from MONGO_URI env var (set in .env or docker-compose).
    Fallback to localhost for local development.
    """
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/citizenai")
    app.config["MONGO_URI"] = mongo_uri
    print(f"✅ Connecting to MongoDB: {mongo_uri}")
    mongo = PyMongo(app)
    return mongo