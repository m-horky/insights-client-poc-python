import argparse
import logging
import sys

from insights_nest._cmd import abstract
from insights_nest._core import system


class RegisterCommand(abstract.AbstractCommand):
    NAME = "register"
    HELP = "register the host"

    @classmethod
    def create(cls, subparsers) -> "RegisterCommand":
        parser = subparsers.add_parser(cls.NAME, help=cls.HELP)
        parser.add_argument(abstract.FORMAT_FLAG, **abstract.FORMAT_FLAG_ARGS)
        return cls()

    def run(self, args: argparse.Namespace) -> None:
        if system.get_inventory_host() is not None:
            print("This host is already registered.")
            sys.exit(1)

        logging.info("Registering the host.")
        # 1. Collect data
        # 2. Upload them

        raise NotImplementedError
