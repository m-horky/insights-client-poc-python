import argparse
import json
import sys

from insights_nest._cmd import abstract
from insights_nest._core import system


class StatusCommand(abstract.AbstractCommand):
    NAME = "status"
    HELP = "display host status"

    @classmethod
    def create(cls, subparsers) -> "StatusCommand":
        parser = subparsers.add_parser(cls.NAME, help=cls.HELP)
        parser.add_argument(abstract.FORMAT_FLAG, **abstract.FORMAT_FLAG_ARGS)
        return cls()

    def run(self, args: argparse.Namespace) -> None:
        is_registered: bool = system.get_inventory_host() is not None

        if args.format == "human":
            if is_registered:
                print("This host is registered.")
            else:
                print("This host is not registered.")
            sys.exit(0)

        if args.format == "json":
            print(json.dumps({"registered": is_registered}))
            sys.exit(0)

        print(f"Unknown format {args.format}", file=sys.stderr)
        sys.exit(1)
