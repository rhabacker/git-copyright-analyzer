<!--
SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>

SPDX-License-Identifier: CC0-1.0
-->

Project: git-copyright-analyzer (gca)

Goal:
Analyze Git history to generate evidence for SPDX copyright statements.

Architecture:

- Python 3.11+
- Typer CLI
- SQLite database
- Streaming git parser
- Incremental updates
- No AI in the core analysis
- AI only for optional review of borderline cases

Planned commands:

- gca init
- gca scan
- gca summary
- gca contributors
- gca suggest

Roadmap:

1. Robust streaming parser
2. SQLite import
3. Summary/report commands
4. Existing SPDX/header parser
5. Company mapping
6. Incremental updates
7. SPDX suggestions
8. Optional AI review

Repository:
- git-copyright-analyzer on GitHub https://github.com/rhabacker/git-copyright-analyzer

chatgpt: I'll treat this as the ongoing project context during this conversation. My default approach will be to help design and implement the tool with an emphasis on:

- Clean, maintainable architecture
- Performance on large repositories (streaming and incremental processing)
- Deterministic, reproducible analysis
- Testability and extensibility
- SPDX compliance and evidence-based attribution
- Keeping AI completely outside the core analysis pipeline, using it only as an optional review layer for ambiguous cases

I'll also try to keep the implementation cohesive across sessions by considering long-term maintainability rather than only solving individual coding tasks.
