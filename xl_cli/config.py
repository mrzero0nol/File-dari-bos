import json
from pathlib import Path
import os
import copy

# Tentukan lokasi penyimpanan konfigurasi yang sesuai dengan sistem operasi
APP_NAME = "xl-cli"
CONFIG_DIR = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"

# Definisikan struktur konfigurasi default yang BENAR di dalam kode
DEFAULT_CONFIG = {
    "user_details": {
        "access_token": None,
        "family_code": None
    },
    "api_config": {
        "base_ciam_url": "https://gede.ciam.xlaxiata.co.id",
        "otp_request_path": "/realms/xl-ciam/auth/otp",
        "otp_validate_path": "/realms/xl-ciam/protocol/openid-connect/token",
        "signature_server_url": "http://localhost:5000/paysign",
        "xl_purchase_url": "https://api.myxl.xlaxiata.co.id/api/v2/purchase",
        "api_key": "vT8tINqHaOxXbGE7eOWAhA=="
    }
}

def ensure_config_dir_exists():
    """Hanya memastikan direktori konfigurasi ada."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    """
    Memuat konfigurasi yang tangguh.
    Fungsi ini SECARA PAKSA menggunakan 'api_config' dari kode untuk menghindari error,
    dan hanya memuat 'user_details' dari file di disk jika ada.
    """
    ensure_config_dir_exists()

    # 1. Mulai dengan struktur default yang benar dari kode.
    final_config = copy.deepcopy(DEFAULT_CONFIG)

    # 2. Periksa apakah ada file konfigurasi di disk.
    if CONFIG_FILE.is_file():
        try:
            with open(CONFIG_FILE, 'r') as f:
                disk_config = json.load(f)

            # 3. HANYA ambil 'user_details' dari file. Abaikan 'api_config' yang mungkin usang.
            if isinstance(disk_config, dict) and "user_details" in disk_config:
                final_config["user_details"].update(disk_config["user_details"])

        except (json.JSONDecodeError, KeyError):
            # Jika file rusak atau formatnya salah, abaikan saja.
            # File akan ditimpa dengan format yang benar saat 'save_config' dipanggil.
            pass

    return final_config

def save_config(config_data):
    """Menyimpan data konfigurasi ke file."""
    ensure_config_dir_exists()
    # Pastikan data yang disimpan selalu memiliki struktur yang benar
    # Ini akan memperbaiki file yang rusak atau usang.
    full_config_to_save = copy.deepcopy(DEFAULT_CONFIG)
    full_config_to_save["user_details"].update(config_data.get("user_details", {}))

    with open(CONFIG_FILE, 'w') as f:
        json.dump(full_config_to_save, f, indent=2)

def get_config_path() -> str:
    """Mengembalikan path file konfigurasi sebagai string."""
    ensure_config_dir_exists()
    return str(CONFIG_FILE)
