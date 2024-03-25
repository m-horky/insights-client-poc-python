import argparse
import json
import sys

import insights_shell.__about__
from insights_shell.cmd import abstract


class VersionCommand(abstract.AbstractCommand):
    NAME = "version"

    def __init__(self, parser):
        self.parser = parser

    @classmethod
    def create(cls, subparsers):
        parser = subparsers.add_parser("version")
        parser.add_argument(
            "--format",
            choices=["human", "json"],
            default="human",
            help="output format",
        )
        return cls(parser)

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
