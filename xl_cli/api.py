import requests
import time
import json
from rich.console import Console

console = Console()

def get_signature(config: dict, package_code: str, payment_token: str) -> str | None:
    """Menghubungi server lokal untuk mendapatkan signature."""

    headers = {
        'x-api-key': config["api_config"]["api_key"],
        'Content-Type': 'application/json'
    }

    payload = {
        "access_token": config["user_details"]["access_token"],
        "sig_time_sec": int(time.time()),
        "package_code": package_code,
        "token_payment": payment_token,
        "payment_method": "pulsa",  # Asumsi dari skrip sebelumnya
        "payment_for": "Pembelian Paket via xl-cli",
        "path": "/api/v2/purchase" # Asumsi dari skrip sebelumnya
    }

    try:
        response = requests.post(config["api_config"]["signature_server_url"], headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        signature_data = response.json()

        if 'x_signature' in signature_data:
            return signature_data['x_signature']
        else:
            console.print("[bold red]Error:[/bold red] Respons dari server signature tidak valid.")
            return None

    except requests.exceptions.ConnectionError:
        console.print(f"\n[bold red]Error:[/bold red] Gagal terhubung ke server signature lokal di [cyan]{config['api_config']['signature_server_url']}[/cyan].")
        console.print("💡 Pastikan Anda sudah menjalankan `python server.py` di terminal lain.")
        return None
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error:[/bold red] Terjadi kesalahan saat meminta signature: {e}")
        return None

def execute_purchase(config: dict, package_code: str, payment_token: str, signature: str):
    """Mengeksekusi panggilan API pembelian ke server XL."""

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
            "paymentMethod": "pulsa",
            "paymentFor": "Pembelian Paket via xl-cli",
        },
        "familyCode": config["user_details"].get("family_code") or None
    }

    if not payload["familyCode"]:
        del payload["familyCode"]

    try:
        response = requests.post(config["api_config"]["xl_purchase_url"], headers=headers, json=payload, timeout=15)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        console.print(f"\n[bold red]Error Pembelian:[/bold red] {e}")
        if e.response is not None:
            console.print(f"   [bold]Kode Status:[/bold] {e.response.status_code}")
            try:
                error_body = e.response.json()
                console.print("   [bold]Pesan Error dari Server:[/bold]")
                console.print(json.dumps(error_body, indent=2))
            except json.JSONDecodeError:
                console.print(f"   [bold]Respons Error (Teks):[/bold] {e.response.text}")
        return None
