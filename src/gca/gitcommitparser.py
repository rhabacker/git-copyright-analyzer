from .gitcommit import GitCommit, GitChange


class GitCommitParser:
    def __init__(self, stream):
        self.stream = stream

    def _number(self, value):

        if value == "-":
            return 0

        return int(value)

    def __iter__(self):
        current = None

        for line in self.stream:
            line = line.rstrip("\n")

            if line.startswith("commit "):
                if current:
                    yield current

                current = GitCommit(
                    hash=line[7:],
                    author="",
                    email="",
                    timestamp=0,
                    subject="",
                )

            elif line.startswith("parent "):
                current.parents.append(line[7:])

            elif line.startswith("author "):
                value = line[7:]

                current.author = value

            elif line.startswith("email "):
                current.email = line[6:]

            elif line.startswith("time "):
                current.timestamp = int(line[5:])

            elif line.startswith("subject "):
                current.subject = line[8:]

            else:
                parts = line.split("\t")

                if len(parts) == 3:

                    additions, deletions, path = parts

                    current.changes.append(
                        GitChange(
                            commit_hash=current.hash,
                            path=path,
                            additions=self._number(additions),
                            deletions=self._number(deletions),
                        )
                    )
        if current:
            yield current
