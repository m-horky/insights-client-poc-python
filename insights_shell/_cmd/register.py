import argparse
import sys
from typing import Self

from insights_shell._cmd import abstract
from insights_shell._shell import system


class RegisterCommand(abstract.AbstractCommand):
    NAME = "register"
    HELP = "register the host"

    @classmethod
    def create(cls, subparsers) -> Self:
        parser = subparsers.add_parser(cls.NAME, help=cls.HELP)
        parser.add_argument(abstract.FORMAT_FLAG, **abstract.FORMAT_FLAG_ARGS)
        return cls()

    def run(self, args: argparse.Namespace) -> None:
        if system.is_registered():
            print("This host is already registered.")
            sys.exit(1)
