from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .config import settings
from .logging_setup import setup_logging
from .metrics import read_runs
from .pipeline import run_pipeline
from .snapshot import list_snapshots
from .validate import validate_raw

app = typer.Typer(no_args_is_help=True, add_completion=False, help="ETL local — pipeline plugável.")
console = Console()


@app.command()
def run(
    input: str = typer.Option(None, "--input", "-i", help="CSV/Excel/JSON/Parquet/URL"),
    target: str = typer.Option(None, "--target", "-t", help="postgres|sqlite|parquet"),
    table: str = typer.Option(None, "--table", help="Nome da tabela/arquivo de saída"),
    mode: str = typer.Option(None, "--mode", "-m", help="replace|append|upsert"),
    no_preview: bool = typer.Option(False, "--no-preview", help="Esconde preview"),
):
    if input:
        settings.etl_input = input
    if target:
        settings.etl_target = target
    if table:
        settings.etl_table = table
    if mode:
        settings.etl_mode = mode

    metrics = run_pipeline(settings, show_preview=not no_preview)
    raise typer.Exit(code=0 if metrics.status == "success" else 1)


@app.command()
def validate(input: str = typer.Argument(..., help="Arquivo de entrada")):
    setup_logging(settings.etl_logs_dir)
    from .extract import extract

    df = extract(input)
    try:
        validate_raw(df)
        console.print(f"[green]✓ schema OK ({len(df)} linhas)[/]")
    except Exception as exc:
        console.print(f"[red]✗ schema inválido: {exc}[/]")
        raise typer.Exit(code=1) from exc


@app.command()
def runs(limit: int = typer.Option(20, help="Quantos runs mostrar")):
    from .pipeline import _metrics_url

    url = _metrics_url(settings)
    if not url:
        console.print("[yellow]sem destino SQL para ler métricas[/]")
        raise typer.Exit(1)
    df = read_runs(url, limit=limit)
    if df.empty:
        console.print("[yellow]nenhum run encontrado[/]")
        return
    t = Table(title="Últimos runs")
    for col in ("run_id", "status", "rows_in", "rows_out", "rows_rejected", "duration_seconds"):
        t.add_column(col)
    for _, row in df.iterrows():
        t.add_row(
            str(row["run_id"]),
            f"[green]{row['status']}[/]" if row["status"] == "success" else f"[red]{row['status']}[/]",
            str(row["rows_in"]),
            str(row["rows_out"]),
            str(row["rows_rejected"]),
            f"{row['duration_seconds']:.2f}s",
        )
    console.print(t)


@app.command()
def snapshots(table: str = typer.Option(None, help="Tabela a listar")):
    table = table or settings.etl_table
    items = list_snapshots(table, settings.etl_snapshots_dir)
    if not items:
        console.print(f"[yellow]nenhum snapshot para {table}[/]")
        return
    t = Table(title=f"Snapshots — {table}")
    t.add_column("arquivo")
    t.add_column("tamanho")
    for p in items:
        t.add_row(p.name, f"{p.stat().st_size / 1024:.1f} KB")
    console.print(t)


@app.command()
def dashboard(port: int = 8501):
    app_path = Path(__file__).parent.parent / "dashboard" / "app.py"
    cmd = [
        sys.executable, "-m", "streamlit", "run", str(app_path),
        "--server.port", str(port),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
    ]
    console.print(f"[cyan]→ streamlit em http://localhost:{port}[/]")
    subprocess.run(cmd, check=False)


@app.command()
def schedule(cron: str = typer.Option(None, help="Expressão cron (ex: '*/15 * * * *')")):
    from .scheduler import start_scheduler

    start_scheduler(cron or settings.etl_cron)


if __name__ == "__main__":
    app()
