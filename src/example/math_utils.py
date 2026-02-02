"""Small math utilities with basic logging and error handling."""
import logging
from typing import Union

logger = logging.getLogger(__name__)

Number = Union[int, float]


def add(a: Number, b: Number) -> Number:
    """Return the sum of a and b."""
    logger.info("Adding %s and %s", a, b)
    return a + b


def divide(a: Number, b: Number) -> Number:
    """Return a / b. Raises ValueError if b is zero."""
    logger.info("Dividing %s by %s", a, b)
    if b == 0:
        logger.error("Division by zero attempted: %s / %s", a, b)
        raise ValueError("Division by zero")
    return a / b
