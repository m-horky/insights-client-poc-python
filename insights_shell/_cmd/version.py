import argparse
import json
import sys
from typing import Self

import insights_shell.__about__
from insights_shell._cmd import abstract


class VersionCommand(abstract.AbstractCommand):
    NAME = "version"
    HELP = "display versions of components"

    @classmethod
    def create(cls, subparsers) -> Self:
        parser = subparsers.add_parser(cls.NAME, help=cls.HELP)
        parser.add_argument(abstract.FORMAT_FLAG, **abstract.FORMAT_FLAG_ARGS)
        return cls()

    def run(self, args: argparse.Namespace) -> None:
        versions = {
            "shell": insights_shell.__about__.VERSION,
            "egg": "unknown",
        }

        if args.format == "human":
            for k, v in versions.items():
                print(f"{k}: {v}")
            sys.exit(0)

        if args.format == "json":
            print(json.dumps(versions))
            sys.exit(0)

        print(f"Unknown format {args['format']}", file=sys.stderr)
        sys.exit(1)
