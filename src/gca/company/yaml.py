# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later


from collections import defaultdict

from .company import suggested_company_id
from .config import CompanyConfig


class CompanyYamlGenerator:
    def generate(
        self,
        config: CompanyConfig,
        rows: list[tuple],
    ) -> str:
        """Generate company.yaml skeleton for unknown domains."""

        companies: dict[str, list[str]] = defaultdict(list)

        for row, status, _, recommend in rows:
            if recommend != "add company":
                continue

            company_id = suggested_company_id(row["domain"])
            companies[company_id].append(row["domain"])

        lines = [
            "companies:",
            "",
        ]

        for company_id in sorted(companies):
            lines.extend(
                [
                    f"  - id: {company_id}",
                    "    name:",
                    "    spdx_name:",
                    "    domains:",
                ]
            )

            for domain in sorted(companies[company_id]):
                lines.append(f"      - {domain}")

        return "\n".join(lines)
