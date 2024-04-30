import argparse
import logging
import os
import sys
from typing import Optional

from insights_nest._core import egg

import insights_nest._app.light
import insights_nest._app.flag
import insights_nest._app.registration


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

    # TODO Log to file at config-specified level instead.
    logging.basicConfig(
        level=logging.CRITICAL,
        style="{",
        format=LOG_FORMAT,
    )


logger = logging.getLogger(__name__)


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    # Modifier flags
    parser.add_argument(
        "--format",
        choices=insights_nest._app.flag.Format.choices(),
        default=insights_nest._app.flag.Format.choices()[0],
        type=insights_nest._app.flag.Format.parse,
        help="output format",
    )
    parser.add_argument(
        "--no-egg-update",
        action="store_true",
        default=False,
        help="do not check for egg updates",
    )

    # Non-terminal commands
    parser.add_argument(
        "--group",
        help="assign the host to a group",
    )
    parser.add_argument(
        "--display-name",
        help="set the host display name",
    )
    parser.add_argument(
        "--ansible-host",
        help="set the Ansible display name",
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
    parser.add_argument(
        "--identity",
        action="store_true",
        default=False,
        help="display host identity",
    )

    # Aliases
    parser.add_argument(
        "--status",
        action="store_true",
        default=False,
        help="deprecated; use --identity instead",
    )
    parser.add_argument(
        "--test-connection",
        action="store_true",
        default=False,
        help="deprecated; use --identity instead",
    )

    return parser


def main():
    parser = get_parser()

    args, _ = parser.parse_known_args()

    if args.no_egg_update:
        logger.debug("Skipping egg update step.")
    else:
        # TODO Should we expose this through CLI or flag?
        egg.update(force=False)

    # Non-terminal commands
    if args.group:
        # FIXME Implement --group.
        logger.warning("--group: not implemented, ignoring.")
    if args.display_name:
        # FIXME Implement --display-name.
        logger.warning("--display-name: not implemented, ignoring.")
    if args.ansible_host:
        # FIXME Implement --ansible-host.
        logger.warning("--ansible-host: not implemented, ignoring.")

    # Aliases
    if args.status:
        logger.warning("Flag --status is deprecated, use --identity instead.")
        if args.format == insights_nest._app.flag.Format.HUMAN:
            print("Warning: Flag --status is deprecated, use --identity instead.")
        args.identity = args.status
    if args.test_connection:
        logger.warning("Flag --test-connection is deprecated, use --identity instead.")
        if args.format == insights_nest._app.flag.Format.HUMAN:
            print("Warning: Flag --test-connection is deprecated, use --identity instead.")
        args.identity = args.test_connection

    # Terminal commands
    result: Optional[int] = None
    if args.register:
        result = insights_nest._app.registration.Register.run(format=args.format)
    if args.unregister:
        result = insights_nest._app.registration.Unregister.run(format=args.format)
    if args.checkin:
        result = insights_nest._app.light.Checkin.run(format=args.format)
    if args.identity:
        result = insights_nest._app.light.Identity.run(format=args.format)

    if result is not None:
        logger.info(f"Quitting with status code {result}.")
        sys.exit(result)

    parser.print_help()


if __name__ == "__main__":
    main()
