import json
from pathlib import Path
import os

# Tentukan lokasi penyimpanan konfigurasi yang sesuai dengan sistem operasi
APP_NAME = "xl-cli"
CONFIG_DIR = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "user_details": {
        "access_token": None,
        "family_code": None
    },
    "api_config": {
        "signature_server_url": "http://localhost:5000/paysign",
        "xl_purchase_url": "https://api.myxl.xlaxiata.co.id/api/v2/purchase",
        "api_key": "vT8tINqHaOxXbGE7eOWAhA=="
    }
}

def ensure_config_dir_exists():
    """Hanya memastikan direktori konfigurasi ada."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    """Memuat konfigurasi dari file, membuat file default jika tidak ada."""
    ensure_config_dir_exists()
    if not CONFIG_FILE.is_file():
        # Jika file tidak ada, buat dengan nilai default
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config_data):
    """Menyimpan data konfigurasi ke file."""
    ensure_config_dir_exists()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=2)

def get_config_path() -> str:
    """Mengembalikan path file konfigurasi sebagai string."""
    # Pastikan file ada sebelum mengembalikan path
    ensure_config_dir_exists()
    if not CONFIG_FILE.is_file():
        save_config(DEFAULT_CONFIG)
    return str(CONFIG_FILE)
