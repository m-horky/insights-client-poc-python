import argparse
import logging
import sys
from typing import Self

from insights_nest.api import inventory
from insights_nest._cmd import abstract
from insights_nest._core import egg
from insights_nest._core import system


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

        try:
            canonical_facts: dict = egg.Egg().run("checkin")
        except RuntimeError:
            logging.error("Check-in failed.")
            print("Check-in failed.")
            return

        try:
            _: inventory.Host = inventory.Inventory().checkin(canonical_facts)
        except LookupError:
            print("Error: Could not upload results to Insights.", file=sys.stderr)
            return

        print("Successfully checked in.")
