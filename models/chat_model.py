import os
from dotenv import load_dotenv
from google import genai
from groq import Groq
from utils.text_cleaning import clean_text

# ===============================
# Load Environment Variables
# ===============================
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Gemini API key not found.")

if not GROQ_API_KEY:
    raise ValueError("Groq API key not found.")

# ===============================
# Initialize Clients
# ===============================
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

# ===============================
# CitizenAI System Prompt
# ===============================
SYSTEM_PROMPT = """
You are CitizenAI, a civic service assistant.

You ONLY answer questions related to:
- Government services
- Public policies
- Civic issues
- Reporting public problems
- Administrative procedures

If a question is unrelated to civic services
(e.g., cooking, entertainment, jokes, personal advice),
respond EXACTLY with:

That topic is outside civic services. Please ask about government services, public policies, or reporting issues.

Do not answer non-civic questions.
Be concise and professional.
"""

# ===============================
# Gemini (Primary Model)
# ===============================
def generate_with_gemini(prompt):
    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            {"role": "system", "parts": [{"text": SYSTEM_PROMPT}]},
            {"role": "user", "parts": [{"text": prompt}]},
        ],
    )

    if not response or not response.text:
        raise ValueError("Empty response from Gemini.")

    return response.text.strip()


# ===============================
# Groq (Fallback Model)
# ===============================
def generate_with_groq(prompt):
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,  # lower temperature = stricter rule following
    )

    return response.choices[0].message.content.strip()


# ===============================
# Main Response Function
# ===============================
def generate_response(user_input):
    cleaned_input = clean_text(user_input)

    try:
        print("🔵 Trying Gemini...")
        return generate_with_gemini(cleaned_input)

    except Exception as e:
        print("⚠ Gemini failed:", e)

        try:
            print("🟢 Switching to Groq fallback...")
            return generate_with_groq(cleaned_input)

        except Exception as e2:
            print("❌ Groq also failed:", e2)
            return "⚠️ AI service is temporarily unavailable. Please try again later."


def clear_chat_history():
    pass