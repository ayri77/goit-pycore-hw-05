import pytest
from src.task1 import caching_fibonacci

# testing fibonaccci
CASES = [
    (0, 0, "null_argument"),
    (-5, 0, "negative_argument"),
    ("", 0, "empty_argument"),
    ("aaa", 0, "string_argument"),
    (1, 1, "1_argument"),
    (2, 1, "2_argument"),
    (3, 2, "3_argument"),
    (10, 55, "10_argument"),
    (15, 610, "15_argument")
]

@pytest.mark.parametrize(
    "arg, exp_fibo",
    [(a, e) for a, e, _ in CASES],
    ids=[i for _, _, i in CASES],
)

# testing cache
def test_caching_fibonacci_returns_expected(arg, exp_fibo):
    fib = caching_fibonacci()
    assert fib(arg) == exp_fibo

# repeating call, test cache size
def test_cache_used_on_repeat_call():
    fib = caching_fibonacci()
    cache = fib._cache

    assert len(cache) == 0
    fib(10)                      # full cache
    size_after_first = len(cache)
    fib(10)                      # take from cache
    assert len(cache) == size_after_first  # test cache size

# two calls, different cache
def test_caches_are_independent():
    fib1 = caching_fibonacci()
    fib2 = caching_fibonacci()
    assert fib1._cache is not fib2._cache