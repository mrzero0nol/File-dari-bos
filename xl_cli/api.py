import requests
import time
import json
import uuid
from datetime import datetime, timezone, timedelta
from rich.console import Console

console = Console()

# --- Konstanta yang Ditiru dari Referensi ---
BASIC_AUTH = "OWZjOTdlZDEtNmEzMC00OGQ1LTk1MTYtNjBjNTNjZTNhMTM1OllEV21GNExKajlYSUt3UW56eTJlMmxiMHRKUWIyOW8z"
AX_DEVICE_ID = "92fb44c0804233eb4d9e29f838223a14"
AX_FP = "YmQLy9ZiLLBFAEVcI4Dnw9+NJWZcdGoQyewxMF/9hbfk/8GbKBg tZxqdiiam8+m2lK31E/zJQ7kjuPXpB3EE8naYL0Q8+0WLhFV1WAPl9Eg="
UA = "myXL / 8.8.0(1179); com.android.vending; (samsung; SM-N935F; SDK 33; Android 13)"
BASE_API_URL = "https://api.myxl.xlaxiata.co.id"

# --- Fungsi Helper untuk Timestamp & Header ---
def java_like_timestamp(now: datetime) -> str:
    ms2 = f"{int(now.microsecond / 10000):02d}"
    tz = now.strftime("%z")
    tz_colon = tz[:-2] + ":" + tz[-2:] if tz else "+00:00"
    return now.strftime(f"%Y-%m-%dT%H:%M:%S.{ms2}") + tz_colon

def ts_gmt7_without_colon(dt: datetime) -> str:
    dt_gmt7 = dt.astimezone(timezone(timedelta(hours=7)))
    millis = f"{int(dt_gmt7.microsecond / 1000):03d}"
    tz = dt_gmt7.strftime("%z")
    return dt_gmt7.strftime(f"%Y-%m-%dT%H:%M:%S.{millis}") + tz

def get_ciam_headers(config: dict) -> dict:
    """Header yang benar untuk permintaan ke server CIAM (Login/OTP)."""
    return {
        "Accept-Encoding": "gzip, deflate, br",
        "Authorization": f"Basic {BASIC_AUTH}",
        "Ax-Device-Id": AX_DEVICE_ID,
        "Ax-Fingerprint": AX_FP,
        "Ax-Request-At": java_like_timestamp(datetime.now(timezone.utc)),
        "Ax-Request-Device": "samsung",
        "Ax-Request-Device-Model": "SM-N935F",
        "Ax-Request-Id": str(uuid.uuid4()),
        "Ax-Substype": "PREPAID",
        "Content-Type": "application/json",
        "Host": config["api_config"]["base_ciam_url"].replace("https://", ""),
        "User-Agent": UA,
    }

# --- Fungsi API ---

def get_ax_api_signature(config: dict, ts: str, contact: str, code: str, ctype: str) -> str | None:
    """Memanggil server.py lokal untuk menghasilkan Ax-Api-Signature."""
    payload = {"ts_for_sign": ts, "contact": contact, "code": code, "contact_type": ctype}
    try:
        response = requests.post("http://localhost:5000/ax_sign", json=payload, headers={"x-api-key": config["api_config"]["api_key"]})
        response.raise_for_status()
        return response.json().get("ax_signature")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error:[/bold red] Gagal mendapatkan AX signature: {e}")
        return None

def request_otp(config: dict, phone_number: str) -> bool:
    """Menghubungi API XL sungguhan untuk meminta OTP."""
    url = config["api_config"]["base_ciam_url"] + config["api_config"]["otp_request_path"]
    headers = get_ciam_headers(config)
    params = {"contact": phone_number, "contactType": "SMS", "alternateContact": "false"}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error:[/bold red] Gagal meminta OTP: {e}")
        if e.response: console.print(f"[bold red]Respons:[/bold red] {e.response.text}")
        return False

def validate_otp_and_get_token(config: dict, phone_number: str, otp_code: str) -> dict | None:
    """Menghubungi API XL sungguhan untuk memvalidasi OTP dan mendapatkan token."""
    url = config["api_config"]["base_ciam_url"] + config["api_config"]["otp_validate_path"]
    headers = get_ciam_headers(config)
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    ts_for_sign = ts_gmt7_without_colon(datetime.now())
    signature = get_ax_api_signature(config, ts_for_sign, phone_number, otp_code, "SMS")
    if not signature: return None
    headers["Ax-Api-Signature"] = signature

    payload = f"contactType=SMS&code={otp_code}&grant_type=password&contact={phone_number}&scope=openid"
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        response.raise_for_status()
        # Mengembalikan seluruh data token (termasuk id_token)
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error:[/bold red] Gagal memvalidasi OTP: {e}")
        if e.response: console.print(f"[bold red]Respons:[/bold red] {e.response.text}")
        return None

