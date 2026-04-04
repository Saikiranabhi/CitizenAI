# chat_model.py
import os
import time
import re
import requests
from dotenv import load_dotenv
from google import genai
from groq import Groq
from utils.text_cleaning import clean_text
from transformers import pipeline

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
# Lazy Load Flan-T5 Pipeline
# ===============================
_flan_pipeline = None

def get_flan_pipeline():
    global _flan_pipeline
    if _flan_pipeline is None:
        print("🟡 Loading Flan-T5 offline model...")
        _flan_pipeline = pipeline(
            "text2text-generation",
            model="google/flan-t5-base",
            max_new_tokens=200
        )
        print("✅ Flan-T5 model loaded.")
    return _flan_pipeline


# ===============================
# Blocked Topics / Keywords
# ===============================
BLOCKED_KEYWORDS = [
    # Violence & weapons
    "kill", "murder", "weapon", "bomb", "explosive", "shoot", "attack",
    "assassinate", "terrorist", "suicide", "harm", "hurt", "abuse",
    "torture", "rape", "assault", "kidnap", "hostage",

    # Drugs & illegal
    "drug", "cocaine", "heroin", "meth", "narcotics", "illegal",
    "smuggle", "trafficking", "hack", "malware", "virus", "phishing",

    # Hate & discrimination
    "racist", "racism", "sexist", "nazi", "hate speech", "genocide",
    "ethnic cleansing", "discrimination", "extremist", "radical",

    # Adult content
    "porn", "sex", "nude", "explicit", "adult content", "nsfw",
    "escort", "prostitute",

    # Self harm
    "self harm", "self-harm", "suicide", "cut myself", "end my life",
    "want to die", "kill myself",
]

# ===============================
# Safe Civic Topics (Whitelist)
# ===============================
CIVIC_KEYWORDS = [
    "government", "policy", "service", "civic", "report", "issue",
    "pothole", "road", "water", "electricity", "sanitation", "garbage",
    "tax", "license", "permit", "certificate", "passport", "visa",
    "hospital", "school", "public", "municipality", "council",
    "vote", "election", "pension", "welfare", "scheme", "subsidy",
    "complaint", "helpline", "emergency", "police", "fire", "ambulance",
    "ration", "aadhar", "pan card", "birth certificate", "death certificate",
    "property", "land", "registration", "court", "legal", "law",
    "transport", "bus", "metro", "railway", "airport", "traffic",
    "environment", "pollution", "noise", "sewage", "drainage",
    "electricity bill", "water bill", "fine", "challan", "application",
    "office", "department", "ministry", "portal", "online", "digital",
]


# ===============================
# Input Safety Check
# ===============================
def is_input_safe(text):
    """
    Returns (is_safe, reason)
    Blocks harmful/off-topic inputs before sending to any API.
    """
    text_lower = text.lower()

    # Check blocked keywords
    for keyword in BLOCKED_KEYWORDS:
        if keyword in text_lower:
            return False, f"blocked_keyword:{keyword}"

    # Check if it has at least some civic relevance
    # (relaxed — only block if it's clearly non-civic AND very short)
    has_civic = any(kw in text_lower for kw in CIVIC_KEYWORDS)
    is_very_short = len(text.strip().split()) <= 4

    if not has_civic and is_very_short:
        return False, "off_topic_short"

    return True, "ok"


# ===============================
# Output Safety Check
# ===============================
def is_output_safe(text):
    """
    Scans AI response for any accidentally generated harmful content.
    Returns (is_safe, cleaned_text)
    """
    text_lower = text.lower()

    for keyword in BLOCKED_KEYWORDS:
        if keyword in text_lower:
            return False, None

    return True, text


# ===============================
# Safe Response Wrapper
# ===============================
def safe_response(func, prompt):
    """
    Wraps any model call with output safety check.
    Returns None if output is unsafe.
    """
    result = func(prompt)
    is_safe, cleaned = is_output_safe(result)
    if not is_safe:
        print("🚫 Unsafe output detected, blocking response.")
        return None
    return cleaned


