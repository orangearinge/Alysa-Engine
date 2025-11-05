# 🧪 Model Testing Guide

Panduan untuk testing individual AI models secara terpisah dari aplikasi Gradio.

## 🎯 Overview

Kedua model (`feedback-model-alysa.py` dan `feedback-model-gemini.py`) telah dikonfigurasi untuk:
- **Import Mode**: Tidak menjalankan test ketika diimpor oleh aplikasi lain
- **Direct Execution**: Menjalankan test example ketika dieksekusi langsung

## 🚀 Testing Individual Models

### **Test Alysa Model**
```bash
cd /Users/fadil/repo/ai/capstone/alysa-engine
python feedback-model-alysa.py
```

**Expected Output:**
```
Testing Alysa TOEFL Feedback Model...
Result:
{
  'original': '...',
  'corrected': '...',
  'grammar_errors': 4,
  'avg_coherence': 0.567,
  'score': 3.2,
  'feedback': [...],
  'detailed_corrections': [...]
}
```

### **Test Gemini Model**
```bash
cd /Users/fadil/repo/ai/capstone/alysa-engine
python feedback-model-gemini.py
```

**Expected Output (with API key):**
```
Testing Gemini TOEFL Feedback Model...
Result:
{
  "original": "...",
  "corrected": "...",
  "grammar_errors": 3,
  "avg_coherence": 0.65,
  "score": 3.8,
  "feedback": [...],
  "detailed_corrections": [...]
}
```

**Expected Output (without API key - Mock Mode):**
```
Testing Gemini TOEFL Feedback Model...
Result:
{
  "original": "...",
  "corrected": "...",
  "grammar_errors": 2,
  "avg_coherence": 0.6,
  "score": 3.5,
  "feedback": ["Analysis completed using Gemini AI (Mock Mode).", ...],
  "detailed_corrections": [...]
}
```

## 🔄 Import Behavior

### **When Imported (No Test Execution)**
```python
# In gradio_app.py or other files
from feedback_model_alysa import ai_toefl_feedback_alysa
from feedback_model_gemini import ai_toefl_feedback_gemini

# No test output will be printed
# Only the functions are available for use
```

### **When Executed Directly (Test Runs)**
```bash
python feedback-model-alysa.py
# Prints test results

python feedback-model-gemini.py  
# Prints test results
```

## 🧪 Testing Workflow

### **1. Individual Model Testing**
```bash
# Test Alysa model functionality
python feedback-model-alysa.py

# Test Gemini model (with/without API key)
python feedback-model-gemini.py
```

### **2. Gradio Application Testing**
```bash
# Run Gradio app (imports models without running tests)
python gradio_app.py
# Access: http://localhost:7860
```

### **3. Flask Application Testing**
```bash
# Run Flask app (imports models without running tests)
python app.py
# Access: http://localhost:5000
```

## 🔍 Debugging

### **Check Import Behavior**
```python
# Test import without execution
python -c "from feedback_model_alysa import ai_toefl_feedback; print('Import successful, no test output')"
```

### **Verify Model Functions**
```python
# Quick function test
python -c "
from feedback_model_alysa import ai_toefl_feedback
result = ai_toefl_feedback('This is test.')
print('Function works:', 'score' in result)
"
```

## 📊 Comparison Testing

### **Same Input, Different Models**
```bash
# Create test script
cat > test_comparison.py << 'EOF'
from feedback_model_alysa import ai_toefl_feedback as alysa_feedback
from feedback_model_gemini import ai_toefl_feedback as gemini_feedback

test_text = "Many students want study abroad because they believe it give them more opportunity."

print("=== ALYSA MODEL ===")
alysa_result = alysa_feedback(test_text)
print(f"Score: {alysa_result['score']}")
print(f"Grammar Errors: {alysa_result['grammar_errors']}")

print("\n=== GEMINI MODEL ===")
gemini_result = gemini_feedback(test_text)
print(f"Score: {gemini_result['score']}")
print(f"Grammar Errors: {gemini_result['grammar_errors']}")
EOF

python test_comparison.py
```

## 🎯 Benefits

### **✅ Clean Import**
- No unwanted output when importing
- Faster application startup
- Professional behavior

### **✅ Easy Testing**
- Direct execution for quick testing
- Consistent test examples
- Clear output formatting

### **✅ Development Workflow**
- Test individual models independently
- Debug specific model issues
- Compare model outputs easily

## 🚨 Troubleshooting

### **No Output When Running Directly**
- Check if you're in the correct directory
- Ensure Python can find the dependencies
- Verify file permissions

### **Import Errors in Gradio**
- Check if all dependencies are installed
- Verify file paths in gradio_app.py
- Test individual imports

### **Gemini API Issues**
- Model will fallback to mock mode
- Check GEMINI_API_KEY environment variable
- Verify internet connection for real API calls

---

**Note**: Dengan konfigurasi ini, Anda bisa menjalankan Gradio tanpa output test yang mengganggu, sambil tetap bisa test individual models ketika diperlukan!
