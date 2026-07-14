# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from pathlib import Path
import typer

from .config import CompanyConfig
from .discover import recommendation
from .mapper import CompanyMapper
from .prompt import CompanyPromptGenerator
from .repository import CompanyRepository
from .yaml import CompanyYamlGenerator
from ..database import Database

app = typer.Typer(help="Company mapping commands")


@app.command("companies")
def companies(ctx: typer.Context) -> None:
    """Show imported companies."""

    db: Database = ctx.obj["db"]

    repo = CompanyRepository(db)

    current = None

    for row in repo.iter_domains():
        if row["company_name"] != current:
            current = row["company_name"]

            typer.echo(current)

            if row["company_spdx_name"] != current:
                typer.echo(f"    SPDX: {row['company_spdx_name']}")

            typer.echo("    Domains:")

        typer.echo(f"        {row['domain']}")


@app.command("config")
def show_config(ctx: typer.Context) -> None:
    """Show configured companies (YAML-files)."""

    db: Database = ctx.obj["db"]

    root = db.get_setting("repository_root")

    if root is None:
        raise typer.BadParameter("No repository has been scanned yet.")

    config = CompanyConfig.load(Path(root))

    for company in sorted(config.companies(), key=lambda c: c.name.casefold()):
        typer.echo(company.name)

        if company.spdx_name != company.name:
            typer.echo(f"    SPDX: {company.spdx_name}")

        typer.echo("    Domains:")

        for domain in sorted(company.domains):
            typer.echo(f"        {domain}")


DOMAIN_WIDTH = 34
COMPANY_WIDTH = 24
STATUS_WIDTH = 10


def format_status(status: str) -> str:
    color = {
        "company": typer.colors.GREEN,
        "personal": typer.colors.BLUE,
        "unknown": typer.colors.YELLOW,
    }.get(status, typer.colors.WHITE)

    return typer.style(status.ljust(STATUS_WIDTH), fg=color)


@app.command("discover")
def discover(
    ctx: typer.Context,
    unknown: bool = typer.Option(
        False,
        "--unknown",
        help="Show only unknown domains.",
    ),
    company: bool = typer.Option(
        False,
        "--company",
        help="Show only company domains.",
    ),
    personal: bool = typer.Option(
        False,
        "--personal",
        help="Show only personal email domains.",
    ),
    prompt: bool = typer.Option(
        False,
        "--prompt",
        help="Generate an AI prompt for completing company.yaml.",
    ),
    yaml: bool = typer.Option(
        False,
        "--yaml",
        help="Generate company.yaml skeleton for unknown domains.",
    ),
) -> None:
    """Discover email domains found in the repository."""

    db: Database = ctx.obj["db"]

    root = db.get_setting("repository_root")
    config = CompanyConfig.load(Path(root)) if root else CompanyConfig.load()

    repo = CompanyRepository(db)

    rows = []

    for row in repo.iter_discover():
        domain = row["domain"]

        if domain in config.personal_domains():
            status = "personal"
            company_name = "-"

        else:
            company = config.company_for_domain(domain)

            if company is None:
                status = "unknown"
                company_name = "-"
            else:
                status = "company"
                company_name = company.name

        if unknown and status != "unknown":
            continue

        if company and status != "company":
            continue

        if personal and status != "personal":
            continue

        recommend = recommendation(
            domain=domain,
            commits=row["commits"],
            authors=row["authors"],
            status=status,
        )

        rows.append(
            (
                row,
                status,
                company_name,
                recommend,
            )
        )

    if prompt:
        text = CompanyPromptGenerator().generate(config, rows)
        typer.echo(text)
        return

    if yaml:
        text = CompanyYamlGenerator().generate(config, rows)
        typer.echo(text)
        return

    typer.echo(
        f"{'Commits':>7} "
        f"{'Authors':>7} "
        f"{'Domain':{DOMAIN_WIDTH}} "
        f"{'Status':10} "
        f"{'Recommendation':16} "
        f"{'Company':{COMPANY_WIDTH}} "
        "Example"
    )

    typer.echo("-" * 120)

    for row, status, company_name, recommend in rows:
        status_text = format_status(status)
        typer.echo(
            f"{row['commits']:7d} "
            f"{row['authors']:7d} "
            f"{row['domain']:{DOMAIN_WIDTH}} "
            f"{status_text} "
            f"{recommend:16} "
            f"{company_name:{COMPANY_WIDTH}} "
            f"{row['example_author']} <{row['example_email']}>"
        )


@app.command("import")
def import_companies(ctx: typer.Context) -> None:
    """Import configured companies."""

    db: Database = ctx.obj["db"]

    root = db.get_setting("repository_root")
    if root is None:
        raise typer.BadParameter("No repository has been scanned yet.")

    cfg = CompanyConfig.load(Path(root))

    repo = CompanyRepository(db)
    repo.import_config(cfg)

    typer.echo(f"Imported {len(list(cfg.companies()))} companies.")


@app.command("map")
def map_companies(ctx: typer.Context) -> None:
    """Map authors to companies."""

    db: Database = ctx.obj["db"]

    root = db.get_setting("repository_root")

    if root is None:
        raise typer.BadParameter("No repository has been scanned yet.")

    config = CompanyConfig.load(Path(root))
    mapper = CompanyMapper(db, config)
    mapped = mapper.run()

    typer.echo(f"Mapped {mapped} authors.")


@app.command("mappings")
def mappings(ctx: typer.Context) -> None:
    """Show author/company mappings."""

    db: Database = ctx.obj["db"]

    repo = CompanyRepository(db)

    current = None

    for row in repo.iter_mappings():
        if row["company_name"] != current:
            current = row["company_name"]
            typer.echo(current)

        typer.echo(f"    {row['author_name']} <{row['author_email']}>")


@app.command("stats")
def stats(
    ctx: typer.Context,
    unknown: bool = typer.Option(
        False,
        "--unknown",
        help="Show only unknown domains.",
    ),
) -> None:
    """Show email domain statistics."""

    db: Database = ctx.obj["db"]
    repo = CompanyRepository(db)

    root = db.get_setting("repository_root")
    config = CompanyConfig.load(Path(root)) if root else CompanyConfig.load()

    typer.echo(
        f"{'Commits':>7} "
        f"{'Authors':>7} "
        f"{'Type':10} "
        f"{'Company':25} "
        "Domain"
    )
    typer.echo("-" * 80)

    for row in repo.iter_domain_stats():
        if row["company_name"] is not None:
            kind = "company"
        elif row["domain"] in config.personal_domains():
            kind = "personal"
        else:
            kind = "unknown"

        if unknown and kind != "unknown":
            continue

        company = row["company_name"] or "-"

        typer.echo(
            f"{row['commits']:7d} "
            f"{row['authors']:7d} "
            f"{kind:10} "
            f"{company:25} "
            f"{row['domain']}"
        )
