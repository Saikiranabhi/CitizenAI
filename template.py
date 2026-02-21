import os

# Base project folder
BASE_DIR = "citizenai"

# Folder and file structure
structure = {
    "Docker & Deployment": [
        "Dockerfile",
        ".dockerignore",
        "docker-compose.yml",
        "docker-compose.dev.yml",
    ],
    ".github/workflows": [
        "ci-cd.yml",
    ],
    "nginx/conf.d": [
        "citizenai.conf",
    ],
    "nginx": [
        "nginx.conf",
    ],
    "database": [
        "db.py",
        "user_model.py",
    ],
    "models": [
        "chat_model.py",
        "sentiment_model.py",
    ],
    "routes": [
        "auth_routes.py",
        "chat_routes.py",
        "sentiment_routes.py",
        "dashboard_routes.py",
    ],
    "templates": [
        "index.html",
        "chat.html",
        "dashboard.html",
        "login.html",
        "signup.html",
        "about.html",
    ],
    "static/css": [
        "styles.css",
    ],
    "utils": [
        "text_cleaning.py",
    ],
    "scripts": [
        "deploy.sh",
    ],
    "": [  # Root level files
        "app.py",
        "requirements.txt",
    ],
    "Config": [
        ".env.example",
    ],
}

def create_structure():
    for folder, files in structure.items():
        folder_path = os.path.join(BASE_DIR, folder)

        # Create directory
        os.makedirs(folder_path, exist_ok=True)

        # Create files
        for file in files:
            file_path = os.path.join(folder_path, file)
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    f.write(f"# {file}\n")

    print("✅ citizenai project structure created successfully!")

if __name__ == "__main__":
    create_structure()
