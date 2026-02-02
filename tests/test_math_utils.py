import logging
import pytest

from example.math_utils import add, divide


def test_add_simple():
    assert add(1, 2) == 3


def test_add_floats():
    assert add(1.5, 2.5) == 4.0


def test_divide():
    assert divide(6, 3) == 2


def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(1, 0)


def test_logging_on_add(caplog):
    caplog.set_level(logging.INFO)
    result = add(2, 3)
    assert result == 5
    assert any("Adding" in rec.getMessage() for rec in caplog.records)
