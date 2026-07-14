# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from collections.abc import Iterator

from ..database import Database
from .config import CompanyConfig
from .models import Company


class CompanyRepository:
    """Repository for company related database access."""

    def __init__(self, db: Database):
        self.db = db

    def import_config(self, config: CompanyConfig) -> None:
        for company in config.companies():
            self.insert_company(company)

        self.db.commit()

    #
    # Company reference data
    #

    def company_id(self, name: str) -> int | None:
        row = self.db.execute(
            """
            SELECT id
            FROM companies
            WHERE name = ?
            """,
            (name,),
        ).fetchone()

        return None if row is None else row["id"]

    def insert_company(self, company):
        self.db.execute(
            """
            INSERT OR IGNORE INTO companies(
                name,
                spdx_name
            )
            VALUES (?,?)
            """,
            (
                company.name,
                company.spdx_name,
            ),
        )

        company_id = self.company_id(company.name)

        for domain in company.domains:
            self.insert_domain(
                company_id,
                domain,
            )

        return company_id

    def companies(self) -> Iterator[Company]:
        return self.db.execute(
            """
            SELECT *
            FROM companies
            ORDER BY name
        """
        )

    #
    # Domains
    #

    def insert_domain(self, company_id: int, domain: str) -> None:
        self.db.execute(
            """
            INSERT OR IGNORE INTO company_domains(company_id, domain)
            VALUES(?, ?)
            """,
            (company_id, domain.lower()),
        )

    def domains(self) -> Iterator[Company]:
        return self.db.execute(
            """
            SELECT *
            FROM company_domains
            ORDER BY domain
        """
        )

    #
    # Author mappings
    #

    def has_mapping(self, author, email) -> bool:
        row = self.db.execute(
            """
            SELECT 1
            FROM author_company
            WHERE author=?
            AND email=?;
            """,
            (author, email),
        ).fetchone()

        return row is not None

    def set_mapping(
        self,
        author,
        email,
        company_id,
        *,
        source: str,
        confidence: int,
        evidence: str,
    ) -> None:
        self.db.execute(
            """
            INSERT OR REPLACE INTO author_company(
                author,
                email,
                company_id,
                source,
                confidence,
                evidence
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                author,
                email,
                company_id,
                source,
                confidence,
                evidence,
            ),
        )

    def iter_commit_authors(self):
        return self.db.execute(
            """
            SELECT DISTINCT
                author,
                email
            FROM commits
            WHERE email IS NOT NULL
            AND trim(email) <> ''
            ORDER BY author, email;
        """
        )

    def iter_discover(self):
        return self.db.execute(
            """
            SELECT *
            FROM company_discover
            """
        )

    def iter_domains(self) -> Iterator:
        return self.db.execute(
            """
            SELECT
                c.name       AS company_name,
                c.spdx_name  AS company_spdx_name,
                d.domain
            FROM company_domains d
            JOIN companies c
            ON c.id = d.company_id
            ORDER BY c.name,
                    d.domain
            """
        )

    def iter_domain_stats(self):
        return self.db.execute(
            """
            SELECT *
            FROM company_domain_stats
            """
        )

    def iter_mappings(self) -> Iterator:
        return self.db.execute(
            """
            SELECT *
            FROM company_mappings
            ORDER BY company_name, author_name
        """
        )
