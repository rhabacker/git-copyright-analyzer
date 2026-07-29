# SPDX-FileCopyrightText: 2026 Ralf Habacker <ralf.habacker@freenet.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from collections.abc import Iterator

import subprocess


class GitRepository:
    def __init__(self, path):
        self.path = path

    def ls_files(self):
        out = subprocess.check_output(
            ["git", "-C", self.path, "ls-files"],
            text=True,
        )
        return out.splitlines()

    def commit_count(self) -> int:
        result = subprocess.run(
            [
                "git",
                "-C",
                self.path,
                "rev-list",
                "--count",
                "HEAD",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        return int(result.stdout.strip())

    def log(self, filename):
        cmd = [
            "git",
            "-c",
            "i18n.logOutputEncoding=UTF-8",
            "-C",
            self.path,
            "log",
            "--follow",
            "--patch",
            "--numstat",
            "--date=unix",
            "--format=%x1e%H%x1f%an%x1f%ae%x1f%at%x1f%s",
            "--",
            filename,
        ]

        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def log_all(self):
        return subprocess.Popen(
            [
                "git",
                "-C",
                self.path,
                "log",
                "--numstat",
                "--format="
                "commit %H%n"
                "parent %P%n"
                "author %an%n"
                "email %ae%n"
                "time %at%n"
                "subject %s%n",
            ],
            stdout=subprocess.PIPE,
            text=True,
        )

    def log_commits(self, commits: list[str]) -> subprocess.Popen:
        if not commits:
            raise ValueError("empty commit list")

        return subprocess.Popen(
            [
                "git",
                "-C",
                self.path,
                "log",
                "--no-walk",
                "--numstat",
                "--format="
                "commit %H%n"
                "parent %P%n"
                "author %an%n"
                "email %ae%n"
                "time %at%n"
                "subject %s%n",
                *commits,
            ],
            stdout=subprocess.PIPE,
            text=True,
        )

    def rev_list(self) -> Iterator[str]:
        process = subprocess.Popen(
            [
                "git",
                "-C",
                self.path,
                "rev-list",
                "HEAD",
            ],
            stdout=subprocess.PIPE,
            text=True,
        )

        assert process.stdout is not None

        for line in process.stdout:
            yield line.rstrip("\n")

        process.wait()

    def wait_finished(self, proc):
        rc = proc.wait()
        if rc != 0:
            raise RuntimeError("git log failed")