def encrypt_purchase_payload(config: dict, id_token: str, payload: dict) -> dict | None:
    """Memanggil server.py lokal untuk mengenkripsi payload pembelian."""
    req_body = {"id_token": id_token, "method": "POST", "path": "payments/api/v8/settlement-multipayment", "body": payload}
    try:
        response = requests.post("http://localhost:5000/xdataenc", json=req_body, headers={"x-api-key": config["api_config"]["api_key"]})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error:[/bold red] Gagal mengenkripsi payload: {e}")
        return None

def get_purchase_signature(config: dict, access_token: str, ts: int, pkg_code: str, token_payment: str) -> str | None:
    """Memanggil server.py lokal untuk mendapatkan signature pembelian."""
    payload = {
        "access_token": access_token, "sig_time_sec": ts, "package_code": pkg_code,
        "token_payment": token_payment, "payment_method": "BALANCE",
        "payment_for": "Beli Paket", "path": "payments/api/v8/settlement-multipayment"
    }
    try:
        response = requests.post(config["api_config"]["signature_server_url"], json=payload, headers={"x-api-key": config["api_config"]["api_key"]})
        response.raise_for_status()
        return response.json().get("x_signature")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error:[/bold red] Gagal mendapatkan signature pembelian: {e}")
        return None

def execute_purchase(config: dict, tokens: dict, package_code: str):
    """Mengeksekusi panggilan API pembelian ke server XL (mengikuti `balance.py`)."""
    # NOTE: Alur pembelian nyata sangat kompleks (melibatkan payment-methods, dll).
    # Ini adalah versi yang disederhanakan dan mungkin memerlukan penyesuaian.

    # 1. Enkripsi Payload
    purchase_payload = { "items": [{"item_code": package_code}], "total_amount": 0 } # Payload yang sangat disederhanakan
    encrypted_data = encrypt_purchase_payload(config, tokens['id_token'], purchase_payload)
    if not encrypted_data: return None

    # 2. Dapatkan Signature Pembelian
    ts_sec = encrypted_data["encrypted_body"]["xtime"] // 1000
    # Token payment dummy, di aplikasi asli ini didapat dari endpoint payment-methods
    token_payment_dummy = f"dummy_payment_token_{ts_sec}"
    purchase_sig = get_purchase_signature(config, tokens['access_token'], ts_sec, package_code, token_payment_dummy)
    if not purchase_sig: return None

    # 3. Bangun Header & Kirim Permintaan
    x_requested_at = datetime.fromtimestamp(ts_sec, tz=timezone.utc).astimezone()
    headers = {
        "host": BASE_API_URL.replace("https://", ""),
        "user-agent": UA,
        "x-api-key": config["api_config"]["api_key"],
        "authorization": f"Bearer {tokens['id_token']}",
        "x-hv": "v3",
        "x-signature-time": str(ts_sec),
        "x-signature": purchase_sig,
        "x-request-id": str(uuid.uuid4()),
        "x-request-at": java_like_timestamp(x_requested_at),
        "x-version-app": "8.8.0",
        "content-type": "application/json; charset=utf-8",
    }
    url = f"{BASE_API_URL}/payments/api/v8/settlement-multipayment"

    try:
        response = requests.post(url, headers=headers, data=json.dumps(encrypted_data["encrypted_body"]), timeout=30)
        response.raise_for_status()

        # Karena respons dienkripsi, kita perlu memanggil server lokal untuk dekripsi
        decrypted_response = requests.post("http://localhost:5000/xdatadec", json=response.json(), headers={"x-api-key": config["api_config"]["api_key"]})
        decrypted_response.raise_for_status()
        return decrypted_response.json().get('plaintext')

    except requests.exceptions.RequestException as e:
        console.print(f"\n[bold red]Error Pembelian:[/bold red] {e}")
        if e.response: console.print(f"   [bold]Respons Error:[/bold] {e.response.text}")
        return None
