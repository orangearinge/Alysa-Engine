---
## **Struktur Database Sistem Pembelajaran Bahasa Inggris (TOEFL iBT) — Versi dengan Learning, Test, dan Task-based Feedback**
---

### 1. _users_

Menyimpan data akun pengguna.

- id — integer, primary key, auto increment
- username — text, unik, tidak boleh kosong
- email — text, unik, tidak boleh kosong
- password_hash — text, hasil hash password
- created_at — datetime, waktu pembuatan akun

---

### 2. _learning_questions_

Bank soal untuk **fitur pembelajaran (Learning Mode)**, dikelompokkan berdasarkan skill dan level.

- id — integer, primary key, auto increment
- skill_type — text, `'speaking'` atau `'writing'`
- level — integer, level kesulitan (1 = beginner, 2 = intermediate, dst.)
- prompt — text, instruksi atau teks soal
- reference_answer — text, contoh jawaban ideal (opsional)
- keywords — text, daftar kata kunci penting (format JSON)
- created_at — datetime, waktu pembuatan soal

---

### 3. _test_questions_

Bank soal untuk **simulation test (TOEFL-like)**, mencakup berbagai task_type.

- id — integer, primary key, auto increment
- section — text, `'speaking'` atau `'writing'`
- task_type — text, jenis tugas: `'independent'`, `'integrated'`, `'describe'`, `'summarize'`, dll.
- prompt — text, teks instruksi atau soal
- reference_answer — text, contoh jawaban ideal (opsional)
- keywords — text, daftar kata kunci penting (format JSON)
- created_at — datetime, waktu pembuatan soal

---

### 4. _user_attempts_

Mencatat setiap **latihan (learning)** yang dilakukan user.

- id — integer, primary key, auto increment
- user_id — integer, foreign key ke tabel _users_
- learning_question_id — integer, foreign key ke tabel _learning_questions_
- user_input — text, jawaban user
- ai_feedback — text, hasil evaluasi LLM (grammar, struktur, dsb.)
- score — float, nilai hasil evaluasi
- created_at — datetime, waktu pengerjaan

---

### 5. _test_sessions_

Mewakili satu sesi **simulasi TOEFL iBT penuh** yang diikuti user.

- id — integer, primary key, auto increment
- user_id — integer, foreign key ke tabel _users_
- total_score — float, total nilai keseluruhan sesi
- ai_feedback — text, ringkasan umpan balik keseluruhan dari LLM
- started_at — datetime, waktu mulai test
- finished_at — datetime, waktu selesai test

---

### 6. _test_answers_

Menyimpan jawaban user **berdasarkan task_type**, bukan per soal.
Setiap baris mewakili satu jenis tugas (_Independent_, _Integrated_, dll.) di satu sesi test.

- id — integer, primary key, auto increment
- test_session_id — integer, foreign key ke tabel _test_sessions_
- section — text, `'speaking'` atau `'writing'`
- task_type — text, jenis tugas: `'independent'`, `'integrated'`, `'describe'`, `'summarize'`, dll.
- combined_question_ids — text, daftar ID soal yang termasuk task ini (format JSON, contoh: `[1,2,3]`)
- user_inputs — text, semua jawaban user per soal dalam format JSON (contoh: `[{"q_id":1,"answer":"..."},{"q_id":2,"answer":"..."}]`)
- ai_feedback — text, hasil evaluasi LLM untuk seluruh task_type
- score — float, skor rata-rata untuk task_type ini
- created_at — datetime, waktu pengerjaan

---

### 7. _ocr_translations_

Menyimpan hasil proses OCR dan terjemahan lengkap (gabungan teks terjemahan dan penjelasan grammar/vocabulary).

- id — integer, primary key, auto increment
- user_id — integer, foreign key ke tabel _users_
- original_text — text, hasil teks dari gambar (bahasa Indonesia)
- translated_and_explained — text, hasil gabungan terjemahan ke Inggris + penjelasan grammar/vocabulary
- created_at — datetime, waktu pemrosesan OCR

---

### 📊 **Relasi Antar Tabel**

```
users
 ├── user_attempts → learning_questions
 ├── test_sessions
 │     └── test_answers (per task_type)
 │           └── test_questions (via combined_question_ids)
 └── ocr_translations
```
