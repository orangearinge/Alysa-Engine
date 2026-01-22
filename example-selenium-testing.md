1. # **Pendahuluan**

   ## **1.1 Informasi Umum**

- **Nama Website:** Admin Dashboard Alysa
- **URL Website:** https://web.pln.co.id
- **Fitur yang diuji:**

1. Fitur Pelanggan
2. Fitur Media
3. Fitur Hubungan Investor
4. Fitur Tentang Kami
5. Fitur Bisnis
6. Fitur Sustainability
7. Fitur Bahasa
8. Fitur Karir

9. **Deskripsi Pengujian**

   ## **2.1 Metode Pengujian**

- **Tool yang digunakan:** Selenium IDE
- **Jenis Pengujian:** Functional Testing
- **Tujuan Pengujian:** Memastikan fitur-fitur utama website berfungsi dengan baik sesuai skenario pengguna

  **2.2 Test Scenario dan Test Case**
  Table Test Scenario

| No  | Skenario Pengujian                                                                                                                    | Hasil yang diharapkan                                                                                                                                          |
| :-: | ------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|  1  | \[Skenario 1 Fitur Pelanggan: menu Pelanggan dan mulai penyambungan baru\]                                                            | Sistem menampilkan halaman Pelanggan dengan benar dan memuat sub menu Layanan Penyambungan Baru. URL berubah sesuai halaman Pelanggan dan tidak terjadi error. |
|  2  | \[Skenario 2 Fitur Media: navigasi Media dan coba akses sub bab Siaran Pers\]                                                         | Sistem menampilkan halaman Media dan sub bab Siaran Pers dengan benar sesuai navigasi yang dipilih tanpa error.                                                |
|  3  | \[Skenario 3 Fitur Hubungan Investor: navigasi Hubungan Investor dan coba akses Laporan Tahunan dan coba unduh Laporan Tahunan 2024\] | Sistem menampilkan halaman Hubungan Investor dan submenu Laporan Tahunan dengan benar, serta berhasil mengunduh Laporan Tahunan 2024 tanpa error.              |
|  4  | \[Skenario 4 Fitur Tentang Kami: navigasi Tentang Kami dan coba akses semua sub menu yang ada disana\]                                | Sistem berhasil menampilkan halaman Tentang Kami dan seluruh sub menu dapat diakses dengan baik sesuai navigasi tanpa terjadi error.                           |
|  5  | \[Skenario 5 Fitur Bisnis: navigasi Bisnis dan akses semua sub menu yang ada\]                                                        | Sistem berhasil menampilkan halaman Bisnis dan seluruh sub menu dapat diakses dengan baik sesuai navigasi tanpa terjadi error.                                 |
|  6  | \[Skenario 6 Fitur Sustainability: navigasi Sustainability, akses sub menu Laporan PKLB & CSR, dan akes pdf Laporan 2019\]            | Sistem berhasil menampilkan halaman Sustainability, submenu Laporan PKLB & CSR dapat diakses, dan file PDF Laporan Tahun 2019 berhasil dibuka tanpa error.     |
|  7  | \[Skenario 7 Fitur Bahasa: fitur ubah bahasa\]                                                                                        | Sistem berhasil merubah bahasa dari website                                                                                                                    |
|  8  | \[Skenario 8 Fitur Karir: fitur Karir dan akses semua sub menu di fitur karir\]                                                       | Sistem dapat menampilkan halaman karir dan seluruh sub menu dapat diakses tanpa terjadi error.                                                                 |

Table Test Case

|   No   | Deskripsi Pengujian     | Langkah Pengujian                                                                        | Hasil yang diharapkan                                                         |  Status   |
| :----: | ----------------------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | :-------: |
| TC-01  | Fitur Pelanggan         | Klik Fitur Pelanggan Klik menu penyambungan baru                                         | Semua menu dapat diakses tanpa error                                          | \[Lulus\] |
| TC- 02 | Fitur Media             | Klik Fitur Media Klik sub menu Siaran Pers                                               | Navigasi dan sub menu dapat diakses tanpa error                               | \[Lulus\] |
| TC-03  | Fitur Hubungan Investor | Klik Fitur Hubungan Investor Klik sub menu Laporan Tahunan Unduh Laporan Tahunan 2024    | Navigasi dan sub menu dapat diakses, dan dapat mengunduh Laporan Tahunan      | \[Lulus\] |
| TC-04  | Fitur Tentang Kami      | Klik Fitur Tentang Kami Klik Semua Sub menu yang ada                                     | Navigasi dan sub menu dapat diakses tanpa error                               | \[Lulus\] |
| TC-05  | Fitur Bisnis            | Klik Fitur Tentang Kami Klik Semua Sub menu yang ada                                     | Navigasi dan sub menu dapat diakses tanpa error                               | \[Lulus\] |
| TC-06  | Fitur Sustainability    | Klik Fitur Sustainability Klik sub menu Laporan PKLB & CSR Unduh Laporan PKLB & CSR 2019 | Navigasi dan sub menu dapat diakses, dan dapat melihat pdf Laporan PKLB & CSR | \[Lulus\] |
| TC-07  | Fitur Bahasa            | Klik fitur ubah bahasa                                                                   | Semua teks di website bisa berubah bahasanya                                  | \[Lulus\] |
| TC-08  | Fitur Karir             | Klik fitur Karir Klik semua sub menu yang ada di Karir                                   | Navigasi dan sub menu dapat diakses tanpa error                               | \[Lulus\] |

