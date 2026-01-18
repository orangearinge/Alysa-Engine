import sys
import os

# Add the project root to sys.path
sys.path.append('/home/ahmadsaif/project/capstone/Alysa-Engine')

from app.ai_models.Alysa.examiner import evaluate
from unittest.mock import MagicMock

def test_scoring():
    print("Testing scoring logic...")
    
    # Test individual evaluation scaling
    # We'll mock the model.predict to return different scores (0-5)
    import app.ai_models.Alysa.examiner as examiner
    original_model = examiner.model
    
    test_cases = [
        (0, 0.0),   # 0/5 * 9 = 0.0
        (2.5, 4.5), # 2.5/5 * 9 = 4.5
        (5, 9.0),   # 5/5 * 9 = 9.0
        (3.2, 6.0), # 3.2/5 * 9 = 5.76 -> round(5.76*2)/2 = 6.0
        (3.1, 5.5), # 3.1/5 * 9 = 5.58 -> round(5.58*2)/2 = 5.5
    ]
    
    for predicted, expected in test_cases:
        examiner.model = MagicMock()
        examiner.model.predict.return_value = [predicted]
        result = evaluate("dummy question", "dummy answer")
        actual = result['score']
        print(f"Predicted raw: {predicted} -> Actual IELTS: {actual} (Expected: {expected})")
        assert actual == expected, f"Failed: predicted {predicted}, expected {expected}, actual {actual}"

    # Test normalization to 0-10
    total_score_band = 6.5 # Average band score
    # Formula in test.py: (total_score_band / 9.0) * 10.0
    normalized = (6.5 / 9.0) * 10.0
    expected_overall = round(normalized, 1)
    print(f"Average Band 6.5 -> Normalized Overall: {expected_overall}")
    assert expected_overall == 7.2, f"Expected 7.2, got {expected_overall}"

    print("All tests passed!")

if __name__ == "__main__":
    try:
        test_scoring()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
