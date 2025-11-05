# 🤖 Gemini AI Model Setup

Panduan untuk mengkonfigurasi Google Gemini AI model dalam aplikasi TOEFL feedback.

## 🔑 API Key Setup

### 1. **Dapatkan API Key**
1. Kunjungi [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Login dengan Google account
3. Create new API key
4. Copy API key yang dihasilkan

### 2. **Set Environment Variable**

**Option A: Terminal (Temporary)**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

**Option B: .env File (Recommended)**
1. Buat file `.env` di root directory:
```bash
touch .env
```

2. Tambahkan API key ke `.env`:
```
GEMINI_API_KEY=your_api_key_here
```

**Option C: System Environment (Permanent)**
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

## 🔄 Mode Operasi

### **With API Key (Real Gemini)**
- Menggunakan Google Gemini Pro model
- Advanced AI analysis
- Contextual understanding
- Natural language feedback

### **Without API Key (Mock Mode)**
- Fallback ke mock response
- Basic pattern matching
- Rule-based analysis
- Tetap functional untuk testing

## 🧪 Testing

### **Test dengan Mock Mode**
```bash
# Tanpa set API key
python gradio_app.py
# Pilih "Gemini Model" - akan menggunakan mock response
```

### **Test dengan Real Gemini**
```bash
# Set API key dulu
export GEMINI_API_KEY="your_key"
python gradio_app.py
# Pilih "Gemini Model" - akan menggunakan real Gemini API
```

## 🔍 Verifikasi Setup

Cek apakah API key terdeteksi:
```python
import os
print("API Key configured:", "Yes" if os.getenv('GEMINI_API_KEY') else "No")
```

## 💡 Tips

1. **Jangan commit API key** ke repository
2. **Gunakan .env file** untuk development
3. **Mock mode** tetap berguna untuk testing tanpa API costs
4. **Rate limits** - Gemini API memiliki rate limiting
5. **Error handling** - aplikasi akan fallback ke mock jika API gagal

## 🚨 Troubleshooting

### **Import Error**
```bash
pip install google-generativeai==0.3.2
```

### **API Key Not Found**
- Cek environment variable: `echo $GEMINI_API_KEY`
- Restart terminal setelah set environment
- Pastikan .env file di root directory

### **API Rate Limit**
- Tunggu beberapa menit
- Gunakan mock mode untuk testing
- Check quota di Google AI Studio

### **Network Error**
- Cek koneksi internet
- Aplikasi akan fallback ke mock mode

## 📊 Comparison: Real vs Mock

| Feature | Real Gemini | Mock Mode |
|---------|-------------|-----------|
| **Analysis Quality** | Advanced AI | Basic patterns |
| **Response Time** | Variable (API) | Fast (local) |
| **Cost** | API usage | Free |
| **Internet** | Required | Not required |
| **Accuracy** | High | Limited |
| **Consistency** | Variable | Consistent |

## 🔐 Security

- **Never hardcode** API keys in source code
- **Use environment variables** or secure vaults
- **Rotate keys** periodically
- **Monitor usage** di Google Cloud Console

---

**Note**: Mock mode memungkinkan aplikasi tetap functional tanpa API key, perfect untuk development dan testing!
