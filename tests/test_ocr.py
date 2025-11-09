import unittest
from unittest.mock import patch, MagicMock
from PIL import Image
import numpy as np
import json
import re
import app.ai_models.ocr as ocr


class TestOCRWhiteBox(unittest.TestCase):

    # ---------- 1. preprocess_image ----------
    def test_preprocess_image_valid(self):
        """Statement + Branch: input gambar valid"""
        img = Image.new('RGB', (10, 10), color='white')
        result = ocr.preprocess_image(img)
        self.assertIsInstance(result, np.ndarray)

    def test_preprocess_image_none(self):
        """Branch Coverage: None → Raise Error"""
        with self.assertRaises(ValueError):
            ocr.preprocess_image(None)

    def test_preprocess_image_invalid(self):
        """Exception path: gambar tidak valid"""
        class FakeImage:
            def convert(self, mode): raise Exception("Conversion failed")
        with self.assertRaises(ValueError):
            ocr.preprocess_image(FakeImage())

    # ---------- 2. extract_text ----------
    @patch.object(ocr.reader, 'readtext', return_value=["Halo", "Dunia"])
    def test_extract_text_valid(self, mock_ocr):
        """Normal path: OCR menghasilkan teks"""
        img = np.zeros((10, 10, 3))
        text = ocr.extract_text(img)
        self.assertEqual(text, "Halo Dunia")

    @patch.object(ocr.reader, 'readtext', return_value=[])
    def test_extract_text_no_text(self, mock_ocr):
        """Branch: OCR kosong → error"""
        with self.assertRaises(ValueError):
            ocr.extract_text(np.zeros((10, 10, 3)))

    # ---------- 3. build_prompt ----------
    def test_build_prompt_contains_text(self):
        """Path tunggal: selalu return string format prompt"""
        text = "Selamat pagi"
        result = ocr.build_prompt(text)
        self.assertIn(text, result)
        self.assertIn("translation", result)

    # ---------- 4. parse_model_output ----------
    def test_parse_model_output_valid_json(self):
        """Branch: JSON valid"""
        valid_json = json.dumps({"translation": "Hi"})
        result = ocr.parse_model_output(valid_json)
        self.assertEqual(result["translation"], "Hi")

    def test_parse_model_output_invalid_json(self):
        """Branch: JSON invalid"""
        invalid_json = "{invalid json}"
        result = ocr.parse_model_output(invalid_json)
        self.assertIn("error", result)

    def test_parse_model_output_wrapped_code_block(self):
        """Branch: output dibungkus triple backtick"""
        wrapped = "```json\n{\"translation\": \"Hi\"}\n```"
        result = ocr.parse_model_output(wrapped)
        self.assertEqual(result["translation"], "Hi")

    # ---------- 5. process_image ----------
    @patch("app.ai_models.ocr.query_gemini", return_value=json.dumps({"translation": "OK"}))
    @patch("app.ai_models.ocr.extract_text", return_value="Hello world")
    @patch("app.ai_models.ocr.preprocess_image", return_value=np.zeros((1,1,3)))
    def test_process_image_valid_flow(self, mock_pre, mock_ext, mock_query):
        """Full pipeline: semua fungsi berjalan sukses"""
        result = ocr.process_image(Image.new('RGB', (10, 10)))
        self.assertIn("translation", result)

    @patch("app.ai_models.ocr.preprocess_image", side_effect=ValueError("No image uploaded"))
    def test_process_image_error_flow(self, mock_pre):
        """Error path: satu fungsi melempar exception"""
        result = ocr.process_image(None)
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
