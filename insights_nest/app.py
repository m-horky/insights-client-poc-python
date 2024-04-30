import argparse
import logging
import os
import sys

from insights_nest import _action
from insights_nest._core import egg

if os.environ.get("NEST_DEBUG_STDERR", "").lower() in ("true", "1"):
    LOG_FORMAT = (
        "\033[32;1m{levelname}\033[0m \033[32m{asctime}\033[0m\n"
        "\033[33m{pathname}:{lineno}\033[0m\n{message}\n"
    )

    logging.basicConfig(
        level=logging.DEBUG,
        style="{",
        format=LOG_FORMAT,
    )
else:
    LOG_FORMAT = "[{levelname:<7}] {pathname}:{lineno} {message}"

    # TODO Log to file


logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()

    # Modifier flags
    parser.add_argument(
        "--format",
        choices=_action.Format.choices(),
        default=_action.Format.choices()[0],
        type=_action.Format.parse,
        help="output format",
    )

    # Non-terminal commands
    parser.add_argument(
        "--group",
        help="assign the host to a group",
    )

    # Terminal commands
    parser.add_argument(
        "--register",
        action="store_true",
        default=False,
        help="register host to Insights",
    )
    parser.add_argument(
        "--unregister",
        action="store_true",
        default=False,
        help="unregister host from Insights",
    )
    parser.add_argument(
        "--checkin",
        action="store_true",
        default=False,
        help="send a light check-in message to Insights",
    )

    args, _ = parser.parse_known_args()
    if args.group:
        # FIXME Implement --group.
        logger.warning("--group: not implemented, ignoring.")
    if args.register:
        sys.exit(_action.Register.run(format=args.format))
    if args.unregister:
        sys.exit(_action.Unregister.run(format=args.format))
    if args.checkin:
        sys.exit(_action.Checkin.run(format=args.format))

    parser.print_help()


if __name__ == "__main__":
    main()
