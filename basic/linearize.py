"""Demonstrate Linearizer ordering across multiple sources."""

from __future__ import annotations

import random
import time
from collections.abc import Iterator
from datetime import UTC, datetime

import logicsponge.core as ls


class Source(ls.SourceTerm):
    """Emit a few timestamped items with random delays."""

    def __init__(self, key: str, delays: list[float]) -> None:
        super().__init__(name=key)
        self.key = key
        self.delays = delays

    def generate(self) -> Iterator[ls.DataItem]:
        for _ in range(3):
            delay = random.choice(self.delays)  # noqa: S311
            time.sleep(delay)
            yield ls.DataItem({self.key: datetime.now(UTC).strftime("%H:%M:%S")})


def main() -> None:
    """Run three sources and merge outputs into a single stream in arrival order."""
    circuit = (
        (Source("A", [1, 2, 3]) | Source("B", [1, 2, 3]) | Source("C", [1, 2, 3]))
        * ls.MergeToSingleStream(combine=True)
        * ls.Print()
        * ls.Stop()
    )
    circuit.start()


if __name__ == "__main__":
    main()
