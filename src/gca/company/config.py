# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from collections.abc import Iterator
from importlib.resources import files
from pathlib import Path

import yaml

from .models import CompanyDefinition


class CompanyConfig:
    def __init__(self) -> None:
        self._companies: dict[str, CompanyDefinition] = {}
        self._domains: dict[str, CompanyDefinition] = {}
        self._personal_domains: set[str] = set()

        self._warnings: list[str] = []

    def warnings(self) -> list[str]:
        return self._warnings

    @classmethod
    def load(cls, repository: Path | None = None) -> "CompanyConfig":
        cfg = cls()

        cfg._load_yaml(files(__package__).joinpath("builtin.yaml"))

        if repository is not None:
            local_dir = repository / ".gca"
            for path in sorted(local_dir.glob("company*.yaml")):
                cfg._load_yaml(path)

        return cfg

    def company_for_domain(self, domain: str) -> CompanyDefinition | None:
        return self._domains.get(domain.lower())

    def companies(self) -> Iterator[tuple[str, CompanyDefinition]]:
        return self._companies.values()

    def domains(self) -> Iterator[tuple[str, CompanyDefinition]]:
        return self._domains.items()

    def personal_domains(self) -> set[str]:
        return self._personal_domains

    def iter_personal_domains(self) -> Iterator[str]:
        return iter(sorted(self._personal_domains))

    def _load_yaml(self, filename: Path) -> None:
        with filename.open("r", encoding="utf-8") as fp:
            data = yaml.safe_load(fp) or {}

        for entry in data.get("companies", []):
            company_id = str(entry.get("id", "")).strip()
            if not company_id:
                self._warnings.append("Ignoring company without 'id'.")
                continue

            name = entry.get("name")
            if not name:
                self._warnings.append(
                    f"Company '{company_id}' is incomplete (missing 'name')."
                )
                continue

            domains = entry.get("domains")
            if not domains:
                self._warnings.append(f"Company '{company_id}' has no domains.")
                continue

            company = CompanyDefinition(
                id=company_id,
                name=name,
                spdx_name=entry.get("spdx_name") or name,
                domains=list(domains),
            )

            self._companies[company.id] = company

            for domain in company.domains:
                self._domains[domain.lower()] = company
