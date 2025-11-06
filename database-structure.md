**Struktur Database Sistem Pembelajaran Bahasa Inggris (TOEFL iBT) — Versi dengan Fitur OCR & Tanpa Lessons Table**

---

### 1. **users**

Menyimpan data akun pengguna.

* id — integer, primary key, auto increment
* username — text, unik, tidak boleh kosong
* email — text, unik, tidak boleh kosong
* password_hash — text, hasil hash password
* created_at — datetime, waktu pembuatan akun

---

### 2. **user_attempts**

Mencatat setiap latihan yang dilakukan user (speaking atau writing).

* id — integer, primary key, auto increment
* user_id — integer, foreign key ke tabel users
* question_title — text, judul atau nama soal (karena soal di-hardcode)
* user_input — text, jawaban user
* ai_feedback — text, hasil evaluasi model AI (grammar, struktur, dsb.)
* score — float, nilai hasil evaluasi
* created_at — datetime, waktu pengerjaan

---

### 3. **test_sessions**

Mewakili sesi simulasi TOEFL iBT penuh untuk tiap user.

* id — integer, primary key, auto increment
* user_id — integer, foreign key ke tabel users
* total_score — float, total nilai keseluruhan sesi
* ai_feedback — text, ringkasan umpan balik keseluruhan dari AI
* started_at — datetime, waktu mulai test
* finished_at — datetime, waktu selesai test

---

### 4. **ocr_translations**

Menyimpan hasil proses OCR dan hasil terjemahan lengkapnya (gabungan teks terjemahan dan penjelasan).

* id — integer, primary key, auto increment
* user_id — integer, foreign key ke tabel users
* original_text — text, hasil teks dari gambar (bahasa Indonesia)
* translated_and_explained — text, hasil gabungan terjemahan ke Inggris + penjelasan grammar/vocabulary
* created_at — datetime, waktu pemrosesan OCR

---

Struktur ini sudah siap dipakai untuk versi awal:

* Soal disediakan langsung (hardcoded) di kode.
* Semua input dan hasil analisis AI tersimpan di `user_attempts` atau `test_sessions`.
* Fitur OCR menyimpan hasil teks tanpa file gambar.
