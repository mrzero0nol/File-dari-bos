# XL-CLI: Aplikasi Baris Perintah untuk API XL

`xl-cli` adalah aplikasi baris perintah (*command-line*) yang fungsional untuk berinteraksi langsung dengan API resmi XL Axiata. Alat ini memungkinkan Anda untuk login ke akun Anda menggunakan **OTP SMS sungguhan**, mengelola konfigurasi, dan membeli paket data langsung dari terminal Anda.

## Arsitektur

Aplikasi ini menggunakan pendekatan hibrida:
- **Login**: Berinteraksi langsung dengan API CIAM resmi XL untuk alur kerja OTP SMS.
- **Tanda Tangan Kriptografi**: Menggunakan `server.py` lokal sebagai "mesin kriptografi" untuk menghasilkan `Ax-Api-Signature` yang diperlukan untuk validasi OTP, karena proses ini sangat kompleks.

## Fitur

- **Login dengan SMS Sungguhan**: Proses login interaktif yang memicu pengiriman OTP ke nomor telepon Anda melalui SMS.
- **Manajemen Sesi Otomatis**: Token akses dari server XL secara otomatis disimpan dengan aman setelah login berhasil.
- **Konfigurasi Mudah**: Atur detail sekunder seperti *family code* dengan perintah `config` yang sederhana.
- **Pembelian Paket**: Beli paket dengan perintah `purchase` yang intuitif.

---

## Cara Penggunaan

### Langkah 1: Instalasi

1.  **Prasyarat**: Pastikan Anda memiliki Python 3.7+ dan `pip` terinstal.
2.  **Kloning Repositori**: `git clone <URL_REPOSITORI_INI>`
3.  **Instalasi**: Navigasi ke direktori root proyek dan jalankan:
    ```bash
    pip install .
    ```
    Perintah ini akan membuat `xl-cli` tersedia secara global di terminal Anda.

### Langkah 2: Login ke Akun Anda

Ini adalah langkah untuk menghubungkan `xl-cli` dengan akun XL Anda. **Anda memerlukan dua terminal yang berjalan secara bersamaan.**

1.  **Jalankan Server Signature**: Di **Terminal 1**, jalankan `server.py`. Server ini **wajib** berjalan di latar belakang untuk menyediakan *signature* kriptografi yang dibutuhkan untuk login.
    ```bash
    python server.py
    ```
    Biarkan terminal ini tetap berjalan.

2.  **Jalankan Perintah Login**: Di **Terminal 2**, jalankan perintah `login`:
    ```bash
    xl-cli login
    ```
3.  **Ikuti Petunjuk**:
    *   Aplikasi akan meminta nomor telepon Anda. Masukkan nomor yang valid.
    *   `xl-cli` akan mengirim permintaan ke server XL, yang seharusnya memicu **pengiriman SMS OTP** ke ponsel Anda.
    *   Masukkan kode OTP yang Anda terima dari SMS.
4.  **Selesai!**: Jika OTP dan *signature* benar, `xl-cli` akan menyimpan token sesi Anda. Anda sekarang sudah login.

### Langkah 3: (Opsional) Atur Family Code

Jika Anda perlu menggunakan *family code* untuk pembelian, simpan kodenya sekali dengan perintah ini:
```bash
xl-cli config set --family "1b42d4f6-a76e-4986-aa5c-e2979da952f4"
```

### Langkah 4: Beli Paket

Setelah login, Anda siap untuk membeli paket. `server.py` harus **tetap berjalan** di Terminal 1.

Di **Terminal 2**, jalankan perintah `purchase` dengan kode paket yang Anda inginkan:
```bash
xl-cli purchase "internet_super_50gb"
```
Aplikasi akan secara otomatis menggunakan token Anda yang tersimpan dan berinteraksi kembali dengan `server.py` dan server XL untuk menyelesaikan transaksi.

---

### Daftar Perintah Utama

-   `xl-cli login`: Memulai sesi login interaktif dengan OTP SMS sungguhan.
-   `xl-cli purchase [KODE_PAKET]`: Membeli paket data.
-   `xl-cli config set --family "..."`: Menyimpan *family code* Anda.
-   `xl-cli config path`: Menampilkan lokasi file konfigurasi Anda.
