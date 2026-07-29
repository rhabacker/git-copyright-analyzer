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
            total_elapsed=(history.elapsed + headers.elapsed + db_commit_time),
        )

    def scan_history(self) -> HistoryStatistics:
        stats = HistoryStatistics()

        start = time.perf_counter()

        missing = self.find_missing_commits(stats)

        if missing:
            self.import_missing_commits(missing, stats)  #

        stats.elapsed = time.perf_counter() - start
        return stats

    def find_missing_commits(self, stats):
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

        return missing

    def import_missing_commits(self, missing, stats):
        missing_count = len(missing)

        with Progress() as progress:
            task = progress.add_task(
                "[cyan]Importing commits ",
                total=missing_count,
            )

            #
            # First import?
            #
            if missing_count == stats.commits_scanned:
                proc = self.git.log_all()

            else:
                proc = self.git.log_commits(missing)

            parser = GitCommitParser(proc.stdout)

            for commit in parser:
                self.db.insert_commit_tree(commit)

                stats.parents_imported += len(commit.parents)
                stats.changes_imported += len(commit.changes)
                stats.commits_imported += 1

                progress.advance(task)
                progress.update(
                    task,
                    description=(
                        f"[cyan]Importing commits ({stats.commits_imported:,}/{missing_count:,})"
                    ),
                )

            self.git.wait_finished(proc)

        return stats

    def scan_headers(self):
        stats = HeaderStatistics()

        files = self.git.ls_files()

        start = time.perf_counter()

        files_count = len(files)

        with Progress() as progress:
            task = progress.add_task(
                "Scanning headers ",
                total=files_count,
            )

            for filename in files:
                stats.files_scanned += 1

                progress.advance(task)
                progress.update(
                    task,
                    description=(
                        f"Scanning headers ({stats.files_scanned:,}/{files_count:,})"
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
