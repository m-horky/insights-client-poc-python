import argparse
import sys
from typing import Self

from insights_nest._cmd import abstract
from insights_nest._shell import system


class ScanCommand(abstract.AbstractCommand):
    NAME = "scan"
    HELP = "scan the system and upload the results to Insights"

    @classmethod
    def create(cls, subparsers) -> Self:
        _ = subparsers.add_parser(cls.NAME, help=cls.HELP)
        # TODO Add Core parameters
        return cls()

    def run(self, args: argparse.Namespace) -> None:
        """Select subcommand to run."""
        if not system.is_registered():
            print("This host is not registered.")
            sys.exit(1)
