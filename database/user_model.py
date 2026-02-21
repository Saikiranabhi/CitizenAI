# user_model.py
from werkzeug.security import generate_password_hash, check_password_hash


class User:
    """User model for authentication and profile management."""
    
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password_hash = generate_password_hash(password)

    def save(self, db):
        """Insert user into MongoDB."""
        db.users.insert_one({
            "name": self.name,
            "email": self.email,
            "password": self.password_hash
        })

    @staticmethod
    def find_by_email(db, email):
        """Find user by email address."""
        return db.users.find_one({"email": email})

    @staticmethod
    def verify_password(stored_password, password):
        """Verify password hash."""
        return check_password_hash(stored_password, password)