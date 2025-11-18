# Skrip Pembelian Paket XL (Versi Ramah Pengguna)

Repositori ini menyediakan seperangkat alat untuk mengotomatiskan pembelian paket XL, termasuk yang menggunakan *family code*. Prosesnya telah disederhanakan agar mudah digunakan.

## Fitur
- **Pengaturan Satu Kali**: Simpan detail akun Anda (token, kode keluarga) sekali saja dalam file `config.json`.
- **Skrip Terpadu**: Satu perintah sederhana (`purchase.py`) untuk menangani seluruh proses pembelian.
- **Otomatisasi Penuh**: Skrip secara otomatis mendapatkan *signature* keamanan dan mengirim permintaan pembelian.

---

## Cara Penggunaan (3 Langkah Mudah)

### Langkah 1: Instalasi Dependensi

Pastikan Anda memiliki semua *library* Python yang dibutuhkan. Buka terminal dan jalankan:
```bash
pip install Flask pycryptodome requests
```

### Langkah 2: Konfigurasi Akun Anda

1.  Salin file `config.template.json` menjadi file baru bernama `config.json`.
    ```bash
    cp config.template.json config.json
    ```
2.  Buka `config.json` dengan editor teks.
3.  Isi `access_token` dan `family_code` dengan data asli dari akun XL Anda. Simpan file tersebut.

### Langkah 3: Beli Paket

1.  **Jalankan Server Lokal**: Di **Terminal 1**, jalankan server keamanan. Cukup jalankan sekali dan biarkan tetap berjalan di latar belakang.
    ```bash
    python server.py
    ```
2.  **Jalankan Skrip Pembelian**: Di **Terminal 2**, jalankan skrip `purchase.py` diikuti dengan kode paket yang ingin Anda beli.

    **Format Perintah:**
    ```bash
    python purchase.py [KODE_PAKET]
    ```

    **Contoh Praktis:**
    ```bash
    python purchase.py "internet_super_50gb"
    ```
3.  **Selesai!**: Skrip akan secara otomatis melakukan proses dua langkah (mendapatkan *signature* dan mengirim permintaan pembelian) dan akan menampilkan hasil akhirnya, baik itu sukses atau gagal.

---

### Komponen Sistem

- **`purchase.py`**: Skrip utama yang Anda gunakan untuk membeli paket.
- **`config.json`**: File tempat Anda menyimpan pengaturan pribadi Anda. (File ini tidak akan diunggah ke Git).
- **`server.py`**: Server lokal yang berjalan di latar belakang untuk membuat *signature* keamanan.
- **`decrypted_pycode.py`**: Modul internal yang digunakan untuk keperluan kompatibilitas.
