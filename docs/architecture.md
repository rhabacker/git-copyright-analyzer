
# Git Copyright Analyzer Architecture

## Goals

Git Copyright Analyzer (gca) extracts copyright information from Git history
and source files and produces deterministic SPDX-compatible reports.

The project is designed around the following principles:

- deterministic analysis
- reproducible results
- incremental processing
- separation of configuration and derived data
- SQLite as the canonical analysis database

## Processing Pipeline

```
Git repository
      │
      ▼
 scan commits
      │
      ▼
SQLite database
      │
      ├── authors
      ├── files
      ├── commits
      ├── copyrights
      ├── companies
      └── ...
      │
      ▼
analysis commands
      │
      ▼
reports / SPDX output
```

The scan phase only extracts facts.

Subsequent commands enrich these facts without rescanning the repository.

## Repository layout

```
src/gca
    cli.py
    ...

    headers/
        ...

    company/
        cli.py
        config.py
        mapper.py
        repository.py

    report/
        ...
```

Each feature is implemented as an independent subpackage.

Every subpackage contains

- CLI
- database access
- models
- configuration
- business logic

instead of mixing all functionality into the top-level package.

## Database

The SQLite database is the canonical storage for all derived information.

Information is divided into

- imported facts
- derived facts
- reference data

Imported facts

- commits
- files
- authors

Derived facts

- copyright owners
- SPDX headers
- author/company mappings

Reference data

- configured companies
- domain mappings

This separation allows derived information to be regenerated at any time.

## Company Mapping

Company information originates from YAML configuration.

```
company.yaml
        │
        ▼
CompanyConfig
        │
        ▼
company import
        │
        ▼
companies
company_domains
```

Git commits are analysed separately.

```
commits
      │
      ▼
discover domains
      │
      ▼
author_company
```

Configuration never modifies commit history.

Instead, mappings are generated from observable evidence
(email domains, future rules, manual overrides).

## Design Principles

The architecture of Git Copyright Analyzer is guided by a small number of
principles that aim to produce deterministic, explainable and reproducible
results.

### Deterministic

Running the same command twice on the same repository and configuration
produces the same result.

Analysis never relies on external services or heuristics that would make the
result non-reproducible.

### Explainable

Derived information should always be traceable back to its origin.

For example, company mappings store

- source
- confidence
- evidence

allowing users to understand why a mapping was created.

### Database as the Analysis State

The SQLite database is the canonical analysis state of the application.

All analysis, reporting and mapping commands operate exclusively on the
database rather than reading configuration files directly.

Configuration files are treated as import sources in the same way as the Git
repository:

```
Git repository      company.yaml
       │                 │
       └──────┬──────────┘
              ▼
        scan / import
              │
              ▼
      SQLite database
              │
              ▼
   reports • mappings • statistics • SPDX
```

This separation provides several advantages:

- a single, consistent source of analysis data
- deterministic command behaviour
- imported configuration can be inspected independently
- derived data can be regenerated without rereading configuration files
- future import sources can be added without changing analysis commands

This distinction is reflected in the CLI:

| Command | Purpose |
|---------|---------|
| `gca company config` | Show the current YAML configuration |
| `gca company import` | Import configuration into the database |
| `gca company show` | Show the imported reference data |
| `gca company map` | Generate author/company mappings from imported data |

### Incremental

Expensive operations, such as scanning Git history, should only be performed
once.

Subsequent commands operate on the SQLite database, allowing additional
analysis without rescanning the repository.

### Separation of Concerns

Each feature is implemented as an independent package consisting of:

- CLI commands
- configuration
- repository (database access)
- models
- business logic

This keeps the user interface, persistence and analysis logic independent and
makes new features straightforward to implement.

### Extensible

New analysis rules should be additive rather than requiring changes to the
existing architecture.

Examples include:

- additional company mapping rules
- manual mapping overrides
- subsidiary/company aliases
- SPDX generation
- optional AI-assisted suggestions

Because analysis is performed on the database, new features can reuse existing
data without modifying the Git scanner

## Roadmap

- ✔ Commit scanner
- ✔ SQLite backend
- ✔ Reporting
- ✔ SPDX header parser
- ✔ Company mapping
- ☐ Incremental updates
- ☐ SPDX generation
- ☐ AI-assisted review
