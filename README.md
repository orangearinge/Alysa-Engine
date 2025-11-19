# TOEFL iBT English Learning System - Backend API

Sistem pembelajaran bahasa Inggris dengan fokus pada Speaking & Writing untuk TOEFL iBT (Internet-Based Test) menggunakan Flask dan MySQL dengan integrasi AI (Alysa dan Gemini).

## Fitur Utama

### 🎓 Mode Learning
- Latihan soal speaking/writing dengan feedback AI real-time
- Pilihan model AI: Alysa (lokal) atau Gemini (cloud)
- Analisis grammar, coherence, dan scoring otomatis
- Riwayat latihan dan progress tracking

### 📝 Mode Test Simulation
- Simulasi test TOEFL iBT
- Timer countdown untuk pengalaman test yang realistis
- Scoring komprehensif dengan feedback detail
- Laporan hasil test dengan saran improvement

### 🔍 OCR Translation
- Upload gambar dengan teks bahasa Indonesia
- Ekstraksi teks otomatis menggunakan EasyOCR
- Terjemahan ke bahasa Inggris dengan penjelasan grammar
- Analisis vocabulary dan struktur kalimat

### 🔐 Admin Dashboard
- **URL**: `/admin/login`
- **Authentication**: Simple Admin Auth (Username/Password dari `.env`)
- **Fitur**:
  - CRUD (Create, Read, Update, Delete) untuk Learning Questions
  - CRUD untuk Test Questions
  - Interface modern dengan Tailwind CSS (Zinc theme)
  - Proteksi route dengan decorator `@admin_required`

## Teknologi yang Digunakan 

- **Backend**: Flask, SQLAlchemy, Flask-JWT-Extended
- **Database**: MySQL
- **AI Models**: 
  - Alysa (LanguageTool + Sentence Transformers)
  - Google Gemini API
- **OCR**: EasyOCR + PIL
- **Authentication**: JWT dengan bcrypt password hashing

## Setup dan Instalasi

### 1. Prerequisites
```bash
# Install MySQL
brew install mysql  # macOS
# atau
sudo apt-get install mysql-server  # Ubuntu

# Start MySQL service
brew services start mysql  # macOS
# atau
sudo systemctl start mysql  # Ubuntu
```

### 2. Clone Repository
```bash
git clone <repository-url>
cd alysa-engine
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy environment file
cp .env.example .env

# Edit .env file dengan konfigurasi Anda
nano .env
```

Isi file `.env`:
```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=toefl_learning
DB_PORT=3306

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key

# AI Model Configuration
GEMINI_API_KEY=your-gemini-api-key

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### 5. Database Setup
```bash
# Jalankan script inisialisasi database
python init_db.py
```

### 6. Run Application
```bash
python app.py
```

Server akan berjalan di `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/register` - Registrasi user baru
- `POST /api/login` - Login user

### Learning Mode
- `GET /api/learning/questions` - Ambil daftar soal learning
- `POST /api/learning/submit` - Submit jawaban dengan AI feedback

### Test Simulation
- `POST /api/test/start` - Mulai sesi test baru
- `POST /api/test/submit` - Submit jawaban test lengkap

### OCR Translation
- `POST /api/ocr/translate` - Upload gambar untuk OCR dan terjemahan

### User History
- `GET /api/user/attempts` - Riwayat latihan user
- `GET /api/user/test-sessions` - Riwayat test sessions
- `GET /api/user/ocr-history` - Riwayat OCR translations

### Health Check
- `GET /api/health` - Status kesehatan API

## Struktur Database

### users
- `id` - Primary key
- `username` - Username unik
- `email` - Email unik  
- `password_hash` - Password ter-hash
- `created_at` - Timestamp pembuatan

### user_attempts
- `id` - Primary key
- `user_id` - Foreign key ke users
- `question_title` - Judul soal
- `user_input` - Jawaban user
- `ai_feedback` - Feedback AI (JSON)
- `score` - Skor hasil evaluasi
- `created_at` - Timestamp pengerjaan

### test_sessions
- `id` - Primary key
- `user_id` - Foreign key ke users
- `total_score` - Total skor keseluruhan
- `ai_feedback` - Feedback keseluruhan (JSON)
- `started_at` - Waktu mulai test
- `finished_at` - Waktu selesai test

### ocr_translations
- `id` - Primary key
- `user_id` - Foreign key ke users
- `original_text` - Teks asli dari gambar
- `translated_and_explained` - Hasil terjemahan + penjelasan (JSON)
- `created_at` - Timestamp pemrosesan

## Contoh Penggunaan API

### 1. Register User
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com", 
    "password": "password123"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "password123"
  }'
```

