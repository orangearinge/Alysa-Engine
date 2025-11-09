import pytest
import numpy as np
from PIL import Image
from app.ai_models import ocr

# BLACK BOX TESTING - EP
class TestBlackBoxEP:
    def test_preprocess_valid_image(self):
        """Equivalence Partition: valid image (RGB expected)."""
        img = Image.new("RGB", (100, 100), color="white")
        result = ocr.preprocess_image(img)
        assert isinstance(result, np.ndarray)
        assert result.shape[2] == 3  # RGB

    def test_preprocess_invalid_none(self):
        """Equivalence Partition: invalid input (None)."""
        with pytest.raises(ValueError, match="No image uploaded"):
            ocr.preprocess_image(None)

    def test_preprocess_invalid_format(self):
        """Equivalence Partition: invalid image object (not PIL Image)."""
        with pytest.raises(ValueError, match="Invalid image file"):
            ocr.preprocess_image("bukan_gambar")

    def test_extract_text_with_text(self, monkeypatch):
        """Equivalence Partition: image dengan teks valid."""
        dummy_array = np.zeros((100, 100, 3))
        monkeypatch.setattr(ocr.reader, "readtext", lambda x, detail: ["Halo dunia"])
        result = ocr.extract_text(dummy_array)
        assert result == "Halo dunia"

    def test_extract_text_no_text(self, monkeypatch):
        """Equivalence Partition: image tanpa teks."""
        dummy_array = np.zeros((100, 100, 3))
        monkeypatch.setattr(ocr.reader, "readtext", lambda x, detail: [])
        with pytest.raises(ValueError, match="No text detected in image"):
            ocr.extract_text(dummy_array)

# WHITE BOX TESTING - DYNAMIC
class TestWhiteBoxDynamic:
    def test_process_image_flow(self, mocker):
        """Dynamic testing: pastikan seluruh fungsi dipanggil dengan benar."""
        mock_img = Image.new("RGB", (50, 50), color="white")

        # Mock semua fungsi internal
        mock_pre = mocker.patch("app.ai_models.ocr.preprocess_image", return_value=np.zeros((50, 50, 3)))
        mock_ext = mocker.patch("app.ai_models.ocr.extract_text", return_value="contoh teks")
        mock_build = mocker.patch("app.ai_models.ocr.build_prompt", return_value="prompt dummy")
        mock_query = mocker.patch("app.ai_models.ocr.query_gemini", return_value='{"translation": "Hello"}')
        mock_parse = mocker.patch("app.ai_models.ocr.parse_model_output", return_value={"translation": "Hello"})

        result = ocr.process_image(mock_img)

        # Verifikasi urutan panggilan fungsi
        mock_pre.assert_called_once()
        mock_ext.assert_called_once()
        mock_build.assert_called_once()
        mock_query.assert_called_once()
        mock_parse.assert_called_once()
        assert result == {"translation": "Hello"}

    def test_process_image_error_handling(self, mocker):
        """Dynamic testing: pastikan error ditangani dengan benar."""
        mocker.patch("app.ai_models.ocr.preprocess_image", side_effect=ValueError("No image uploaded"))
        result = ocr.process_image(None)
        assert "error" in result
        assert "No image uploaded" in result["error"]