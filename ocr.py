import easyocr
from PIL import Image
import numpy as np
from google import genai
import json
import gradio as gr
import re
import os
import ssl
import certifi
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

# -----------------------------------
# KONFIGURASI API GEMINI
# -----------------------------------
GEMINI_API_KEY = "AIzaSyAP-1OSgvqEJKOmIJQzR2uPnpa0eupPxg8"
os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY

client = genai.Client()

# -----------------------------------
# SETUP OCR
# -----------------------------------
reader = easyocr.Reader(['id', 'en'])

# -----------------------------------
# FUNGSI UTAMA
# -----------------------------------

def process_image(image):
    if image is None:
        return {"error": "No image uploaded"}

    try:
        image = image.convert("RGB")
    except Exception:
        return {"error": "Invalid image file"}

    # OCR
    ocr_result = reader.readtext(np.array(image), detail=0)
    ocr_text = " ".join(ocr_result).strip()
    if not ocr_text:
        return {"error": "No text detected in image"}

    # Prompt ke Gemini
    prompt = f"""
You are a linguistics assistant.
You will receive text that may be in Indonesian or English.

Your task:
1. Detect if the text is Indonesian.
2. If yes, translate it into clear and natural English (only one version).
3. Then analyze each **English sentence**.
   For each sentence, identify:
   - Grammar point (e.g., Simple Present Tense, Coordinating Conjunction, Interjection)
   - Give a short explanation in Indonesian about how that grammar is used.

Return only valid JSON in this exact format:

{{
  "detected_language": "<string>",
  "translation": "<string>",
  "sentence_analysis": [
    {{
      "sentence": "<English sentence>",
      "grammar_point": "<string>",
      "explanation": "<string in Indonesian>"
    }}
  ]
}}

Text: {ocr_text}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        text = response.text.strip()

        # Bersihkan potensi ```json ... ```
        if text.startswith("```"):
            text = text.strip("`").replace("json", "", 1).strip()

        result = json.loads(text)
    except json.JSONDecodeError:
        result = {"raw_output": text, "error": "Invalid JSON format returned by model"}
    except Exception as e:
        result = {"error": str(e)}

    return result

# -----------------------------------
# GRADIO INTERFACE
# -----------------------------------
iface = gr.Interface(
    fn=process_image,
    inputs=gr.Image(type="pil", label="Upload Image"),
    outputs=gr.JSON(label="Result"),
    title="Gemini OCR + Translate + Grammar Check",
    description="Upload an image containing text (Indonesian or English), and get translation + grammar analysis."
)

if __name__ == "__main__":
    iface.launch()
