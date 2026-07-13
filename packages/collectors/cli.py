"""CLI for advertising media collection."""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import typer
from rich import print

from packages.collectors.registry import get_all_collectors, get_collector
from packages.common.schema import MediaPlatform

app = typer.Typer(add_completion=False, help="Collect ad performance data from media APIs")


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


@app.command("collect")
def collect(
    report_date: str = typer.Option(..., "--date", help="Report date YYYY-MM-DD"),
    media: str = typer.Option("all", "--media", help="google|yahoo|meta|x|line|tiktok|all"),
) -> None:
    target_date = _parse_date(report_date)
    outputs: list[Path] = []

    if media.lower() == "all":
        collectors = get_all_collectors()
    else:
        collectors = [get_collector(MediaPlatform(media.lower()))]

    for collector in collectors:
        path = collector.collect(target_date)
        outputs.append(path)
        print(f"[green]collected[/green] {collector.media.value} -> {path}")

    print(f"[bold]done[/bold]: {len(outputs)} media files")


if __name__ == "__main__":
    app()
