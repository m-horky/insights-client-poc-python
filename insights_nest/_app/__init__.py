import json
import logging
import sys

from insights_nest._app import flag

logger = logging.getLogger(__name__)


def pprint(message: str, /, format: flag.Format, ok: bool) -> int:
    """Print a message in requested format and return zero or non-zero code."""
    if format == flag.Format.JSON:
        message = json.dumps({"message": message, "ok": ok})
    if format == flag.Format.HUMAN:
        if not ok:
            message = f"Error: {message}"

    print(message, file=sys.stdout)
    return 0 if ok else 1
