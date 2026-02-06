Tentu, ini adalah versi yang sudah dipoles khusus untuk GitHub.
Versi ini memiliki struktur yang lebih profesional dengan penambahan:
 * Badges agar terlihat keren.
 * Table of Contents untuk navigasi cepat.
 * Highlighting pada bagian penting (URL, Auth).
 * Layout Tabel yang lebih rapi.
 * Emoji untuk visualisasi yang lebih menarik tapi tetap profesional.
Kamu tinggal copy kode raw di bawah ini dan paste ke file README.md di repository GitHub kamu.
# 💳 SawargiPay H2H API Documentation

![API Status](https://img.shields.io/badge/API-Active-success?style=flat-square)
![Version](https://img.shields.io/badge/Version-1.0.0-blue?style=flat-square)
![Format](https://img.shields.io/badge/Format-JSON-orange?style=flat-square)

Dokumentasi resmi untuk integrasi **Host-to-Host (H2H)** transaksi pulsa, paket data, dan PPOB menggunakan SawargiPay API. Dokumentasi ini mencakup manajemen saldo, pengecekan produk, pembuatan transaksi, dan pengecekan status.

---

## 📑 Daftar Isi

- [Konfigurasi Dasar](#-konfigurasi-dasar)
- [Autentikasi](#-autentikasi)
- [Response & Error Handling](#-response--error-handling)
- [Endpoints](#-endpoints)
  - [1. Cek Saldo](#1-cek-saldo)
  - [2. Daftar Produk](#2-daftar-produk)
  - [3. Transaksi](#3-transaksi)
  - [4. Cek Status](#4-cek-status)
- [Support](#-support)

---

## ⚙️ Konfigurasi Dasar

- **Base URL:**

https://api.sawargipay.com
- **Content-Type:** `application/json`
- **Rate Limit:** Saat ini tidak ada *hard limit*, namun harap gunakan secara wajar (*fair usage*) untuk menjaga stabilitas server.

---

## 🔐 Autentikasi

Setiap request ke API wajib menyertakan **API Key** di dalam header.

| Header Key | Value Format | Deskripsi |
| :--- | :--- | :--- |
| `Api-Key` | `String` | API Key rahasia Anda. (Hubungi CS untuk mendapatkan Key) |

**Contoh Header:**
```http
Api-Key: Minta_Sama_CS
Content-Type: application/json

📡 Response & Error Handling
Format standar response API (JSON):
{
  "status": true, // atau false
  "message": "Pesan response dari server",
  "data": { ... } // Objek atau Array data
}

Kode Status HTTP:
| Code | Status | Keterangan |
|---|---|---|
| 200 | OK | Request berhasil diproses. |
| 400 | Bad Request | Parameter input salah atau kurang. |
| 401 | Unauthorized | API Key salah, tidak dikirim, atau akun bermasalah. |
| 500 | Server Error | Terjadi kesalahan internal pada server. |
🚀 Endpoints
1. Cek Saldo
Mendapatkan informasi sisa saldo akun Anda.
 * URL: /h2h_activity/v1/saldo
 * Method: POST
<details>
<summary><b>Lihat Contoh Request & Response</b></summary>
cURL Request:
curl --location --request POST '[https://api.sawargipay.com/h2h_activity/v1/saldo](https://api.sawargipay.com/h2h_activity/v1/saldo)' \
--header 'Api-Key: YOUR_API_KEY'

Response Success:
{
  "status": true,
  "message": "Saldo berhasil diambil",
  "data": {
    "saldo": 1000000,
    "saldo_formatted": "Rp 1.000.000"
  }
}

</details>
2. Daftar Produk
Mengambil daftar layanan yang tersedia (Pulsa, Paket Data, dll).
 * URL: /h2h_activity/v1/produk
 * Method: POST
Body Parameters:
| Parameter | Type | Required | Description |
|---|---|---|---|
| kategori | string | Yes | Pilihan: "PULSA", "PAKET_DATA" |
| operator | string | No | Filter operator (e.g., "Telkomsel", "XL") |
<details>
<summary><b>Lihat Contoh Request & Response</b></summary>
cURL Request:
curl --location '[https://api.sawargipay.com/h2h_activity/v1/produk](https://api.sawargipay.com/h2h_activity/v1/produk)' \
--header 'Api-Key: YOUR_API_KEY' \
--header 'Content-Type: application/json' \
--data '{
    "kategori": "PULSA",
    "operator": "Telkomsel"
}'

Response Success:
{
  "status": true,
  "message": "Produk berhasil diambil",
  "data": [
    {
      "kode": "TSEL5",
      "nama": "Telkomsel 5.000",
      "kategori": "PULSA",
      "operator": "Telkomsel",
      "harga": 5500,
      "harga_formatted": "Rp 5.500",
      "keterangan": "Pulsa Telkomsel 5.000",
      "status": "Aktif"
    }
  ]
}

</details>
3. Transaksi
Melakukan pembelian produk (Top Up).
 * URL: /h2h_activity/v1/transaksi
 * Method: POST
Body Parameters:
| Parameter | Type | Required | Description |
|---|---|---|---|
| kategori | string | Yes | "PULSA" atau "PAKET_DATA" |
| produk_kode | string | Yes | Kode produk (didapat dari endpoint Produk) |
| tujuan | string | Yes | Nomor HP pelanggan (e.g., "081234567890") |
<details>
<summary><b>Lihat Contoh Request & Response</b></summary>
cURL Request:
curl --location '[https://api.sawargipay.com/h2h_activity/v1/transaksi](https://api.sawargipay.com/h2h_activity/v1/transaksi)' \
--header 'Api-Key: YOUR_API_KEY' \
--header 'Content-Type: application/json' \
--data '{
    "kategori": "PULSA",
    "produk_kode": "TSEL5",
    "tujuan": "081234567890"
}'

Response (Pending/Process):
{
  "status": true,
  "message": "Transaksi sedang diproses",
  "data": {
    "trx_kode": "TRX20240203001",
    "status": "pending"
  }
}

Response (Direct Success):
{
  "status": true,
  "message": "Transaksi berhasil",
  "data": {
    "trx_kode": "TRX20240203001",
    "produk_nama": "Telkomsel 5.000",
    "tujuan": "081234567890",
    "harga": 5500,
    "sn": "1234567890",
    "status": "success"
  }
}

</details>
4. Cek Status
Mengecek status transaksi real-time menggunakan Kode Transaksi.
 * URL: /h2h_activity/v1/status
 * Method: POST
Body Parameters:
| Parameter | Type | Required | Description |
|---|---|---|---|
| trx_kode | string | Yes | Kode Transaksi unik (e.g., "TRX20240203001") |
<details>
<summary><b>Lihat Contoh Request & Response</b></summary>
cURL Request:
curl --location '[https://api.sawargipay.com/h2h_activity/v1/status](https://api.sawargipay.com/h2h_activity/v1/status)' \
--header 'Api-Key: YOUR_API_KEY' \
--header 'Content-Type: application/json' \
--data '{
    "trx_kode": "TRX20240203001"
}'

Response Success:
{
  "status": true,
  "message": "Status transaksi berhasil diambil",
  "data": {
    "trx_kode": "TRX20240203001",
    "produk_nama": "Telkomsel 5.000",
    "tujuan": "081234567890",
    "harga": 5500,
    "status": "success",
    "sn": "1234567890",
    "created_at": "2024-02-03 10:30:00"
  }
}

</details>
Keterangan Status
| Status | Deskripsi |
|---|---|
| pending | Transaksi sedang dalam antrian atau proses provider. |
| success | Transaksi berhasil, pulsa masuk ke pelanggan. |
| failed | Transaksi gagal. Saldo otomatis dikembalikan (refund). |
📞 Support
Jika Anda mengalami kendala teknis atau masalah integrasi, silakan hubungi tim dukungan kami.
© 2024 SawargiPay H2H API Integration.

