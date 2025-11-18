import typer
from typing_extensions import Annotated
from rich.console import Console
import json
import time
from rich.progress import Progress
from rich.json import JSON

from . import config as cfg_manager
from . import api

# Aplikasi utama
app = typer.Typer(
    rich_markup_mode="markdown",
    help="CLI untuk berinteraksi dengan API XL."
)

console = Console()

@app.command()
def login():
    """
    Memulai sesi login interaktif untuk mendapatkan token akses.
    """
    console.print("--- [bold]Login Interaktif XL-CLI[/bold] ---")
    phone_number = typer.prompt("Masukkan nomor telepon Anda (cth: 08123456789)")

    cfg = cfg_manager.load_config()

    # Langkah 1: Minta OTP
    console.print(f"Mengirim permintaan OTP ke {phone_number}...")
    if not api.request_otp(cfg, phone_number):
        raise typer.Exit(code=1)

    console.print("[bold green]✓ Permintaan OTP berhasil.[/bold green] (Dalam simulasi, OTP adalah '123456')")

    # Langkah 2: Validasi OTP
    otp_code = typer.prompt("Masukkan kode OTP yang Anda terima")

    console.print("Memvalidasi kode OTP...")
    token = api.validate_otp_and_get_token(cfg, phone_number, otp_code)

    if not token:
        console.print("[bold red]Login gagal.[/bold red]")
        raise typer.Exit(code=1)

    # Langkah 3: Simpan Token
    cfg["user_details"]["access_token"] = token
    cfg_manager.save_config(cfg)

    console.print("\n[bold green]✅ Login berhasil! Token akses Anda telah disimpan dengan aman.[/bold green]")
    console.print("Anda sekarang siap untuk menggunakan perintah `purchase`.")

# Aplikasi sekunder untuk sub-perintah 'config'
config_app = typer.Typer(
    name="config",
    help="Mengatur atau melihat konfigurasi sekunder."
)
app.add_typer(config_app)

@config_app.callback()
def config_callback(ctx: typer.Context):
    """Callback untuk perintah config."""
    if ctx.invoked_subcommand is None:
        console.print("[bold yellow]Peringatan:[/bold yellow] Perintah 'config' memerlukan sub-perintah.")
        console.print("Gunakan `xl-cli config set --help` untuk mengatur kode family.")
        console.print("Gunakan `xl-cli config path` untuk melihat lokasi file konfigurasi.")

@config_app.command("set")
def config_set(
    family: Annotated[str, typer.Option("--family", help="Kode family Anda (opsional). Format: UUID")] = None,
):
    """
    Mengatur konfigurasi sekunder seperti kode family.
    """
    if family is None:
        console.print("[bold yellow]Peringatan:[/bold yellow] Tidak ada yang diatur. Harap gunakan opsi `--family`.")
        raise typer.Exit(code=1)

    current_config = cfg_manager.load_config()

    current_config["user_details"]["family_code"] = family
    console.print("✅ Kode family berhasil disimpan.")

    cfg_manager.save_config(current_config)
    console.print("\n[bold green]Konfigurasi berhasil diperbarui![/bold green]")

@config_app.command("path")
def config_path():
    """
    Menampilkan path absolut ke file konfigurasi.
    """
    cfg_path = cfg_manager.get_config_path()
    console.print(f"{cfg_path}")

@app.command()
def purchase(
    package_code: Annotated[str, typer.Argument(help="Kode paket yang ingin dibeli.")],
):
    """
    Membeli paket internet menggunakan kredensial yang tersimpan.
    """
    # 1. Muat Konfigurasi
    cfg = cfg_manager.load_config()
    if not cfg["user_details"]["access_token"]:
        console.print("[bold red]Error:[/bold red] Token akses belum diatur.")
        console.print("Silakan jalankan `xl-cli login` terlebih dahulu.")
        raise typer.Exit(code=1)

    # Buat token pembayaran unik untuk transaksi ini
    payment_token = f"purchase_{package_code}_{int(time.time())}"

    with Progress(console=console) as progress:
        task1 = progress.add_task("[cyan]Mendapatkan signature...", total=1)

        # 2. Dapatkan Signature
        signature = api.get_signature(cfg, package_code, payment_token)
        if not signature:
            progress.stop()
            raise typer.Exit(code=1)

        progress.update(task1, advance=1, description="[green]Signature didapatkan.[/green]")

        task2 = progress.add_task("[cyan]Mengirim permintaan pembelian...", total=1)

        # 3. Lakukan Pembelian
        result = api.execute_purchase(cfg, package_code, payment_token, signature)
        if not result:
            progress.stop()
            raise typer.Exit(code=1)

        progress.update(task2, advance=1, description="[green]Pembelian selesai.[/green]")

    # 4. Tampilkan Hasil
    console.print("\n[bold green]--- Hasil Transaksi ---[/bold green]")
    console.print(JSON(json.dumps(result)))


if __name__ == "__main__":
    app()
