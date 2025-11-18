import typer
from typing_extensions import Annotated
from rich.console import Console
import json

from . import config as cfg_manager # Mengganti nama import untuk kejelasan

# Aplikasi utama
app = typer.Typer(
    rich_markup_mode="markdown",
    help="CLI untuk berinteraksi dengan API XL."
)

# Aplikasi sekunder untuk sub-perintah 'config'
config_app = typer.Typer(
    name="config",
    help="Mengatur atau melihat konfigurasi."
)
app.add_typer(config_app)

console = Console()

@config_app.callback()
def config_callback(ctx: typer.Context):
    """Callback untuk perintah config."""
    # Jika tidak ada sub-perintah yang dipanggil, tampilkan bantuan
    if ctx.invoked_subcommand is None:
        console.print("[bold yellow]Peringatan:[/bold yellow] Perintah 'config' memerlukan sub-perintah.")
        console.print("Gunakan `xl-cli config set --help` untuk mengatur kredensial.")
        console.print("Gunakan `xl-cli config path` untuk melihat lokasi file konfigurasi.")

@config_app.command("set")
def config_set(
    token: Annotated[str, typer.Option("--token", help="Access token akun XL Anda.")] = None,
    family: Annotated[str, typer.Option("--family", help="Kode family Anda (opsional).")] = None,
):
    """
    Mengatur kredensial seperti token akses dan kode family.
    """
    if token is None and family is None:
        console.print("[bold yellow]Peringatan:[/bold yellow] Tidak ada yang diatur. Harap gunakan opsi `--token` atau `--family`.")
        raise typer.Exit(code=1)

    current_config = cfg_manager.load_config()

    if token:
        current_config["user_details"]["access_token"] = token
        console.print("✅ Token akses berhasil disimpan.")

    if family:
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

from . import api
import time
from rich.progress import Progress
from rich.json import JSON

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
        console.print("Silakan jalankan `xl-cli config set --token \"...\"` terlebih dahulu.")
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
