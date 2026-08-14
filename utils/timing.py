import time
from collections import defaultdict
from contextlib import contextmanager


class IOTimeTracker:
    def __init__(self):
        self._totals = defaultdict(float)
        self._counts = defaultdict(int)

    def reset(self):
        self._totals.clear()
        self._counts.clear()

    @contextmanager
    def track(self, category: str):
        start = time.perf_counter()
        try:
            yield
        finally:
            self._totals[category] += time.perf_counter() - start
            self._counts[category] += 1

    def total(self, category: str) -> float:
        return self._totals[category]

    def count(self, category: str) -> int:
        return self._counts[category]


io_timer = IOTimeTracker()
