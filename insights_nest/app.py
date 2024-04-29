import argparse
import logging
import sys

from insights_nest import _action

logging.basicConfig(
    level=logging.DEBUG,
    style="{",
    format="[{levelname:<7}] {filename}:{lineno} {message}\033[0m",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()

    # Generic flags
    parser.add_argument(
        "--format",
        choices=_action.Format.choices(),
        default=_action.Format.choices()[0],
        type=_action.Format.parse,
        help="output format",
    )

    # Command flags
    parser.add_argument(
        "--group",
        help="assign the host to a group",
    )
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

    args, _ = parser.parse_known_args()
    if args.group:
        # FIXME Implement --group.
        logger.warning("--group: not implemented, ignoring.")
    if args.register:
        sys.exit(_action.Register.run(format=args.format))
    if args.unregister:
        sys.exit(_action.Unregister.run(format=args.format))

    parser.print_help()


if __name__ == "__main__":
    main()
