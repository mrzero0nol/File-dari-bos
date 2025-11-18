# XL-CLI: Aplikasi Baris Perintah untuk API XL

`xl-cli` adalah aplikasi baris perintah (*command-line*) yang modern dan ramah pengguna untuk berinteraksi dengan API XL. Alat ini memungkinkan Anda mengelola konfigurasi akun dan membeli paket data langsung dari terminal Anda.

Proyek ini meniru gaya aplikasi CLI profesional seperti `gh` atau `doctl` untuk pengalaman pengguna yang intuitif.

## Fitur

- **Instalasi Mudah**: Cukup instal sekali, dan perintah `xl-cli` akan tersedia di seluruh sistem Anda.
- **Manajemen Konfigurasi Aman**: Simpan kredensial Anda (token akses, kode keluarga) dengan aman menggunakan perintah `config`. Tidak perlu lagi mengedit file JSON secara manual.
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

### Langkah 2: Konfigurasi Akun Anda

Sebelum dapat membeli paket, Anda perlu menyimpan kredensial Anda. Cukup jalankan perintah ini sekali:
```bash
xl-cli config set --token "TOKEN_AKSES_VALID_ANDA" --family "KODE_FAMILY_ANDA"
```
-   Opsi `--family` bersifat opsional.
-   Kredensial Anda akan disimpan dengan aman di direktori konfigurasi sistem Anda (misalnya, `~/.config/xl-cli/`).

### Langkah 3: Beli Paket

1.  **Jalankan Server Lokal**: Aplikasi ini memerlukan `server.py` untuk berjalan di latar belakang guna menangani pembuatan *signature* kriptografi. Buka **Terminal 1** dan jalankan:
    ```bash
    python server.py
    ```
    Biarkan terminal ini tetap berjalan.

2.  **Beli Paket**: Sekarang, di **Terminal 2**, Anda dapat membeli paket kapan saja dengan perintah `purchase` yang sederhana:

    **Format Perintah:**
    ```bash
    xl-cli purchase [KODE_PAKET]
    ```

    **Contoh Praktis:**
    ```bash
    xl-cli purchase "internet_super_50gb"
    ```
3.  **Selesai!**: `xl-cli` akan menampilkan *progress bar* saat bekerja dan akan mencetak hasil akhir transaksi langsung di terminal Anda.

---

### Daftar Perintah

-   `xl-cli config set --token "..." --family "..."`: Menyimpan kredensial Anda.
-   `xl-cli config path`: Menampilkan lokasi file konfigurasi Anda.
-   `xl-cli purchase [KODE_PAKET]`: Membeli paket data.
