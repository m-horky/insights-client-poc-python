import argparse
import json
import sys
from typing import Self

from insights_shell._cmd import abstract


class StatusCommand(abstract.AbstractCommand):
    NAME = "status"

    @classmethod
    def create(cls, subparsers) -> Self:
        parser = subparsers.add_parser(cls.NAME)
        parser.add_argument(abstract.FORMAT_FLAG, **abstract.FORMAT_FLAG_ARGS)
        return cls()

    def run(self, args: argparse.Namespace) -> None:
        """Display system status."""
        is_registered: bool = False

        if args.format == "human":
            if is_registered:
                print("This host is registered.")
            else:
                print("This host is not registered.")
            sys.exit(0)

        if args.format == "json":
            print(json.dumps({"registered": is_registered}))
            sys.exit(0)

        print(f"Unknown format {args['format']}", file=sys.stderr)
        sys.exit(1)
