import logging
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parents[2] / "logs" / "app.log"


def configure_logging() -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=str(LOG_FILE),
        level=logging.INFO,
        force=True,
    )