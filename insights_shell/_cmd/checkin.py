import argparse
import sys
from typing import Self

from insights_shell._cmd import abstract
from insights_shell._shell import system


class CheckinCommand(abstract.AbstractCommand):
    NAME = "checkin"
    HELP = "scan the system for canonical facts and upload the results to Insights"

    @classmethod
    def create(cls, subparsers) -> Self:
        _ = subparsers.add_parser(cls.NAME, help=cls.HELP)
        return cls()

    def run(self, args: argparse.Namespace) -> None:
        """Select subcommand to run."""
        if not system.is_registered():
            print("This host is not registered.")
            sys.exit(1)

        # 1. Load the egg
        # 2. Call insights.util.canonical_facts:get_canonical_facts()
        raise NotImplementedError
