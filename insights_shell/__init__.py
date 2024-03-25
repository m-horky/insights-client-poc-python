import argparse
import sys

import insights_shell._cmd.abstract
from insights_shell._cmd.version import VersionCommand
from insights_shell._cmd.status import StatusCommand
from insights_shell._cmd.register import RegisterCommand
from insights_shell._cmd.unregister import UnregisterCommand


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--insecure-egg",
        action="store_true",
        default=False,
        help=argparse.SUPPRESS,
    )

    subparsers = parser.add_subparsers(dest="command")
    commands: dict[str, insights_shell._cmd.abstract.AbstractCommand] = {}
    for subcommand in [
        VersionCommand,
        StatusCommand,
        RegisterCommand,
        UnregisterCommand,
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
