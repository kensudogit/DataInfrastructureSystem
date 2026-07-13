"""CLI for transform / load pipeline."""
from __future__ import annotations

from datetime import datetime

import typer
from rich import print

from packages.transformers.pipeline import load_to_postgres, transform_day

app = typer.Typer(add_completion=False, help="Transform landing data into curated marts")


@app.command("transform")
def transform(
    report_date: str = typer.Option(..., "--date", help="Report date YYYY-MM-DD"),
    load_db: bool = typer.Option(False, "--load-db", help="Also load into PostgreSQL"),
) -> None:
    day = datetime.strptime(report_date, "%Y-%m-%d").date()
    paths = transform_day(day)
    for name, path in paths.items():
        print(f"[green]wrote[/green] {name}: {path}")

    if load_db:
        load_to_postgres(day)
        print("[bold]loaded[/bold] into PostgreSQL staging/mart")


if __name__ == "__main__":
    app()
