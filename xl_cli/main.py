import typer
from typing_extensions import Annotated
from rich.console import Console
import json
from rich.progress import Progress
from rich.json import JSON

from . import config as cfg_manager
from . import api

# Aplikasi utama
app = typer.Typer(rich_markup_mode="markdown", help="CLI untuk berinteraksi dengan API XL.")
console = Console()

@app.command()
def login():
    """Memulai sesi login interaktif untuk mendapatkan token."""
    console.print("--- [bold]Login Interaktif XL-CLI[/bold] ---")
    phone_number = typer.prompt("Masukkan nomor telepon Anda (cth: 0878xxxx)")

    cfg = cfg_manager.load_config()

    console.print(f"Mengirim permintaan OTP ke {phone_number}...")
    if not api.request_otp(cfg, phone_number):
        raise typer.Exit(code=1)

    console.print("[bold green]✓ Permintaan OTP berhasil.[/bold green] Harap periksa SMS Anda.")
    otp_code = typer.prompt("Masukkan kode OTP yang Anda terima")

    console.print("Memvalidasi kode OTP...")
    tokens = api.validate_otp_and_get_token(cfg, phone_number, otp_code)
    if not tokens:
        console.print("[bold red]Login gagal.[/bold red]")
        raise typer.Exit(code=1)

    # Simpan seluruh objek token
    cfg["user_details"]["tokens"] = tokens
    cfg_manager.save_config(cfg)

    console.print("\n[bold green]✅ Login berhasil! Sesi Anda telah disimpan.[/bold green]")

# Sub-perintah 'config'
config_app = typer.Typer(name="config", help="Mengatur konfigurasi sekunder.")
app.add_typer(config_app)

@config_app.command("set")
def config_set(family: Annotated[str, typer.Option("--family", help="Kode family Anda (format: UUID).")] = None):
    """Mengatur konfigurasi sekunder seperti kode family."""
    if family is None:
        console.print("[bold yellow]Peringatan:[/bold yellow] Tidak ada yang diatur.")
        raise typer.Exit(code=1)

    current_config = cfg_manager.load_config()
    current_config["user_details"]["family_code"] = family
    cfg_manager.save_config(current_config)
    console.print("\n[bold green]Konfigurasi berhasil diperbarui![/bold green]")

@config_app.command("path")
def config_path():
    """Menampilkan path absolut ke file konfigurasi."""
    console.print(cfg_manager.get_config_path())

@app.command()
def purchase(package_code: Annotated[str, typer.Argument(help="Kode paket yang ingin dibeli.")]):
    """Membeli paket internet menggunakan sesi yang tersimpan."""
    cfg = cfg_manager.load_config()
    tokens = cfg["user_details"].get("tokens")
    if not tokens:
        console.print("[bold red]Error:[/bold red] Anda belum login.")
        console.print("Silakan jalankan `xl-cli login` terlebih dahulu.")
        raise typer.Exit(code=1)

    with Progress(console=console) as progress:
        task = progress.add_task("[cyan]Memproses pembelian...", total=1)

        result = api.execute_purchase(cfg, tokens, package_code)

        if not result:
            progress.stop()
            raise typer.Exit(code=1)

        progress.update(task, advance=1, description="[green]Pembelian selesai.[/green]")

    console.print("\n[bold green]--- Hasil Transaksi ---[/bold green]")
    console.print(JSON(json.dumps(result)))

if __name__ == "__main__":
    app()
