# Alysa-Engine - TOEFL iBT Learning System

Sistem Pembelajaran Bahasa Inggris dengan fokus pada Speaking & Writing untuk TOEFL iBT (Internet-Based Test).

## Fitur Utama

- 🔐 **Sistem Login Sederhana** - Autentikasi user untuk akses aplikasi
- 📚 **Learning Mode** - Latihan speaking dengan soal TOEFL iBT
- 🤖 **AI Feedback** - Analisis grammar, coherence, dan scoring otomatis
- ⏱️ **Test Simulation** - Mode simulasi test (coming soon)
- 📊 **Progress Tracking** - Monitoring kemajuan belajar

## Teknologi yang Digunakan

- **Backend**: Flask (Python)
- **Frontend**: HTML, Bootstrap 5, CSS
- **AI Model**: 
  - LanguageTool untuk grammar checking
  - Sentence Transformers untuk coherence analysis
  - Custom scoring algorithm

## Instalasi dan Setup

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd alysa-engine
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Gemini API (Optional)**
   ```bash
   # Set environment variable for Gemini AI
   export GEMINI_API_KEY="your_api_key_here"
   
   # Or create .env file with:
   # GEMINI_API_KEY=your_api_key_here
   ```
   *Note: Tanpa API key, Gemini model akan menggunakan mock mode*

4. **Jalankan aplikasi**
   
   **Option A: Flask Web App (Full Learning System)**
   ```bash
   python app.py
   ```
   - Akses di: `http://localhost:5000`
   
   **Option B: Gradio Testing Interface (AI Model Testing)**
   ```bash
   python gradio_app.py
   ```
   - Akses di: `http://localhost:7860`

## Login Credentials (Demo)

- Username: `demo` | Password: `demo`
- Username: `student1` | Password: `password123`

## Struktur Aplikasi

```
alysa-engine/
├── app.py                    # Main Flask application
├── gradio_app.py            # Gradio testing interface
├── feedback-model-alysa.py   # AI feedback model
├── requirements.txt          # Python dependencies
├── templates/               # HTML templates
│   ├── base.html           # Base template
│   ├── login.html          # Login page
│   ├── dashboard.html      # Main dashboard
│   ├── learning.html       # Learning mode
│   ├── speaking.html       # Speaking practice
│   ├── feedback.html       # AI feedback results
│   └── simulation.html     # Test simulation (coming soon)
├── README.md               # Main documentation
├── GRADIO_README.md        # Gradio interface documentation
├── GEMINI_SETUP.md         # Gemini API setup guide
└── MODEL_TESTING.md        # Individual model testing guide
```

## Cara Penggunaan

1. **Login** dengan credentials yang tersedia
2. **Pilih Learning Mode** dari dashboard
3. **Pilih soal speaking** yang ingin dipraktikkan
4. **Tulis response** dalam text area (simulasi speaking)
5. **Submit untuk analisis AI** dan dapatkan feedback
6. **Review feedback** untuk improvement

## AI Feedback Features

- ✅ **Grammar Analysis** - Deteksi dan koreksi grammar errors
- ✅ **Coherence Scoring** - Analisis keterkaitan antar kalimat
- ✅ **Overall Scoring** - Score 0-5 berdasarkan TOEFL criteria
- ✅ **Detailed Corrections** - Saran perbaikan spesifik
- ✅ **Comparison View** - Original vs corrected text

## Testing

### **Individual Model Testing**
```bash
# Test Alysa model
python feedback-model-alysa.py

# Test Gemini model
python feedback-model-gemini.py
```

### **Application Testing**
```bash
# Test Gradio interface
python gradio_app.py

# Test Flask web app
python app.py
```

*Note: Models tidak akan menjalankan test example ketika diimpor oleh aplikasi*

## Development Notes

- Aplikasi ini adalah prototype untuk pembelajaran TOEFL iBT
- Speaking input menggunakan text (simulasi) untuk kemudahan testing
- Model AI menggunakan heuristic scoring yang dapat dikembangkan lebih lanjut
- Database menggunakan in-memory storage (untuk production gunakan database proper)
- Models dikonfigurasi untuk clean import tanpa test output

## Future Enhancements

- 🎤 Real speech-to-text integration
- 📖 Reading comprehension module
- 🎧 Listening practice with audio
- ✍️ Writing tasks (essays)
- 📊 Advanced analytics and progress tracking
- 🎯 Personalized learning paths
- 🔄 Full test simulation mode
