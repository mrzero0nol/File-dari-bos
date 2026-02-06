# 🚀 SawargiPay H2H API Documentation

Dokumentasi resmi untuk integrasi Host-to-Host (H2H) transaksi pulsa dan paket data.

> [!IMPORTANT]
> **Base URL:** `https://api.sawargipay.com`
>
> **Content-Type:** `application/json`

## 🔐 Autentikasi

Setiap request ke API harus menyertakan **API Key** di dalam Header.

| Header Key | Value | Deskripsi |
| :--- | :--- | :--- |
| `Api-Key` | `YOUR_SECRET_API_KEY` | Dapatkan API Key dengan menghubungi CS. |

> [!NOTE]
> **Rate Limiting:** Saat ini tidak ada batasan ketat, namun harap gunakan dengan bijak untuk menjaga stabilitas server.

---

## 📚 Daftar Endpoint

### 1. 💰 Cek Saldo
Mendapatkan informasi sisa saldo akun Anda.

- **Method:** `POST`
- **Endpoint:** `/h2h_activity/v1/saldo`

**Contoh Request (cURL):**
```bash
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

2. 📦 Daftar Produk
Mengambil daftar produk tersedia berdasarkan kategori dan operator.
 * Method: POST
 * Endpoint: /h2h_activity/v1/produk
Parameter Body:
| Parameter | Tipe | Wajib | Contoh |
|---|---|---|---|
| kategori | string | Ya | "PULSA", "PAKET_DATA" |
| operator | string | Tidak | "Telkomsel", "XL" |
Contoh Request:
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

3. ⚡ Transaksi (Top Up)
Melakukan pembelian pulsa atau paket data.
 * Method: POST
 * Endpoint: /h2h_activity/v1/transaksi
Parameter Body:
| Parameter | Tipe | Wajib | Deskripsi |
|---|---|---|---|
| kategori | string | Ya | "PULSA" atau "PAKET_DATA" |
| produk_kode | string | Ya | Kode produk (misal: TSEL5) |
| tujuan | string | Ya | Nomor HP pelanggan (misal: 081234567890) |
Contoh Request:
curl --location '[https://api.sawargipay.com/h2h_activity/v1/transaksi](https://api.sawargipay.com/h2h_activity/v1/transaksi)' \
--header 'Api-Key: YOUR_API_KEY' \
--header 'Content-Type: application/json' \
--data '{
    "kategori": "PULSA",
    "produk_kode": "TSEL5",
    "tujuan": "081234567890"
}'

Response Success:
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

4. 🔄 Cek Status Transaksi
Mengecek status terakhir dari transaksi yang telah dilakukan.
 * Method: POST
 * Endpoint: /h2h_activity/v1/status
Parameter Body:
| Parameter | Tipe | Wajib | Deskripsi |
|---|---|---|---|
| trx_kode | string | Ya | ID Transaksi (misal: TRX2024...) |
Contoh Request:
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

🛠 Kode Status & Error
API menggunakan HTTP Status Code standar dan field status di dalam JSON.
| Status | HTTP Code | Keterangan |
|---|---|---|
| success | 200 | Transaksi sukses, SN tersedia. |
| pending | 200 | Transaksi sedang diproses provider. |
| failed | 200 | Transaksi gagal, saldo direfund. |
| error | 401 | Unauthorized: API Key salah/tidak ada. |
| error | 400 | Bad Request: Parameter input salah. |
| error | 500 | Server Error: Kesalahan internal server. |

