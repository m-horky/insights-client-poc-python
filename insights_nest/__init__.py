import argparse
import logging
import sys

from insights_nest._core import egg

import insights_nest._cmd.abstract
from insights_nest._cmd.version import VersionCommand
from insights_nest._cmd.status import StatusCommand
from insights_nest._cmd.identity import IdentityCommand
from insights_nest._cmd.register import RegisterCommand
from insights_nest._cmd.unregister import UnregisterCommand
from insights_nest._cmd.checkin import CheckinCommand
from insights_nest._cmd.scan import ScanCommand
from insights_nest._cmd.scan_compliance import ComplianceScanCommand


logging.basicConfig(
    level=logging.DEBUG,
    format="[{levelname:<7}] {module}:{lineno} {message}\033[0m",
    style="{",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-update",
        action="store_true",
        default=False,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--force-egg-update",
        action="store_true",
        default=False,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--insecure-egg",
        action="store_true",
        default=False,
        help=argparse.SUPPRESS,
    )

    commands: dict[str, insights_nest._cmd.abstract.AbstractCommand] = {}

    subparsers = parser.add_subparsers(dest="command")
    for subcommand in [
        # host
        StatusCommand,
        IdentityCommand,
        RegisterCommand,
        UnregisterCommand,
        VersionCommand,
        # collection
        CheckinCommand,
        ScanCommand,
        ComplianceScanCommand,
        #
        # --support
        # --diagnosis
    ]:
        commands[subcommand.NAME] = subcommand.create(subparsers)

    args = parser.parse_args()

    if args.command not in commands.keys():
        if args.command is None:
            parser.print_help()
            sys.exit(0)
        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)

    if not args.no_update:
        _: egg.EggUpdateResult = egg.update(
            force=args.force_egg_update, insecure=args.insecure_egg
        )

    commands[args.command].run(args)


if __name__ == "__main__":
    main()
