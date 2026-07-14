# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

COMPANY_SCHEMA = """
CREATE TABLE author_company (
    author TEXT NOT NULL,
    email TEXT NOT NULL,

    company_id INTEGER NOT NULL,

    source TEXT NOT NULL,
    confidence INTEGER NOT NULL,
    evidence TEXT,

    PRIMARY KEY(author, email)
);

CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    spdx_name TEXT
);

CREATE TABLE company_domains (
    domain TEXT PRIMARY KEY,
    company_id INTEGER
);

CREATE VIEW company_discover AS
SELECT
    lower(substr(email, instr(email, '@') + 1)) AS domain,

    COUNT(*)                AS commits,
    COUNT(DISTINCT author)  AS authors,

    MIN(author)             AS example_author,
    MIN(email)              AS example_email

FROM commits

WHERE email IS NOT NULL
  AND trim(email) <> ''

GROUP BY domain

ORDER BY
    commits DESC,
    authors DESC,
    domain;

CREATE VIEW company_domain_stats AS
SELECT
    lower(substr(c.email, instr(c.email, '@') + 1)) AS domain,

    COUNT(*) AS commits,

    COUNT(DISTINCT c.author) AS authors,

    cd.company_id,

    co.name AS company_name,
    co.spdx_name AS company_spdx_name

FROM commits c

LEFT JOIN company_domains cd
       ON cd.domain =
          lower(substr(c.email, instr(c.email, '@') + 1))

LEFT JOIN companies co
       ON co.id = cd.company_id

WHERE c.email IS NOT NULL
  AND trim(c.email) <> ''

GROUP BY
    domain,
    cd.company_id,
    co.name,
    co.spdx_name

ORDER BY
    commits DESC,
    domain;

CREATE VIEW company_mappings AS
SELECT
    ac.author AS author_name,
    ac.email  AS author_email,

    substr(ac.email, instr(ac.email, '@') + 1) AS email_domain,

    c.name      AS company_name,
    c.spdx_name AS company_spdx_name,

    ac.source,
    ac.confidence,
    ac.evidence
FROM author_company ac
JOIN companies c
  ON c.id = ac.company_id;
"""
