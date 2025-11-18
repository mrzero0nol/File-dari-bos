# XL-CLI: Aplikasi Baris Perintah untuk API XL

`xl-cli` adalah aplikasi baris perintah (*command-line*) yang modern dan ramah pengguna untuk berinteraksi dengan API XL. Alat ini memungkinkan Anda untuk login menggunakan OTP, mengelola konfigurasi akun, dan membeli paket data langsung dari terminal Anda.

Proyek ini meniru gaya aplikasi CLI profesional seperti `gh` atau `doctl` untuk pengalaman pengguna yang intuitif.

## Fitur

- **Login Interaktif**: Proses login berbasis OTP yang mudah digunakan. Cukup jalankan `xl-cli login`, dan aplikasi akan memandu Anda.
- **Manajemen Sesi Otomatis**: Token akses secara otomatis disimpan dengan aman setelah login berhasil. Tidak perlu lagi menyalin-tempel token secara manual.
- **Konfigurasi Mudah**: Atur detail sekunder seperti *family code* dengan perintah `config` yang sederhana.
- **Perintah Intuitif**: Beli paket dengan perintah sederhana seperti `xl-cli purchase [KODE_PAKET]`.
- **Umpan Balik Interaktif**: Dilengkapi dengan *progress bar* dan output yang diformat dengan baik untuk kejelasan.

---

## Cara Penggunaan

### Langkah 1: Instalasi

1.  **Prasyarat**: Pastikan Anda memiliki Python 3.7+ dan `pip` terinstal.
2.  **Kloning Repositori**: Jika Anda belum melakukannya, kloning repositori ini ke mesin lokal Anda.
3.  **Instalasi**: Navigasi ke direktori root proyek dan jalankan perintah berikut. Tanda `.` mengacu pada direktori saat ini.
    ```bash
    pip install .
    ```
    Perintah ini akan menginstal `xl-cli` dan semua dependensinya. Sekarang perintah `xl-cli` akan tersedia secara global di terminal Anda.

### Langkah 2: Login ke Akun Anda

Ini adalah langkah paling penting. Anda hanya perlu melakukannya sekali untuk memulai sesi.

1.  **Jalankan Server Lokal**: `xl-cli` memerlukan `server.py` untuk berjalan di latar belakang guna mensimulasikan API login dan *signature*. Buka **Terminal 1** dan jalankan:
    ```bash
    python server.py
    ```
    Biarkan terminal ini tetap berjalan.

2.  **Jalankan Perintah Login**: Di **Terminal 2**, jalankan perintah `login`:
    ```bash
    xl-cli login
    ```
3.  **Ikuti Petunjuk**: Aplikasi akan meminta nomor telepon Anda, dan kemudian kode OTP.
    -   *Catatan Simulasi*: Server lokal akan mencetak OTP yang benar (yaitu "123456") di Terminal 1. Gunakan kode ini saat diminta.
4.  **Selesai!**: Setelah login berhasil, token akses Anda akan disimpan secara otomatis.

### Langkah 3: (Opsional) Atur Family Code

Jika Anda perlu menggunakan *family code* untuk pembelian, atur dengan perintah berikut. Ganti dengan UUID *family code* Anda yang sebenarnya.
```bash
xl-cli config set --family "1b42d4f6-a76e-4986-aa5c-e2979da952f4"
```

### Langkah 4: Beli Paket

Sekarang Anda siap untuk membeli paket kapan saja. Cukup jalankan perintah `purchase` dengan kode paket yang Anda inginkan.
```bash
xl-cli purchase "internet_super_50gb"
```
Aplikasi akan secara otomatis menggunakan token Anda yang tersimpan untuk melakukan transaksi.

---

### Daftar Perintah Utama

-   `xl-cli login`: Memulai sesi login interaktif untuk mendapatkan dan menyimpan token akses.
-   `xl-cli purchase [KODE_PAKET]`: Membeli paket data.
-   `xl-cli config set --family "..."`: Menyimpan *family code* Anda.
-   `xl-cli config path`: Menampilkan lokasi file konfigurasi Anda.
