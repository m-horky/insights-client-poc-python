import argparse
import sys
from typing import Self

from insights_shell._cmd import abstract
from insights_shell._shell import system


class ComplianceScanCommand(abstract.AbstractCommand):
    NAME = "scan-for-compliance"
    HELP = "scan the system and upload the results to Insights Compliance"

    @classmethod
    def create(cls, subparsers) -> Self:
        _ = subparsers.add_parser(cls.NAME, help=cls.HELP)
        # TODO Add Compliance parameters
        return cls()

    def run(self, args: argparse.Namespace) -> None:
        """Select subcommand to run."""
        if not system.is_registered():
            print("This host is not registered.")
            sys.exit(1)