### 3. Submit Learning Answer
```bash
curl -X POST http://localhost:5000/api/learning/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "question_id": 1,
    "answer": "My hometown is Jakarta, the capital city of Indonesia...",
    "model": "alysa"
  }'
```

### 4. Upload OCR Image
```bash
curl -X POST http://localhost:5000/api/ocr/translate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "image=@/path/to/image.jpg"
```

## Model AI yang Tersedia

### Alysa Model (Local)
- **Grammar Check**: LanguageTool untuk deteksi kesalahan grammar
- **Coherence Analysis**: Sentence Transformers untuk analisis keterkaitan antar kalimat
- **Scoring**: Algoritma heuristik berdasarkan grammar errors dan coherence
- **Kelebihan**: Cepat, tidak memerlukan internet, gratis
- **Kekurangan**: Terbatas pada aturan grammar yang sudah ada

### Gemini Model (Cloud)
- **Dynamic Analysis**: AI generatif untuk analisis komprehensif
- **Natural Feedback**: Feedback yang lebih natural dan kontekstual
- **Advanced Scoring**: Scoring yang lebih akurat berdasarkan standar TOEFL
- **Kelebihan**: Lebih akurat, feedback lebih detail dan natural
- **Kekurangan**: Memerlukan API key, bergantung pada internet

## Development

### Menjalankan dalam Mode Development
```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

### Testing
```bash
# Install testing dependencies
pip install pytest pytest-flask

# Run tests
pytest
```

### Database Migration
```bash
# Initialize migration
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

## Deployment

### Production Setup
1. Set environment variables untuk production
2. Gunakan WSGI server seperti Gunicorn
3. Setup reverse proxy dengan Nginx
4. Configure SSL certificate
5. Setup database backup strategy

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Pastikan MySQL service berjalan
   - Cek kredensial database di `.env`
   - Pastikan database sudah dibuat

2. **JWT Token Error**
   - Pastikan JWT_SECRET_KEY sudah di-set
   - Cek format Authorization header: `Bearer <token>`

3. **AI Model Error**
   - Pastikan Gemini API key valid
   - Cek koneksi internet untuk Gemini
   - Pastikan dependencies AI model ter-install

4. **OCR Error**
   - Pastikan format gambar didukung (jpg, png, etc.)
   - Cek ukuran file tidak melebihi limit
   - Pastikan gambar mengandung teks yang jelas

## Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

MIT License - lihat file LICENSE untuk detail lengkap.

## 🛠️ Penjelasan Teknis Admin CRUD

Fitur Admin Dashboard diimplementasikan menggunakan pendekatan **Server-Side Rendering (SSR)** dengan Flask `render_template` dan styling menggunakan **Tailwind CSS**.

### 1. Authentication Flow
Sistem login admin dibuat sederhana namun aman untuk kebutuhan internal:
- **Credentials**: Username dan password admin disimpan di environment variables (`ADMIN_USERNAME`, `ADMIN_PASSWORD`).
- **Session**: Menggunakan Flask `session` untuk menyimpan status login (`session['admin_logged_in'] = True`).
- **Decorator**: Custom decorator `@admin_required` dibuat untuk memproteksi route admin. Jika user belum login, akan di-redirect ke halaman login.

```python
# app/routes/question.py
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('question.admin_login'))
        return f(*args, **kwargs)
    return decorated_function
```

### 2. CRUD Implementation
Setiap entitas (LearningQuestion dan TestQuestion) memiliki set route lengkap:
- **List (GET)**: Mengambil semua data dari database dan me-render tabel.
- **Create (GET/POST)**: Menampilkan form kosong (GET) dan memproses input baru (POST).
- **Edit (GET/POST)**: Menampilkan form terisi data lama (GET) dan memproses update (POST).
- **Delete (POST)**: Menghapus data berdasarkan ID.

### 3. Frontend & Styling
- **Base Template**: `base.html` memuat CDN Tailwind CSS dan konfigurasi tema warna **Zinc**.
- **Components**: Menggunakan utility classes Tailwind untuk membuat UI yang konsisten (Card, Form Input, Button, Table).
- **Feedback**: Menggunakan Flask `flash` messages untuk notifikasi sukses/gagal operasi.

### 4. Konfigurasi
Pastikan `.env` memiliki konfigurasi berikut:
```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin
```
Jika tidak di-set, defaultnya adalah `admin` / `admin`.
