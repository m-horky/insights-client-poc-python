import argparse
import sys

import insights_shell.cmd.abstract
from insights_shell.cmd.version import VersionCommand


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--insecure-egg",
        action="store_true",
        default=False,
        help=argparse.SUPPRESS,
    )

    subparsers = parser.add_subparsers(dest="command")
    subcommands: list[type[insights_shell.cmd.abstract.AbstractCommand]] = [
        VersionCommand,
    ]

    commands: dict[str, insights_shell.cmd.abstract.AbstractCommand] = {}
    for subcommand in subcommands:
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
