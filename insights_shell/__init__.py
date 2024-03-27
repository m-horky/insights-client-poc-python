import argparse
import logging
import sys

import insights_shell._cmd.abstract
from insights_shell._cmd.version import VersionCommand
from insights_shell._cmd.status import StatusCommand
from insights_shell._cmd.identity import IdentityCommand
from insights_shell._cmd.register import RegisterCommand
from insights_shell._cmd.unregister import UnregisterCommand
from insights_shell._cmd.checkin import CheckinCommand
from insights_shell._cmd.scan import ScanCommand
from insights_shell._cmd.scan_compliance import ComplianceScanCommand


logging.basicConfig(
    level=logging.DEBUG,
    format="[{levelname:<7}] {filename}:{lineno} {message}\033[0m",
    style="{",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--insecure-egg",
        action="store_true",
        default=False,
        help=argparse.SUPPRESS,
    )

    commands: dict[str, insights_shell._cmd.abstract.AbstractCommand] = {}

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

    commands[args.command].run(args)


if __name__ == "__main__":
    main()
