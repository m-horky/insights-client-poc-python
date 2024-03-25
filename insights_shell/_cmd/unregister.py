import argparse
from typing import Self

from insights_shell._cmd import abstract


class UnregisterCommand(abstract.AbstractCommand):
    NAME = "unregister"
    HELP = "unregister the system"

    @classmethod
    def create(cls, subparsers) -> Self:
        parser = subparsers.add_parser(cls.NAME, help=cls.HELP)
        parser.add_argument(abstract.FORMAT_FLAG, **abstract.FORMAT_FLAG_ARGS)
        return cls()

    def run(self, args: argparse.Namespace) -> None:
        print(args)
