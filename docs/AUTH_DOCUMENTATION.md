# Alysa Authentication Documentation

Sistem autentikasi Alysa menggunakan pendekatan **Hybrid Auth**, menggabungkan **Firebase Authentication** untuk manajemen identitas di sisi klien (Mobile) dan **Flask-JWT-Extended** untuk manajemen sesi aman di sisi server.

## Overview Alur Autentikasi

1. Client (Flutter) melakukan login/registrasi via Firebase.
2. Client mendapatkan **Firebase ID Token**.
3. Client mengirimkan ID Token ke Backend Alysa.
4. Backend memverifikasi token ke Firebase Admin SDK.
5. Jika valid, backend mencocokkan/membuat user di database lokal dan mengembalikan **Internal JWT Access Token**.
6. Client menggunakan internal JWT tersebut untuk request API Alysa lainnya.

---

## Endpoint API

### 1. Firebase Login / Registration

Backend secara otomatis menangani pendaftaran user baru pada login pertama (Just-In-Time Provisioning).

- **URL:** `/api/auth/firebase-login`
- **Method:** `POST`
- **Authentication:** `Bearer <Firebase_ID_Token>` (Diletakkan di header `Authorization`)

#### Request Header:

```http
Authorization: Bearer <ID_TOKEN_DARI_FIREBASE>
Content-Type: application/json
```

#### Success Response (200 OK):

Terdapat `access_token` yang digunakan untuk request selanjutnya.

```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "john.doe",
    "email": "john.doe@example.com"
  }
}
```

#### Error Response:

- **401 Unauthorized:** Token hilang, format salah, atau token Firebase tidak valid/expired.
- **400 Bad Request:** Email tidak ditemukan dalam klaim token Firebase.

---

## Logika Internal Backend

### Verifikasi Token

Backend menggunakan `firebase_admin.auth.verify_id_token(id_token)` untuk memvalidasi bahwa token tersebut benar-benar diterbitkan oleh project Firebase Alysa dan belum kadaluarsa.

### Manajemen User (Auto-Provisioning)

Jika email dari Firebase belum ada ditable `users`:

1. Sistem mengambil bagian depan email sebagai `username` dasar.
2. Jika username sudah dipakai, sistem menambahkan angka (misal: `user`, `user1`, `user2`) hingga unik.
3. User baru disimpan ke database tanpa password (karena autentikasi ditangani Firebase).

### Sesi JWT

Internal JWT yang diterbitkan memiliki masa berlaku sesuai konfigurasi:

- **Default:** 24 Jam (Dapat dikonfigurasi di `config.py` via `JWT_ACCESS_TOKEN_EXPIRES`).

---

## Komponen Terkait

- **File Route:** `app/routes/auth.py`
- **Model DB:** `User` di `app/models/database.py`
- **Konfigurasi:**
  - `JWT_SECRET_KEY`: Digunakan untuk menandatangani internal JWT.
  - `app/firebase_config.py`: Inisialisasi Firebase Admin SDK.

---

## Cara Pengujian (cURL)

```bash
curl -X POST http://localhost:5000/api/auth/firebase-login \
     -H "Authorization: Bearer YOUR_FIREBASE_ID_TOKEN"
```