# ===============================
# CitizenAI System Prompt (Strict)
# ===============================
SYSTEM_PROMPT = """
You are CitizenAI, a strictly civic-only AI assistant for government services.

YOUR STRICT RULES:
1. You ONLY answer questions about:
   - Government services (water, electricity, sanitation, transport)
   - Public policies and welfare schemes
   - Civic issues (potholes, garbage, pollution, noise)
   - Administrative procedures (certificates, licenses, permits)
   - Emergency helplines (police, fire, ambulance)
   - Voting, elections, and democratic processes
   - Taxes, fines, and public dues

2. You MUST REFUSE any question involving:
   - Violence, weapons, or harm of any kind
   - Drugs or illegal substances
   - Adult or sexual content
   - Hate speech or discrimination
   - Hacking or cybercrime
   - Personal advice unrelated to civic matters
   - Entertainment, cooking, sports, jokes

3. If asked anything outside civic services, respond EXACTLY with:
   "I can only assist with civic and government service queries. 
    Please ask about public services, policies, or civic issues."

4. Never generate harmful, illegal, or inappropriate content under any circumstance.
5. Be concise, professional, and factual.
6. Do not make up government policies — say you don't know if unsure.
"""


# ===============================
# Groq — Primary Model
# ===============================
def generate_with_groq(prompt):
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=512,          # limit output length
        top_p=0.9,
    )
    result = response.choices[0].message.content.strip()
    if not result:
        raise ValueError("Empty response from Groq.")
    return result


# ===============================
# Gemini 1.5 Flash — Fallback 1
# ===============================
def generate_with_gemini(prompt):
    for attempt in range(2):
        try:
            response = gemini_client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[
                    {"role": "user", "parts": [{"text": SYSTEM_PROMPT + "\n\nUser: " + prompt}]},
                ],
            )
            if not response or not response.text:
                raise ValueError("Empty response from Gemini.")
            return response.text.strip()

        except Exception as e:
            if "429" in str(e) and attempt == 0:
                print("⏳ Gemini rate limited, retrying in 30s...")
                time.sleep(30)
            else:
                raise e


# ===============================
# Ollama TinyLlama — Fallback 2
# ===============================
def generate_with_ollama(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "tinyllama",
            "prompt": SYSTEM_PROMPT + "\n\nUser: " + prompt + "\nAssistant:",
            "stream": False
        },
        timeout=30
    )
    response.raise_for_status()
    result = response.json().get("response", "").strip()
    if not result:
        raise ValueError("Empty response from Ollama.")
    return result


# ===============================
# Flan-T5 Offline — Fallback 3
# ===============================
def generate_with_flan(prompt):
    flan = get_flan_pipeline()

    civic_prompt = (
        f"As a civic assistant, answer this government service question only:\n"
        f"Question: {prompt}\n"
        f"Answer:"
    )

    result = flan(civic_prompt)

    if result and result[0].get("generated_text"):
        answer = result[0]["generated_text"].strip()
        if answer:
            return (
                f"{answer}\n\n"
                "_(Offline response — please verify with official government sources.)_"
            )

    raise ValueError("Empty response from Flan-T5.")


# ===============================
# Main Response Function
# ===============================
def generate_response(user_input):
    cleaned_input = clean_text(user_input)

    # ── Safety check BEFORE sending to any API ──
    is_safe, reason = is_input_safe(cleaned_input)
    if not is_safe:
        print(f"🚫 Input blocked: {reason}")
        if "blocked_keyword" in reason:
            return (
                "⚠️ Your message contains content that cannot be processed. "
                "CitizenAI only handles civic and government service queries."
            )
        return (
            "I can only assist with civic and government service queries. "
            "Please ask about public services, policies, or civic issues."
        )

    # 1️⃣ Groq — Primary
    try:
        print("🟢 Trying Groq (Primary)...")
        result = safe_response(generate_with_groq, cleaned_input)
        if result:
            return result
        raise ValueError("Groq response was unsafe.")
    except Exception as e:
        print(f"⚠️ Groq failed: {e}")

    # 2️⃣ Gemini 1.5 Flash — Fallback 1
    try:
        print("🔵 Falling back to Gemini 1.5 Flash...")
        result = safe_response(generate_with_gemini, cleaned_input)
        if result:
            return result
        raise ValueError("Gemini response was unsafe.")
    except Exception as e:
        print(f"⚠️ Gemini failed: {e}")

    # 3️⃣ Ollama TinyLlama — Fallback 2
    try:
        print("🟠 Falling back to Ollama (TinyLlama)...")
        result = safe_response(generate_with_ollama, cleaned_input)
        if result:
            return result
        raise ValueError("Ollama response was unsafe.")
    except Exception as e:
        print(f"⚠️ Ollama failed: {e}")

    # 4️⃣ Flan-T5 Offline — Fallback 3
    try:
        print("🟡 Falling back to Flan-T5 (Offline)...")
        result = safe_response(generate_with_flan, cleaned_input)
        if result:
            return result
        raise ValueError("Flan-T5 response was unsafe.")
    except Exception as e:
        print(f"❌ All models failed: {e}")

    return "⚠️ All AI services are temporarily unavailable. Please try again later."


def clear_chat_history():
    pass