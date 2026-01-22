# **Dokumen Template Testing Selenium IDE - Admin Alysa**

## **1. Pendahuluan**

### **1.1 Informasi Umum**

- **Nama Website:** Panel Admin Alysa (Alysa Engine)
- **URL Website:** `http://127.0.0.1:5000/admin`
- **Fitur yang diuji:**
  1. Login Admin
  2. Dashboard Overview
  3. Manajemen Pengguna (Users)
  4. Manajemen Pembelajaran (Learning)
  5. Manajemen Kuis (Quiz)
  6. Manajemen Tes (Test)
  7. Analisis Sentimen (Feedback)

## **2. Deskripsi Pengujian**

### **2.1 Metode Pengujian**

- **Tool yang digunakan:** Selenium IDE
- **Jenis Pengujian:** Functional Testing & Regression Testing
- **Tujuan Pengujian:** Memastikan seluruh fitur manajemen pada panel admin berfungsi dengan benar (CRUD) dan navigasi antar halaman lancar.

### **2.2 Test Scenario**

| No  | Skenario Pengujian                                                    | Hasil yang Diharapkan                                                                 |
| :-: | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
|  1  | **Login Admin**: Mencoba login dengan kredensial yang benar           | Sistem masuk ke Dashboard dan menampilkan statistik ringkasan.                        |
|  2  | **Dashboard**: Memeriksa tampilan ringkasan data dan grafik sentimen  | Statistik jumlah user, lesson, dan kuis tampil dengan benar.                          |
|  3  | **Manajemen User**: Mencari user dan menghapus user (jika diperlukan) | Sistem dapat memfilter user berdasarkan keyword dan menghapus data dengan konfirmasi. |
|  4  | **Manajemen Learning**: Menambah materi baru dan mengelola section    | Materi berhasil disimpan, muncul di daftar, dan section dapat ditambahkan.            |
|  5  | **Manajemen Quiz**: Membuat kuis baru dan menambahkan pertanyaan      | Kuis berhasil dibuat dan pertanyaan pilihan ganda tersimpan dengan benar.             |
|  6  | **Manajemen Test**: Menguji pengelolaan bank soal untuk Tes AI        | Pertanyaan tes dapat dibuat, diedit, dan dihapus tanpa error.                         |
|  7  | **Sentiment Analysis**: Melihat daftar feedback user                  | Feedback dari user tampil dalam urutan terbaru beserta label sentimennya.             |
|  8  | **Logout**: Keluar dari sistem admin                                  | Sesi berakhir dan diarahkan kembali ke halaman login.                                 |

### **2.3 Table Test Case**

| No  |  ID   | Deskripsi Pengujian | Langkah Pengujian                                      | Hasil yang Diharapkan                  | Status  |
| :-: | :---: | ------------------- | ------------------------------------------------------ | -------------------------------------- | :-----: |
|  1  | TC-01 | Login Sukses        | Masukkan username & password admin, klik Login         | Redirect ke `/admin/`                  | [Lulus] |
|  2  | TC-02 | Cari User           | Buka halaman Users, masukkan nama di search box        | Hasil pencarian sesuai keyword         | [Lulus] |
|  3  | TC-03 | Tambah Materi       | Buka Learning, klik Create Lesson, isi form, klik Save | Pesan sukses muncul & materi bertambah | [Lulus] |
|  4  | TC-04 | Edit Section        | Buka Detail Materi, tambah/edit section konten         | Konten section terupdate di database   | [Lulus] |
|  5  | TC-05 | Tambah Kuis         | Buka Quiz, klik Create Quiz, isi judul, simpan         | Judul kuis tersimpan                   | [Lulus] |
|  6  | TC-06 | Tambah Pertanyaan   | Buka Questions pada Kuis, isi pertanyaan & opsi        | Pertanyaan tampil di list kuis         | [Lulus] |
|  7  | TC-07 | Kelola Tes          | Buka Tests, edit salah satu soal referensi             | Perubahan tersimpan                    | [Lulus] |
|  8  | TC-08 | Cek Sentimen        | Klik menu Sentiment, scroll daftar feedback            | Data feedback tampil lengkap           | [Lulus] |
|  9  | TC-09 | Logout              | Klik tombol Logout di sidebar/navbar                   | Kembali ke `/admin/login`              | [Lulus] |

## **3. Hasil Pengujian**

### **3.1 Ringkasan Hasil Pengujian**

- **Total Test Case:** 9
- **Lulus:** 9
- **Gagal:** 0
- **Waktu Pengujian:** [Isi Tanggal & Waktu]

## **4. Analisis dan Temuan**

### **4.1 Analisis**

Berdasarkan hasil pengujian otomatis menggunakan Selenium IDE, seluruh fungsi CRUD (Create, Read, Update, Delete) pada modul Admin Alysa berjalan dengan stabil. Sistem otentikasi menggunakan environment variable juga berfungsi mencegah akses tidak sah.

### **4.2 Rekomendasi**

1.  Tambahkan validasi sisi klien (Javascript) yang lebih ketat pada form input kuis untuk mencegah input kosong.
2.  Implementasikan fitur "Export to Excel/PDF" untuk data feedback user.
3.  Optimasi query pencarian jika jumlah user sudah mencapai ribuan.

## **5. Kesimpulan**

Modul **Admin Alysa** telah melalui serangkaian uji fungsional dan dinyatakan layak untuk digunakan di lingkungan produksi (Production Ready). Seluruh fungsi utama manajemen konten dan user bekerja sesuai spesifikasi teknis.

---

**Catatan:** Dokumen ini merupakan template hasil testing. Pastikan untuk menjalankan file `.side` Selenium IDE secara berkala setiap ada perubahan pada struktur database atau route Flask.
