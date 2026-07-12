# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import typer
from ..reports import Reports

app = typer.Typer(help="Commands related to source file headers.")


@app.command()
def list(ctx: typer.Context):
    """Show present copyright and license header."""

    reports: Reports = ctx.obj["reports"]

    for row in reports.headers.headers():
        typer.echo(f"{row['path']}:{row['line']}: {row['kind']}: {row['value']}")


@app.command()
def lint(ctx: typer.Context):
    reports: Reports = ctx.obj["reports"]

    def show(title, rows):
        if not rows:
            return

        typer.echo(title)
        typer.echo("-" * len(title))

        for row in rows:
            typer.echo(row["path"])

        typer.echo()

    show(
        "Files without copyright",
        reports.headers.missing_copyright(),
    )

    show(
        "Files without license",
        reports.headers.missing_license(),
    )

    show(
        "Files without copyright and license",
        reports.headers.missing_headers(),
    )
