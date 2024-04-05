import argparse
import sys

from insights_nest._cmd import abstract
from insights_nest._core import system


class ComplianceScanCommand(abstract.AbstractCommand):
    NAME = "scan-compliance"
    HELP = "scan the system for compliance and upload the results to Insights"

    @classmethod
    def create(cls, subparsers) -> "ComplianceScanCommand":
        _ = subparsers.add_parser(cls.NAME, help=cls.HELP)
        # TODO Add Compliance parameters
        return cls()

    def run(self, args: argparse.Namespace) -> None:
        """Select subcommand to run."""
        if not system.is_registered():
            print("This host is not registered.")
            sys.exit(1)
