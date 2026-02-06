# SawargiPay H2H API Documentation

Dokumentasi API Host-to-Host (H2H) untuk integrasi transaksi pulsa dan paket data melalui SawargiPay.

## 📋 Daftar Isi
- [Informasi Dasar](#informasi-dasar)
- [Autentikasi](#autentikasi)
- [Rate Limiting](#rate-limiting)
- [Format Response](#format-response)
- [Error Handling](#error-handling)
- [Endpoint](#endpoint)
  - [1. Saldo](#1-saldo)
  - [2. Produk](#2-produk)
  - [3. Transaksi](#3-transaksi)
  - [4. Status](#4-status)
- [Keterangan Status](#keterangan-status)
- [Support](#support)

## Informasi Dasar

| Item | Keterangan |
|------|------------|
| **Base URL** | `https://api.sawargipay.com` |
| **Content-Type** | `application/json` |
| **Format Data** | JSON |

## Autentikasi

Semua request memerlukan API Key yang valid melalui header.

```http
Api-Key: your_api_key_here
```

**Catatan:** Dapatkan API Key dengan menghubungi Customer Service SawargiPay.

## Rate Limiting

Tidak ada batasan request yang ketat saat ini, namun disarankan untuk tidak melakukan spamming request agar menjaga stabilitas server.

## Format Response

Semua response mengikuti format JSON berikut:

```json
{
  "status": true,
  "message": "Pesan response",
  "data": {}
}
```

## Error Handling

| HTTP Code | Deskripsi |
|-----------|-----------|
| 401 | Unauthorized - API Key tidak valid atau tidak ditemukan |
| 400 | Bad Request - Parameter request tidak valid |
| 500 | Internal Server Error - Kesalahan pada server |

---

## Endpoint

### 1. Saldo

#### Cek Saldo
Mendapatkan informasi saldo akun saat ini.

- **URL:** `/h2h_activity/v1/saldo`
- **Method:** `POST`

**Contoh Request:**
```bash
curl --location --request POST 'https://api.sawargipay.com/h2h_activity/v1/saldo' \
--header 'Api-Key: Minta_Sama_CS'
```

**Response Success:**
```json
{
  "status": true,
  "message": "Saldo berhasil diambil",
  "data": {
    "saldo": 1000000,
    "saldo_formatted": "Rp 1.000.000"
  }
}
```

### 2. Produk

#### Get Produk
Mengambil daftar produk berdasarkan kategori dan operator.

- **URL:** `/h2h_activity/v1/produk`
- **Method:** `POST`

**Request Body:**
| Parameter | Tipe | Wajib | Deskripsi | Nilai Valid |
|-----------|------|-------|-----------|-------------|
| `kategori` | String | Ya | Kategori produk | `"PULSA"`, `"PAKET_DATA"` |
| `operator` | String | Tidak | Filter operator | Contoh: `"Telkomsel"`, `"XL"` |

**Contoh Request:**
```bash
curl --location 'https://api.sawargipay.com/h2h_activity/v1/produk' \
--header 'Api-Key: Minta_Sama_CS' \
--header 'Content-Type: application/json' \
--data '{
    "kategori": "PULSA",
    "operator": "Telkomsel"
}'
```

**Response Success:**
```json
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
```

### 3. Transaksi

#### Beli Pulsa / Paket Data
Melakukan order pembelian pulsa atau paket data.

- **URL:** `/h2h_activity/v1/transaksi`
- **Method:** `POST`

**Request Body:**
| Parameter | Tipe | Wajib | Deskripsi | Nilai Valid |
|-----------|------|-------|-----------|-------------|
| `kategori` | String | Ya | Kategori transaksi | `"PULSA"`, `"PAKET_DATA"` |
| `produk_kode` | String | Ya | Kode produk | Contoh: `"TSEL5"` |
| `tujuan` | String | Ya | Nomor HP tujuan | Contoh: `"081234567890"` |

**Contoh Request:**
```bash
curl --location 'https://api.sawargipay.com/h2h_activity/v1/transaksi' \
--header 'Api-Key: Minta_Sama_CS' \
--header 'Content-Type: application/json' \
--data '{
    "kategori": "PULSA",
    "produk_kode": "TSEL5",
    "tujuan": "081234567890"
}'
```

**Response Success (Langsung Sukses):**
```json
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
```

**Response Pending (Sedang Diproses):**
```json
{
  "status": true,
  "message": "Transaksi sedang diproses",
  "data": {
    "trx_kode": "TRX20240203001",
    "status": "pending"
  }
}
```

### 4. Status

#### Cek Status Transaksi
Mengecek status transaksi berdasarkan kode transaksi.

- **URL:** `/h2h_activity/v1/status`
- **Method:** `POST`

**Request Body:**
| Parameter | Tipe | Wajib | Deskripsi |
|-----------|------|-------|-----------|
| `trx_kode` | String | Ya | Kode transaksi unik |

**Contoh Request:**
```bash
curl --location 'https://api.sawargipay.com/h2h_activity/v1/status' \
--header 'Api-Key: Minta_Sama_CS' \
--header 'Content-Type: application/json' \
--data '{
    "trx_kode": "TRX20240203001"
}'
```

**Response Success:**
```json
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
```

## Keterangan Status

Berikut adalah kemungkinan nilai status yang dikembalikan:

| Status | Deskripsi |
|--------|-----------|
| `pending` | Transaksi sedang diproses oleh sistem/provider |
| `success` | Transaksi berhasil, SN (Serial Number) sudah keluar |
| `failed` | Transaksi gagal (saldo otomatis direfund jika terpotong) |

## Support

Untuk bantuan teknis lebih lanjut, silakan hubungi tim support SawargiPay.

---
**Dokumentasi Versi:** 2.0  
**Terakhir diperbarui:** 2024
