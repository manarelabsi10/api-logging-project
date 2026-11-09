import logging
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parents[2] / "logs" / "app.log"


def configure_logging() -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=str(LOG_FILE),
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        force=False,
    )