import time
from contextlib import contextmanager

import typer


@contextmanager
def timed_phase(name: str):
    start = time.perf_counter()

    typer.echo(f"{name} started")

    try:
        yield

    finally:
        elapsed = time.perf_counter() - start
        typer.echo(
            f"{name} finished in {elapsed:.2f}s"
        )
