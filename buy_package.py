import requests
import argparse
import json

# !!! PENTING !!!
# URL ini adalah URL produksi asli berdasarkan file decrypted_pycode.py.
# Sesuaikan 'path' jika endpoint pembelian yang sebenarnya berbeda.
API_PURCHASE_URL = "https://api.myxl.xlaxiata.co.id/api/v2/purchase"

# API Key ini harus sesuai dengan yang diterima oleh server XL
API_KEY = "vT8tINqHaOxXbGE7eOWAhA=="

def execute_purchase(args):
    """
    Mengirim permintaan pembelian yang sebenarnya ke server XL API.
    Fungsi ini adalah TEMPLATE. Anda mungkin perlu menyesuaikan body
    permintaan (payload) sesuai dengan dokumentasi API XL yang sebenarnya.
    """

    # 1. Siapkan Headers untuk permintaan
    # Header ini biasanya berisi otentikasi dan signature.
    headers = {
        'x-api-key': API_KEY,
        'x-signature': args.signature,
        'Authorization': f'Bearer {args.access_token}', # Asumsi umum menggunakan Bearer token
        'Content-Type': 'application/json'
    }

    print(">>> Headers yang akan dikirim:")
    # Jangan print access_token atau signature di log produksi asli
    print(json.dumps({k: (v[:10] + '...' if len(v) > 10 else v) for k, v in headers.items()}, indent=2))

    # 2. Siapkan Body (Payload) Permintaan
    # Body ini berisi detail paket yang ingin dibeli.
    # Strukturnya HARUS disesuaikan dengan API XL yang sebenarnya.
    # Di sini, kita menggunakan data yang mirip dengan yang kita sign.
    payload = {
        "packageCode": args.package_code,
        "paymentDetails": {
            "paymentToken": args.token_payment,
            "paymentMethod": args.payment_method,
            "paymentFor": args.payment_for,
        },
        "familyCode": args.family_code # Field khusus untuk family code
    }

    # Menghapus familyCode dari payload jika tidak disediakan
    if not args.family_code:
        del payload["familyCode"]

    print("\n>>> Body (payload) yang akan dikirim:")
    print(json.dumps(payload, indent=2))

    # 3. Kirim Permintaan
    print(f"\n>>> Mengirim permintaan POST ke: {API_PURCHASE_URL}")
    print("... (Ini adalah simulasi, tidak ada permintaan nyata yang dikirim oleh skrip ini) ...")

    try:
        # Baris di bawah ini sekarang AKTIF dan akan mengirim permintaan nyata.
        response = requests.post(API_PURCHASE_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status() # Akan error jika status code bukan 200-299

        # Jika permintaan berhasil, cetak respons dari server
        response_data = response.json()
        print("\n<<< Respons dari server XL:")
        print(json.dumps(response_data, indent=2))

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Terjadi error saat melakukan permintaan ke API XL: {e}")
        # Jika ada respons error dari server, coba cetak isinya untuk debugging
        if e.response is not None:
            print(f"   Kode Status Error: {e.response.status_code}")
            try:
                # Coba parsing error sebagai JSON
                error_body = e.response.json()
                print("   Body Respons Error (JSON):")
                print(json.dumps(error_body, indent=2))
            except json.JSONDecodeError:
                # Jika bukan JSON, cetak sebagai teks biasa
                print(f"   Body Respons Error (Teks): {e.response.text}")


def main():
    parser = argparse.ArgumentParser(
        description="""Skrip untuk MENGEKSEKUSI pembelian paket ke API XL.
Ini adalah langkah KEDUA setelah mendapatkan signature dari client.py.""",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Argumen yang didapat dari langkah pertama (client.py)
    parser.add_argument("signature", help="Nilai 'x_signature' yang didapatkan dari menjalankan client.py.")

    # Argumen yang sama dengan yang digunakan di client.py
    parser.add_argument("access_token", help="Access token pengguna yang valid.")
    parser.add_argument("package_code", help="Kode paket yang akan dibeli.")
    parser.add_argument("token_payment", help="Token unik untuk transaksi pembayaran.")
    parser.add_argument("payment_method", help="Metode pembayaran (misal: 'pulsa').")
    parser.add_argument("payment_for", help="Deskripsi pembayaran.")
    parser.add_argument("--family_code", help="Kode family (opsional).", default=None)

    parser.epilog = """
Contoh Penggunaan:
1. Jalankan `client.py` terlebih dahulu untuk mendapatkan signature:
   python client.py "tok_123" "pkg_1" "pay_tok_1" "pulsa" "beli" "/api/purchase" --family_code "FAM1"
   >> ...
   >> ✅ Signature berhasil dibuat: [SIGNATURE_PANJANG_DARI_OUTPUT]

2. Gunakan signature tersebut untuk menjalankan skrip ini:
   python buy_package.py [SIGNATURE_PANJANG_DARI_OUTPUT] "tok_123" "pkg_1" "pay_tok_1" "pulsa" "beli" --family_code "FAM1"
"""

    args = parser.parse_args()
    execute_purchase(args)

if __name__ == "__main__":
    main()
