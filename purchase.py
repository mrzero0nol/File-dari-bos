import requests
import argparse
import json
import time
import os
import sys

CONFIG_FILE = "config.json"

def load_config():
    """Memuat konfigurasi dari file config.json."""
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Error: File konfigurasi '{CONFIG_FILE}' tidak ditemukan.")
        print(f"💡 Silakan salin 'config.template.json' menjadi '{CONFIG_FILE}' dan isi detail Anda.")
        sys.exit(1)

    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    # Validasi sederhana
    if "GANTI_DENGAN" in config["user_details"]["access_token"]:
        print(f"❌ Error: Harap isi 'access_token' di file '{CONFIG_FILE}'.")
        sys.exit(1)

    return config

def get_signature(config, package_code, payment_token):
    """Langkah 1: Meminta signature dari server lokal."""
    print("langkah 1: Meminta signature dari server lokal...")

    headers = {
        'x-api-key': config["api_config"]["api_key"],
        'Content-Type': 'application/json'
    }

    payload = {
        "access_token": config["user_details"]["access_token"],
        "sig_time_sec": int(time.time()),
        "package_code": package_code,
        "token_payment": payment_token,
        "payment_method": config["transaction_defaults"]["payment_method"],
        "payment_for": config["transaction_defaults"]["payment_for"],
        "path": config["transaction_defaults"]["api_path"]
    }

    try:
        response = requests.post(config["api_config"]["signature_server_url"], headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        signature_data = response.json()

        if 'x_signature' in signature_data:
            print("✅ Signature berhasil didapatkan.")
            return signature_data['x_signature']
        else:
            print("❌ Gagal mendapatkan signature dari server lokal.")
            return None

    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Gagal terhubung ke server lokal di {config['api_config']['signature_server_url']}.")
        print("💡 Pastikan Anda sudah menjalankan 'python server.py' di terminal lain.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Terjadi error saat meminta signature: {e}")
        return None

def execute_purchase(config, package_code, payment_token, signature):
    """Langkah 2: Mengeksekusi pembelian ke server XL."""
    print("\nlangkah 2: Mengirim permintaan pembelian ke server XL...")

    headers = {
        'x-api-key': config["api_config"]["api_key"],
        'x-signature': signature,
        'Authorization': f'Bearer {config["user_details"]["access_token"]}',
        'Content-Type': 'application/json'
    }

    payload = {
        "packageCode": package_code,
        "paymentDetails": {
            "paymentToken": payment_token,
            "paymentMethod": config["transaction_defaults"]["payment_method"],
            "paymentFor": config["transaction_defaults"]["payment_for"],
        },
        "familyCode": config["user_details"].get("family_code") or None
    }

    if not payload["familyCode"]:
        del payload["familyCode"]

    print("   Mengirim permintaan ke:", config["api_config"]["xl_purchase_url"])
    try:
        response = requests.post(config["api_config"]["xl_purchase_url"], headers=headers, json=payload, timeout=15)
        response.raise_for_status()

        response_data = response.json()
        print("\n✅ Pembelian Berhasil!")
        print(json.dumps(response_data, indent=2))

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Pembelian Gagal: {e}")
        if e.response is not None:
            print(f"   Kode Status: {e.response.status_code}")
            try:
                error_body = e.response.json()
                print("   Pesan Error dari Server:")
                print(json.dumps(error_body, indent=2))
            except json.JSONDecodeError:
                print(f"   Respons Error (Teks): {e.response.text}")

def main():
    parser = argparse.ArgumentParser(
        description="Skrip terpadu untuk membeli paket XL.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("package_code", help="Kode paket yang ingin dibeli. Contoh: 'internet_bulanan_10gb'")

    args = parser.parse_args()

    config = load_config()

    # Buat token pembayaran unik untuk setiap transaksi
    payment_token = f"buy_{args.package_code}_{int(time.time())}"

    # Jalankan alur kerja
    signature = get_signature(config, args.package_code, payment_token)

    if signature:
        execute_purchase(config, args.package_code, payment_token, signature)

if __name__ == "__main__":
    main()
