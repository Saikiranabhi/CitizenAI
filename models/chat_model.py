# chat_model.py
import os
from dotenv import load_dotenv
import google.generativeai as genai
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
import torch
from utils.text_cleaning import clean_text

# Load environment variables
load_dotenv()

# Configuration: Switch between Gemini and IBM Granite
USE_GEMINI = True  # Set to True for Gemini API, False for IBM Granite

if USE_GEMINI:
    # ──────────────────────────────────────────
    # Gemini API Setup
    # ──────────────────────────────────────────
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Gemini API token not found in environment variables.")
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel("gemini-2.0-flash-exp")
    gemini_chat = gemini_model.start_chat(history=[])
else:
    # ──────────────────────────────────────────
    # IBM Granite Setup
    # ──────────────────────────────────────────
    class ChatModel:
        def __init__(self, model_path="ibm-granite/granite-3.0-8b-instruct"):
            self.model_path = model_path
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map=self.device,
                torch_dtype=torch.bfloat16 if self.device == "cuda" else torch.float32,
            )
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)

        def generate_text(self, prompt, max_new_tokens=1024, seed=42):
            conv = [{"role": "user", "content": prompt}]
            input_ids = self.tokenizer.apply_chat_template(
                conv,
                return_tensors="pt",
                thinking=True,
                return_dict=True,
                add_generation_prompt=True
            ).to(self.device)
            set_seed(seed)
            output = self.model.generate(
                **input_ids,
                max_new_tokens=max_new_tokens,
            )
            prediction = self.tokenizer.decode(
                output[0, input_ids["input_ids"].shape[1]:],
                skip_special_tokens=True
            )
            return prediction

    chat_model = ChatModel()


def generate_response(user_input):
    """
    Generate a response using either Gemini API or IBM Granite.
    Controlled by USE_GEMINI variable at the top of this file.
    """
    try:
        cleaned_input = clean_text(user_input)
        
        if USE_GEMINI:
            response = gemini_chat.send_message(cleaned_input)
            return response.text
        else:
            response = chat_model.generate_text(cleaned_input)
            return response
            
    except Exception as e:
        print("[ERROR in generate_response]:", e)
        return "Sorry, I couldn't process your request right now."