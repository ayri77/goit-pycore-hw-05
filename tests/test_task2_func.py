import pytest
from src.task2 import sum_profit, generator_numbers

text1 = "Загальний дохід працівника складається з декількох частин: 1000.01 як основний дохід, доповнений додатковими надходженнями 27.45 і 324.00 доларів."
text2 = "Текст без даних"

def test_generator_yields_floats_type():
    vals = list(generator_numbers(text1))
    assert vals, "generator_numbers should yield at least one value"
    assert all(isinstance(v, float) for v in vals), "values must be float"

def test_generator_empty_input_returns_empty_iterable():
    assert list(generator_numbers("")) == []

def test_generator_no_numbers_returns_empty_iterable():
    assert list(generator_numbers(text2)) == []

def test_sum_profit_uses_callable_with_text():
    seen = {}
    def fake_gen(s: str):
        seen["arg"] = s
        yield 1.0
        yield 2.5
    assert sum_profit("abc def", fake_gen) == pytest.approx(3.5)
    assert seen.get("arg") == "abc def"

def test_sum_profit_rejects_iterator_instead_of_callable():
    # check TypeError
    with pytest.raises(TypeError):
        sum_profit(text1, generator_numbers(text1))

@pytest.mark.parametrize(
    "txt, expected",
    [
        ("a 7.00 b", 7.00),    # two decimal numbers
        ("a 7.0 b", 0.00),     # one decimal numbers
        ("a 7.000 b", 0.00),   # three decimal numbers
        ("a 12,34 b", 0.00),   # wrong separator
        ("x  12.30   0.70   y", 13.00),  # more spaces
    ],
    ids=["two_decimals", "one_decimal", "three_decimals", "comma_decimal", "extra_spaces"],
)
def test_number_format_rules(txt, expected):
    assert sum_profit(txt, generator_numbers) == pytest.approx(expected)