Table Test Case

|   No   | Deskripsi Pengujian     | Langkah Pengujian                                                                        | Hasil yang diharapkan                                                         |  Status   |
| :----: | ----------------------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | :-------: |
| TC-01  | Fitur Pelanggan         | Klik Fitur Pelanggan Klik menu penyambungan baru                                         | Semua menu dapat diakses tanpa error                                          | \[Lulus\] |
| TC- 02 | Fitur Media             | Klik Fitur Media Klik sub menu Siaran Pers                                               | Navigasi dan sub menu dapat diakses tanpa error                               | \[Lulus\] |
| TC-03  | Fitur Hubungan Investor | Klik Fitur Hubungan Investor Klik sub menu Laporan Tahunan Unduh Laporan Tahunan 2024    | Navigasi dan sub menu dapat diakses, dan dapat mengunduh Laporan Tahunan      | \[Lulus\] |
| TC-04  | Fitur Tentang Kami      | Klik Fitur Tentang Kami Klik Semua Sub menu yang ada                                     | Navigasi dan sub menu dapat diakses tanpa error                               | \[Lulus\] |
| TC-05  | Fitur Bisnis            | Klik Fitur Tentang Kami Klik Semua Sub menu yang ada                                     | Navigasi dan sub menu dapat diakses tanpa error                               | \[Lulus\] |
| TC-06  | Fitur Sustainability    | Klik Fitur Sustainability Klik sub menu Laporan PKLB & CSR Unduh Laporan PKLB & CSR 2019 | Navigasi dan sub menu dapat diakses, dan dapat melihat pdf Laporan PKLB & CSR | \[Lulus\] |
| TC-07  | Fitur Bahasa            | Klik fitur ubah bahasa                                                                   | Semua teks di website bisa berubah bahasanya                                  | \[Lulus\] |
| TC-08  | Fitur Karir             | Klik fitur Karir Klik semua sub menu yang ada di Karir                                   | Navigasi dan sub menu dapat diakses tanpa error                               | \[Lulus\] |

3. **Hasil Pengujian**  
   3.1. **Ringkasan Hasil Pengujian**
1. Fitur Pelanggan

1. # **Analisis dan Temuan**

   ## **4.1 Analisis**

   Berdasarkan hasil pengujian yang telah dilakukan menggunakan Selenium IDE terhadap Website Perusahaan Listrik Negara (PLN), terdapat 8 (delapan) fitur yang diuji, yaitu Fitur Pelanggan, Media, Hubungan Investor, Tentang Kami, Bisnis, Sustainability, Bahasa, dan Karir.

   Hasil pengujian menunjukkan bahwa seluruh fitur yang diuji berjalan sesuai dengan skenario pengujian yang telah ditentukan. Setiap navigasi menu utama dan sub menu dapat diakses dengan baik, halaman ditampilkan sesuai tujuan, serta fitur unduhan dokumen (PDF) berjalan dengan normal.

   Pengujian juga memastikan bahwa:

- Tidak ditemukan error pada proses navigasi antar halaman
- Tidak terjadi kegagalan saat mengakses sub menu
- File laporan berhasil dibuka dan diunduh sesuai fungsinya
- Fitur perubahan bahasa bekerja dengan baik

  Secara keseluruhan, tidak ditemukan error fungsional selama proses pengujian menggunakan Selenium IDE.

  ## **4.2 Rekomendasi**

  Berdasarkan hasil pengujian yang telah dilakukan, seluruh fitur yang diuji telah berfungsi dengan baik. Namun, beberapa rekomendasi yang dapat diberikan untuk pengembangan ke depan adalah sebagai berikut:

1. Melakukan pengujian berkala untuk memastikan kestabilan sistem setelah adanya pembaruan konten atau fitur.
2. Menambahkan pengujian non-fungsional seperti performance testing dan security testing untuk meningkatkan kualitas website.
3. Memastikan konsistensi tampilan dan aksesibilitas pada berbagai perangkat dan browser.
4. Mengembangkan automasi pengujian lanjutan untuk fitur-fitur lain yang belum diuji.  

5. **Kesimpulan**  
   Berdasarkan pengujian yang telah dilakukan terhadap Website Perusahaan Listrik Negara (PLN) menggunakan metode Functional Testing dengan tool Selenium IDE, dapat disimpulkan bahwa:

- Total fitur yang diuji: 8
- Jumlah fitur yang lulus pengujian: 8
- Jumlah fitur yang gagal pengujian: 0

  Seluruh fitur yang diuji telah berjalan sesuai dengan skenario pengujian dan tidak ditemukan error fungsional. Dengan demikian, website PLN dinyatakan layak digunakan dari sisi fungsionalitas berdasarkan skenario pengujian yang dilakukan.

  **CATATAN**

  Pengujian ini hanya mencakup pengujian fungsional pada beberapa fitur utama website PLN. Oleh karena itu, masih terdapat kemungkinan adanya bug atau permasalahan pada fitur lain yang belum diuji. Disarankan untuk melakukan pengujian lanjutan secara menyeluruh guna memastikan kualitas dan keandalan website secara keseluruhan.
