# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from .gitrepository import GitRepository
from .gitcommitparser import GitCommitParser
from .headers.scanner import HeaderScanner
from .models import ScanStatistics, HeaderStatistics, HistoryStatistics

from rich.progress import Progress
import time

SCAN_EXCLUDED_PREFIXES = (
    "LICENSES/",
    ".git/",
)


class Scanner:
    def __init__(self, repo, database):
        self.db = database
        self.git = GitRepository(repo)
        self.headers = HeaderScanner(self.db)

    def should_scan(self, filename: str) -> bool:
        return not filename.startswith(SCAN_EXCLUDED_PREFIXES)

    def scan(self) -> ScanStatistics:
        history = self.scan_history()

        headers = self.scan_headers()

        db_commit_time = self.commit()

        return ScanStatistics(
            history=history,
            headers=headers,
            db_commit_time=db_commit_time,
            total_elapsed=(history.elapsed + history.elapsed + db_commit_time),
        )

    def scan_history(self) -> HistoryStatistics:
        stats = HistoryStatistics()

        start = time.perf_counter()

        #
        # Phase 1: discover missing commits
        #
        missing: list[str] = []

        total = self.git.commit_count()

        with Progress() as progress:
            task = progress.add_task(
                "[cyan]Checking commits  ",
                total=total,
            )

            existing = self.db.get_commit_hashes()

            for commit_hash in self.git.rev_list():
                stats.commits_scanned += 1

                progress.advance(task)
                progress.update(
                    task,
                    description=(
                        f"[cyan]Checking commits  ({stats.commits_scanned:,}/{total:,})"
                    ),
                )

                if commit_hash in existing:
                    continue

                missing.append(commit_hash)

        #
        # Nothing to do
        #
        if not missing:
            stats.elapsed = time.perf_counter() - start
            return stats

        #
        # Phase 2: Import commits
        #
        with Progress() as progress:
            task = progress.add_task(
                "[cyan]Importing commits ",
                total=len(missing),
            )

            #
            # First import?
            #
            if len(missing) == stats.commits_scanned:
                proc = self.git.log_all()

            else:
                proc = self.git.log_commits(missing)

            parser = GitCommitParser(proc.stdout)

            imported_now = 0

            for commit in parser:
                imported_now += 1

                stats.commits_imported += 1

                self.db.insert_commit(commit)

                for parent in commit.parents:
                    self.db.insert_commit_parent(
                        commit.hash,
                        parent,
                    )
                    stats.parents_imported += 1

                for change in commit.changes:
                    self.db.insert_change(change)
                    stats.changes_imported += 1

                progress.advance(task)
                progress.update(
                    task,
                    description=(
                        f"[cyan]Importing commits ({imported_now:,}/{len(missing):,})"
                    ),
                )

            proc.wait()

        stats.elapsed = time.perf_counter() - start

        return stats

    def scan_headers(self):
        stats = HeaderStatistics()

        files = self.git.ls_files()

        start = time.perf_counter()

        with Progress() as progress:
            task = progress.add_task(
                "Scanning headers ",
                total=len(files),
            )

            for filename in files:
                stats.files_scanned += 1

                progress.advance(task)
                progress.update(
                    task,
                    description=(
                        f"Scanning headers ({stats.files_scanned:,}/{len(files):,})"
                    ),
                )

                if not self.should_scan(filename):
                    stats.files_ignored += 1
                    continue

                file_id = self.db.get_or_create_file(filename)

                result = self.headers.scan(filename, file_id)

                if result is not None:
                    stats.headers_found += 1

                    # if record includes spdx copyright
                    #   stats.spdx_headers += 1

        stats.elapsed = time.perf_counter() - start

        return stats

    def commit(self):
        start = time.perf_counter()

        self.db.commit()

        return time.perf_counter() - start
