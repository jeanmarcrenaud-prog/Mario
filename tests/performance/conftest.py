# tests/performance/conftest.py
# Dummy implementation of the 'benchmark' fixture used in performance tests.
# It simply returns a callable that measures execution time using perf_counter.
import time
import pytest

@pytest.fixture
def benchmark():
    """Return a simple benchmark object.

    The real test suite expects the `pytest-benchmark` plugin, but for the
    purposes of these unit tests we provide a lightweight fallback.
    """
    class Benchmark:
        def __call__(self, func, *args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            # Store the duration on an attribute for possible inspection.
            self.duration = end - start
            return result
    return Benchmark()
