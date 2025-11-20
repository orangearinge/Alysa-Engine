import json
import re
import ssl

import certifi
import easyocr
import gradio as gr
import numpy as np
from google import genai
from PIL import Image

# KONFIGURASI API & SSL
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

client = genai.Client()
reader = easyocr.Reader(['id', 'en'])


# 🧩 PIPELINE FUNCTIONS
def preprocess_image(image: Image.Image):
    """Validasi dan konversi gambar ke format OCR-ready (RGB numpy array)."""
    if image is None:
        raise ValueError("No image uploaded")
    try:
        image = image.convert("RGB")
        return np.array(image)
    except Exception:
        raise ValueError("Invalid image file")


def extract_text(image_array: np.ndarray):
    """Ambil teks dari gambar menggunakan EasyOCR."""
    ocr_result = reader.readtext(image_array, detail=0)
    text = " ".join(ocr_result).strip()
    if not text:
        raise ValueError("No text detected in image")
    return text


def build_prompt(ocr_text: str):
    """Buat prompt untuk dikirim ke Gemini."""
    return f"""
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


def query_gemini(prompt: str):
    """Kirim prompt ke Gemini dan kembalikan hasil teks mentah."""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text.strip()


def parse_model_output(text: str):
    """Bersihkan dan parsing hasil output dari Gemini menjadi JSON."""
    # Bersihkan dari wrapper Markdown
    if text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text)
        text = text.replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw_output": text, "error": "Invalid JSON format returned by model"}



# MAIN PROCESS FUNCTION
def process_image(image):
    try:
        img_array = preprocess_image(image)
        ocr_text = extract_text(img_array)
        prompt = build_prompt(ocr_text)
        raw_response = query_gemini(prompt)
        result = parse_model_output(raw_response)
        return result
    except Exception as e:
        return {"error": str(e)}



# GRADIO INTERFACE
iface = gr.Interface(
    fn=process_image,
    inputs=gr.Image(type="pil", label="Upload Image"),
    outputs=gr.JSON(label="Result"),
    title="Gemini OCR + Translate + Grammar Check",
    description="Upload an image containing text (Indonesian or English), and get translation + grammar analysis."
)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", share=True)
