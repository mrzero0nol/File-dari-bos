import requests
import time
import json
from rich.console import Console

import uuid
from datetime import datetime, timezone, timedelta

console = Console()

# --- Placeholder/Konstanta yang Ditiru dari me-cli ---
BASIC_AUTH = "OWZjOTdlZDEtNmEzMC00OGQ1LTk1MTYtNjBjNTNjZTNhMTM1OllEV21GNExKajlYSUt3UW56eTJlMmxiMHRKUWIyOW8z"
AX_DEVICE_ID = "92fb44c0804233eb4d9e29f838223a14"
AX_FP = "YmQLy9ZiLLBFAEVcI4Dnw9+NJWZcdGoQyewxMF/9hbfk/8GbKBg tZxqdiiam8+m2lK31E/zJQ7kjuPXpB3EE8naYL0Q8+0WLhFV1WAPl9Eg="
UA = "myXL / 8.8.0(1179); com.android.vending; (samsung; SM-N935F; SDK 33; Android 13"

# --- Fungsi Helper untuk Header ---
def java_like_timestamp(now: datetime) -> str:
    ms2 = f"{int(now.microsecond / 10000):02d}"
    tz = now.strftime("%z")
    tz_colon = tz[:-2] + ":" + tz[-2:] if tz else "+00:00"
    return now.strftime(f"%Y-%m-%dT%H:%M:%S.{ms2}") + tz_colon

def ts_gmt7_without_colon(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone(timedelta(hours=7)))
    else:
        dt = dt.astimezone(timezone(timedelta(hours=7)))
    millis = f"{int(dt.microsecond / 1000):03d}"
    tz = dt.strftime("%z")
    return dt.strftime(f"%Y-%m-%dT%H:%M:%S.{millis}") + tz

def get_common_headers(config: dict) -> dict:
    now = datetime.now(timezone(timedelta(hours=7)))
    return {
        "Authorization": f"Basic {BASIC_AUTH}",
        "Ax-Device-Id": AX_DEVICE_ID,
        "Ax-Fingerprint": AX_FP,
        "Ax-Request-At": java_like_timestamp(now),
        "Ax-Request-Id": str(uuid.uuid4()),
        "User-Agent": UA,
    }

# --- Fungsi API ---

def get_ax_api_signature(config: dict, ts_for_sign: str, contact: str, code: str, contact_type: str) -> str | None:
    """Memanggil server lokal untuk menghasilkan Ax-Api-Signature."""
    url = "http://localhost:5000/ax_sign"
    headers = {"Content-Type": "application/json", "x-api-key": config["api_config"]["api_key"]}
    payload = {"ts_for_sign": ts_for_sign, "contact": contact, "code": code, "contact_type": contact_type}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("ax_signature")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error:[/bold red] Gagal mendapatkan AX signature dari server lokal: {e}")
        return None

def request_otp(config: dict, phone_number: str) -> bool:
    """Menghubungi API XL sungguhan untuk meminta OTP."""
    url = config["api_config"]["base_ciam_url"] + config["api_config"]["otp_request_path"]
    headers = get_common_headers(config)
    querystring = {"contact": phone_number, "contactType": "SMS", "alternateContact": "false"}
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=30)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error:[/bold red] Gagal meminta OTP: {e}")
        return False

def validate_otp_and_get_token(config: dict, phone_number: str, otp_code: str) -> str | None:
    """Menghubungi API XL sungguhan untuk memvalidasi OTP dan mendapatkan token."""
    url = config["api_config"]["base_ciam_url"] + config["api_config"]["otp_validate_path"]

    headers = get_common_headers(config)
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    now_gmt7 = datetime.now(timezone(timedelta(hours=7)))
    ts_for_sign = ts_gmt7_without_colon(now_gmt7)

    signature = get_ax_api_signature(config, ts_for_sign, phone_number, otp_code, "SMS")
    if not signature:
        return None
    headers["Ax-Api-Signature"] = signature

    payload = f"contactType=SMS&code={otp_code}&grant_type=password&contact={phone_number}&scope=openid"
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error:[/bold red] Gagal memvalidasi OTP: {e}")
        return None

def get_signature(config: dict, package_code: str, payment_token: str) -> str | None:
    """Menghubungi server lokal untuk mendapatkan signature pembelian."""

    headers = {
        'x-api-key': config["api_config"]["api_key"],
        'Content-Type': 'application/json'
    }

    payload = {
        "access_token": config["user_details"]["access_token"],
        "sig_time_sec": int(time.time()),
        "package_code": package_code,
        "token_payment": payment_token,
        "payment_method": "pulsa",
        "payment_for": "Pembelian Paket via xl-cli",
        "path": "/api/v2/purchase"
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
        # Panggilan ini ditujukan ke API XL yang sebenarnya
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
