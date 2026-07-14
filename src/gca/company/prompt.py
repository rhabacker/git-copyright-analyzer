# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from .company import suggested_company_id
from .config import CompanyConfig


class CompanyPromptGenerator:
    def generate(
        self,
        config: CompanyConfig,
        rows: list[tuple],
    ) -> str:
        """Generate a prompt for an AI assistant."""

        lines = []

        lines.extend(
            [
                "Determine the legal company names for the following email domains.",
                "",
                "Return YAML only.",
                "",
                "Use the following format:",
                "",
                "companies:",
                "",
                "  - id:",
                "    name:",
                "    spdx_name:",
                "    domains:",
                "",
                "Rules:",
                "",
                "- Group multiple domains belonging to the same company.",
                "- Use the official legal company name.",
                "- Use the SPDX copyright holder name if it differs.",
                "- Preserve existing company ids.",
                "- Return valid YAML only.",
                "",
                "Current configuration:",
                "",
                "companies:",
                "",
            ]
        )

        for company in sorted(config.companies(), key=lambda c: c.id):
            lines.append(f"  - id: {company.id}")
            lines.append(f"    name: {company.name}")
            lines.append(f"    spdx_name: {company.spdx_name}")
            lines.append("    domains:")

            for domain in sorted(company.domains):
                lines.append(f"      - {domain}")

            lines.append("")

        lines.extend(
            [
                "Add the following companies:",
                "",
                "companies:",
                "",
            ]
        )

        from collections import defaultdict

        companies = defaultdict(list)

        for row, status, _, recommend in rows:
            if recommend != "add company":
                continue

            companies[suggested_company_id(row["domain"])].append(row["domain"])

        for company_id in sorted(companies):
            lines.append(f"  - id: {company_id}")
            lines.append("    name:")
            lines.append("    spdx_name:")
            lines.append("    domains:")

            for domain in sorted(companies[company_id]):
                lines.append(f"      - {domain}")

            lines.append("")

        return "\n".join(lines)
