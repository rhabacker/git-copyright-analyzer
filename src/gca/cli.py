# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import typer
from pathlib import Path
from typing_extensions import Annotated

from .database import Database
from .reports import Reports
from .scanner import Scanner

from .company.cli import app as company_app
from .company.config import CompanyConfig
from .company.mapper import CompanyMapper
from .files.cli import app as files_app
from .headers.cli import app as headers_app

DEFAULT_DATABASE = Path("gca.sqlite")

app = typer.Typer()

app.add_typer(
    company_app,
    name="company",
)

app.add_typer(
    files_app,
    name="files",
)

app.add_typer(
    headers_app,
    name="headers",
)

DatabaseOption = Annotated[
    Path,
    typer.Option(
        "--database",
        "-d",
        help="SQLite database",
    ),
]


@app.callback()
def main(
    ctx: typer.Context,
    database: DatabaseOption = Path("gca.sqlite"),
):
    db = Database(database)

    ctx.obj = {
        "db": db,
        "reports": Reports(db),
    }


@app.command()
def init(ctx: typer.Context, repository: str):
    """Initialize database."""

    db: Database = ctx.obj["db"]

    if db.schema_version() is None:
        db.initialize()

        db.set_setting("repository_root", str(Path(repository).resolve()))
        db.commit()
        typer.echo("Initialized database.")
    else:
        db.check_version()
        typer.echo("Database already initialized.")


@app.command()
def scan(ctx: typer.Context):
    """Scan files in git repository."""

    db: Database = ctx.obj["db"]
    root = db.get_setting("repository_root")
    scanner = Scanner(root, db)
    scanner.scan()

    config = CompanyConfig.load(Path(root))
    mapper = CompanyMapper(db, config)
    mapper.run()


@app.command()
def commits(ctx: typer.Context, limit: int = 20):
    """Show commit statistics."""

    reports: Reports = ctx.obj["reports"]

    typer.echo(f"{'commit_hash':40} {'additions':>8} {'deletions':>8} {'files':>8}")
    typer.echo("-" * 80)

    for row in reports.commits(limit):
        typer.echo(
            f"{row['commit_hash'][:40]:40} "
            f"{row['additions']:10d} "
            f"{row['deletions']:10d}"
            f"{row['files']:8d} "
        )


@app.command()
def contributors(ctx: typer.Context):
    """Show contributor statistics."""

    reports: Reports = ctx.obj["reports"]

    typer.echo(
        f"{'Author':40} {'Commits':>8} {'Files':>8} {'+Lines':>10} {'-Lines':>10}"
    )
    typer.echo("-" * 80)

    for row in reports.contributors():
        typer.echo(
            f"{row['author'][:40]:40} "
            f"{row['commits']:8d} "
            f"{row['files']:8d} "
            f"{row['additions']:10d} "
            f"{row['deletions']:10d}"
        )


@app.command()
def largest_commits(ctx: typer.Context, limit: int = 20):
    """Show the largest commits."""

    reports: Reports = ctx.obj["reports"]

    typer.echo(f"{'commit_hash':40} {'additions':>8} {'deletions':>8} {'files':>8}")
    typer.echo("-" * 80)

    for row in reports.largest_commits(limit):
        typer.echo(
            f"{row['commit_hash'][:40]:40} "
            f"{row['additions']:10d} "
            f"{row['deletions']:10d} "
            f"{row['files']:>8d}  "
        )


@app.command()
def summary(ctx: typer.Context):
    """Print repository summary."""

    reports: Reports = ctx.obj["reports"]
    summary = reports.summary()

    typer.echo("Repository summary")
    typer.echo("---------------------")
    typer.echo(f"Files      : {summary['files']:8d}")
    typer.echo(f"Commits    : {summary['commits']:8d}")
    typer.echo(f"Authors    : {summary['authors']:8d}")
    typer.echo(f"Changes    : {summary['changes']:8d}")


if __name__ == "__main__":
    app()
