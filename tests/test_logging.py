import logging
import tempfile
from playlingo.logging_config import InMemoryLogHandler, setup_logging, get_memory_handler, dump_logs_to_file


def test_inmemory_handler_capacity():
    h = InMemoryLogHandler(capacity=3)
    logger = logging.getLogger("test_inmem")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(h)

    logger.debug("one")
    logger.info("two")
    logger.warning("three")
    logger.error("four")

    logs = h.get_logs()
    assert len(logs) == 3
    assert any("two" in l for l in logs)
    assert any("four" in l for l in logs)


def test_setup_and_dump(tmp_path):
    # use a temporary memory capacity
    setup_logging(level=logging.DEBUG, capture_in_memory=True, memory_capacity=5)
    mh = get_memory_handler()
    assert mh is not None
    logger = logging.getLogger("playlingo.tests")
    logger.setLevel(logging.DEBUG)
    logger.info("diag_test_line")

    fn = tmp_path / "logs.txt"
    dump_logs_to_file(str(fn))
    content = fn.read_text(encoding="utf-8")
    assert "diag_test_line" in content
