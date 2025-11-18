# Analisis Kode: Klien & Server Kriptografi

Repositori ini berisi dua skrip Python yang bekerja sama untuk mengelola komunikasi aman (terenkripsi): `server.py` dan `decrypted_pycode.py`.

---

## 1. `server.py` (Bertindak sebagai Server)

File ini adalah server web yang dibuat menggunakan **Flask**. Fungsi utamanya adalah menyediakan layanan kriptografi melalui API.

### Fungsi Utama:
- **Penyedia Layanan Kriptografi**: Menyediakan _endpoints_ untuk enkripsi (menggunakan **AES-256-CBC**) dan pembuatan tanda tangan digital (menggunakan **HMAC-SHA512**).
- **Simulasi Backend**: Bertindak sebagai backend yang mensimulasikan proses keamanan yang dibutuhkan oleh sebuah aplikasi, seperti validasi API key dan pengamanan _request body_.

### Cara Kerja:
1.  **Menjalankan Server**: Saat dieksekusi, `server.py` memulai sebuah server web yang siap menerima permintaan HTTP di port 5000.
2.  **Menyediakan Endpoints**: Memiliki beberapa URL yang bisa diakses:
    - `/xdataenc`: Untuk mengenkripsi data.
    - `/xdatadec`: Untuk mendekripsi data.
    - `/paysign`, `/bountysign`, dll: Untuk membuat _signature_ (tanda tangan) untuk berbagai jenis transaksi.
3.  **Memproses Permintaan**: Ketika sebuah permintaan masuk, server akan memvalidasi `x-api-key`, melakukan operasi kriptografi yang diminta menggunakan kunci rahasia internal, dan mengembalikan hasilnya dalam format JSON.

**Analogi**: Anggap `server.py` sebagai **brankas digital**. Anda memberikannya data, ia akan menguncinya (enkripsi) dan memberinya stempel pengaman (_signature_) sebelum mengembalikannya.

---

## 2. `decrypted_pycode.py` (Bertindak sebagai Modul Konfigurasi Klien)

File ini **bukan untuk dijalankan langsung**. Ini adalah sebuah modul konfigurasi yang diimpor oleh skrip lain (klien) untuk membantunya berkomunikasi dengan server.

### Fungsi Utama:
- **Menyimpan Kredensial**: Berisi semua konfigurasi penting seperti URL API, kunci, dan token yang dibutuhkan untuk otentikasi.
- **Menyuntikkan Header Otomatis**: Secara otomatis menambahkan _header_ HTTP khusus (`y-sig-key: onodera91`) ke setiap permintaan yang dikirim ke domain yang telah ditentukan (`crypto.mashul.ol`, `me.mashul.ol`).

### Cara Kerja (Monkey Patching):
1.  **Di-import oleh Klien**: Sebuah skrip klien akan memulai dengan `import decrypted_pycode`.
2.  **Mengatur Konfigurasi**: Seketika itu juga, semua kunci dan kredensial dimuat sebagai _environment variable_ agar mudah diakses.
3.  **Memodifikasi Library HTTP**: Bagian terpenting dari file ini adalah kemampuannya untuk memodifikasi _library_ `requests` dan `httpx` saat _runtime_. Ia "mencegat" setiap permintaan yang akan dikirim.
4.  **Menambahkan Header**: Sebelum permintaan dikirim, ia memeriksa tujuannya. Jika tujuannya adalah salah satu host yang diizinkan, ia akan **secara otomatis menambahkan _header_ `y-sig-key`**.
5.  **Melanjutkan Permintaan**: Permintaan yang sudah dimodifikasi kemudian diteruskan untuk dikirim.

**Analogi**: Anggap `decrypted_pycode.py` sebagai **asisten pribadi** untuk skrip klien. Setiap kali klien ingin mengirim surat (permintaan HTTP), asisten ini akan secara otomatis menempelkan stiker khusus (_header_) yang diperlukan agar surat itu diterima oleh server.

---

### Hubungan Keduanya

-   `decrypted_pycode.py` **menyiapkan** permintaan dari sisi klien.
-   `server.py` **menerima dan memproses** permintaan tersebut di sisi server.

Keduanya membentuk sistem sederhana untuk pengembangan dan pengujian alur kerja yang melibatkan komunikasi terenkripsi.
