import requests
import argparse
import json
import time

# Konfigurasi server
SERVER_URL = "http://localhost:5000/paysign"
API_KEY = "vT8tINqHaOxXbGE7eOWAhA==" # API Key harus sama dengan yang ada di server.py

def get_payment_signature(args):
    """
    Mengirim permintaan ke server untuk mendapatkan payment signature.
    """
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }

    # Endpoint di server.py membutuhkan timestamp dalam detik (epoch seconds)
    sig_time_sec = int(time.time())

    # Menggabungkan family_code ke dalam 'payment_for' jika ada,
    # karena server.py tidak memiliki field khusus untuk itu.
    payment_for_data = args.payment_for
    if args.family_code:
        payment_for_data += f" (family_code: {args.family_code})"

    payload = {
        "access_token": args.access_token,
        "sig_time_sec": sig_time_sec,
        "package_code": args.package_code,
        "token_payment": args.token_payment,
        "payment_method": args.payment_method,
        "payment_for": payment_for_data,
        "path": args.path
    }

    print(">>> Mengirim data berikut ke server untuk di-sign:")
    print(json.dumps(payload, indent=2))

    try:
        response = requests.post(SERVER_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()  # Akan error jika status code bukan 2xx (misal: 401, 500)

        response_data = response.json()
        print("\n<<< Respons dari server:")
        if 'x_signature' in response_data:
            print(f"✅ Signature berhasil dibuat: {response_data['x_signature']}")
        else:
            print("❌ Gagal mendapatkan signature. Respons server:")
            print(json.dumps(response_data, indent=2))

    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Gagal terhubung ke server di {SERVER_URL}.")
        print("💡 Pastikan Anda sudah menjalankan 'python server.py' di terminal lain.")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Terjadi error saat melakukan permintaan: {e}")
    except json.JSONDecodeError:
        print("\n❌ Error: Gagal mem-parsing respons dari server. Respons bukan JSON yang valid.")
        print(f"Raw response: {response.text}")

def main():
    """
    Fungsi utama untuk parsing argumen command-line dan menjalankan klien.
    """
    parser = argparse.ArgumentParser(
        description="CLI Client untuk mendapatkan 'payment signature' dari server.py.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("access_token", help="Access token pengguna. Contoh: 'dummy_token_123'")
    parser.add_argument("package_code", help="Kode paket yang akan dibeli. Contoh: 'internet_bulanan_10gb'")
    parser.add_argument("token_payment", help="Token unik untuk transaksi pembayaran. Contoh: 'payment_abc_456'")
    parser.add_argument("payment_method", help="Metode pembayaran. Contoh: 'pulsa'")
    parser.add_argument("payment_for", help="Deskripsi pembayaran. Contoh: 'pembelian_paket_xl'")
    parser.add_argument("path", help="Path API yang terkait. Contoh: '/api/v1/purchase'")
    parser.add_argument("--family_code", help="Kode family (opsional). Contoh: 'F12345'", default=None)

    # Menampilkan contoh penggunaan jika tidak ada argumen
    parser.epilog = """
Contoh Penggunaan:
python client.py your_access_token pkg_internet_50k payment_token_xyz pulsa pembelian_reguler /api/purchase --family_code F123
"""

    args = parser.parse_args()
    get_payment_signature(args)

if __name__ == "__main__":
    main()
