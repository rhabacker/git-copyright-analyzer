# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import typer
from ..reports import Reports

app = typer.Typer(help="Commands related to source files.")


@app.command()
def list(ctx: typer.Context, limit: int = 20):
    """Show the most frequently modified files."""

    reports: Reports = ctx.obj["reports"]

    typer.echo(f"{'Revisions':>10} {'+Lines':>10} {'-Lines':>10}  Path")
    typer.echo("-" * 90)

    for row in reports.files.files(limit):
        typer.echo(
            f"{row['revisions']:10d} "
            f"{row['additions']:10d} "
            f"{row['deletions']:10d}  "
            f"{row['path']}"
        )


@app.command()
def contributors(ctx: typer.Context, path: str):
    """Show contributors for a single file."""

    reports: Reports = ctx.obj["reports"]

    typer.echo(f"Contributors for {path}\n")

    typer.echo(f"{'Author':40} {'Commits':>8} {'+Lines':>10} {'-Lines':>10}")
    typer.echo("-" * 75)

    for row in reports.files.contributors(path):
        typer.echo(
            f"{row['author'][:40]:40} "
            f"{row['commits']:8d} "
            f"{row['additions']:10d} "
            f"{row['deletions']:10d}"
        )
