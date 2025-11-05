# 🎯 TOEFL iBT AI Feedback Analyzer - Gradio Interface

Interface testing untuk membandingkan 2 model AI: `feedback-model-alysa.py` dan `feedback-model-gemini.py` menggunakan Gradio.

## 🚀 Cara Menjalankan

1. **Install dependencies** (jika belum):
   ```bash
   pip install -r requirements.txt
   ```

2. **Jalankan aplikasi Gradio**:
   ```bash
   python gradio_app.py
   ```

3. **Akses interface**:
   - Buka browser dan kunjungi: `http://localhost:7860`
   - Interface akan terbuka otomatis

## 🎨 Fitur Interface

### ✍️ Input Section
- **🤖 Model Selection** - Pilih antara 2 AI models:
  - **Alysa Model** - LanguageTool + Sentence Transformers (Local)
  - **Gemini Model** - Google Gemini AI (Cloud-based)
- **📝 Text Area** - Tempat memasukkan teks untuk dianalisis
- **Sample Texts** - 3 contoh teks dengan karakteristik berbeda:
  - **Good Example** - Teks dengan grammar baik dan coherent
  - **Grammar Errors** - Teks dengan banyak kesalahan grammar
  - **Poor Coherence** - Teks dengan coherence rendah

### 📊 Analysis Results (Tabbed Interface)

#### 1. **📝 Grammar Analysis**
- Jumlah grammar errors yang ditemukan
- Detail koreksi untuk setiap error:
  - Kata/frasa yang salah
  - Saran perbaikan
  - Penjelasan error

#### 2. **🔗 Coherence Analysis**
- Coherence score (0-1)
- Persentase coherence
- Penjelasan tentang coherence

#### 3. **💬 AI Feedback**
- Feedback messages dari AI
- Saran improvement
- Penilaian overall

#### 4. **📋 Text Comparison**
- **Original Text** - Teks asli yang diinput
- **AI Corrected Version** - Versi yang sudah dikoreksi AI

### 🎯 Overall Score
- Score 0-5 berdasarkan kriteria TOEFL
- **Model information** ditampilkan bersama score
- Ditampilkan prominently di bagian atas results

## 🤖 Model Comparison

### **Alysa Model (LanguageTool + Transformers)**
- **Pros**: 
  - Fast local processing
  - Detailed grammar analysis
  - Consistent results
  - No API costs
- **Cons**: 
  - Limited to predefined rules
  - Less contextual understanding

### **Gemini Model (Google AI)**
- **Pros**: 
  - Advanced AI understanding
  - Contextual analysis
  - Natural language feedback
  - Comprehensive evaluation
- **Cons**: 
  - Requires internet connection
  - API costs (if applicable)
  - Variable response times

## 🧪 Testing Scenarios

### Scenario 1: Good Writing
```
Input: Well-structured essay dengan grammar yang benar
Expected: High score (4-5), minimal grammar errors, high coherence
```

### Scenario 2: Grammar Issues
```
Input: Text dengan grammar errors (verb agreement, articles, dll)
Expected: Lower score, detailed grammar corrections, feedback tentang grammar
```

### Scenario 3: Poor Coherence
```
Input: Kalimat-kalimat yang tidak berhubungan
Expected: Low coherence score, feedback tentang organization
```

## 🔧 Technical Details

- **Port**: 7860 (default Gradio)
- **Interface**: Web-based dengan Gradio Blocks
- **Theme**: Soft theme untuk UI yang clean
- **Real-time**: Analysis dilakukan saat tombol "Analyze" diklik

## 💡 Tips Penggunaan

1. **Test dengan sample texts** dulu untuk memahami output format
2. **Coba berbagai jenis teks** untuk melihat variasi feedback
3. **Perhatikan tab yang berbeda** untuk analisis komprehensif
4. **Gunakan Clear button** untuk reset interface

## 🎨 UI Features

- **Responsive design** dengan Gradio Blocks
- **Tabbed interface** untuk organized results
- **Color-coded buttons** (Primary untuk analyze, Secondary untuk clear)
- **Markdown formatting** untuk readable output
- **Sample text dropdown** untuk quick testing

## 🔄 Workflow

1. **Select AI Model** - Pilih Alysa atau Gemini model
2. **Input Text** - Pilih sample text atau tulis sendiri
3. **Analyze** - Klik "Analyze with AI" 
4. **Review Results** - Results ditampilkan dalam 4 tabs terpisah dengan model info
5. **Compare Models** - Test dengan model berbeda untuk comparison
6. **Clear & Repeat** - Clear dan test text lain

## 🚨 Error Handling

- Validasi input kosong
- Try-catch untuk model errors
- User-friendly error messages
- Graceful degradation jika model gagal

---

**Interface ini perfect untuk:**
- ✅ **Model Comparison** - Compare Alysa vs Gemini performance
- ✅ **Quick Testing** - Test model feedback dengan berbagai input
- ✅ **Demo Purposes** - Demo kepada stakeholders dengan 2 model options
- ✅ **Development** - Development dan debugging kedua model
- ✅ **Research** - Analyze perbedaan output antara rule-based vs AI model
- ✅ **Educational** - Learning tentang different AI approaches
