# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from .company import suggested_company_id
from .config import CompanyConfig

import typer

class CompanyPromptGenerator:
    """Generate an AI prompt for completing company.yaml."""

    def generate(self, config, rows) -> str:
        lines: list[str] = []

        lines.extend(
            [
                "The following YAML contains company domains that could not be identified automatically.",
                "",
                "Task:",
                "",
                "- Determine whether each domain belongs to a company or organization.",
                "- If it does, fill in id, name and spdx_name.",
                "- Do not modify the domains list.",
                "- Use a stable company identifier for id (for example 'microsoft', not 'linux').",
                "- Prefer the legal company name.",
                "- Use the SPDX copyright holder name when known.",
                "- If you are not confident, leave the fields empty.",
                "- Do not invent information.",
                "- Return ONLY the completed YAML document.",
                "",
                "companies:",
                "",
            ]
        )

        for row, status, _, _ in rows:
            if status != "unknown":
                continue

            lines.append(f"  # commits: {row['commits']}")
            lines.append(f"  # authors: {row['authors']}")
            lines.append(
                f"  # example: {row['example_author']} <{row['example_email']}>"
            )

            lines.append("  - id:")
            lines.append("    name:")
            lines.append("    spdx_name:")
            lines.append("    domains:")
            lines.append(f"      - {row['domain']}")
            lines.append("")

        typer.echo("\n".join(lines))
        return
