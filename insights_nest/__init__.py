import argparse
import logging
import sys

from insights_nest._core import egg

import insights_nest._cmd.abstract
from insights_nest._cmd.checkin import CheckinCommand
from insights_nest._cmd.identity import IdentityCommand
from insights_nest._cmd.playbook_verifier import VerifyPlaybookCommand
from insights_nest._cmd.scan_advisor import AdvisorScanCommand
from insights_nest._cmd.scan_compliance import ComplianceScanCommand
from insights_nest._cmd.status import StatusCommand
from insights_nest._cmd.version import VersionCommand


logging.basicConfig(
    level=logging.DEBUG,
    format="[{levelname:<7}] {module}:{lineno} {message}\033[0m",
    style="{",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-egg-update",
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

    commands: dict[str, insights_nest._cmd.abstract.AbstractCommand] = {}

    subparsers = parser.add_subparsers(dest="command")
    for subcommand in [
        StatusCommand,
        IdentityCommand,
        VersionCommand,
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

    if not args.no_egg_update:
        _: egg.EggUpdateResult = egg.update(force=args.force_egg_update)


if __name__ == "__main__":
    main()
