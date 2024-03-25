import argparse
from typing import Self


class AbstractCommand:
    NAME: str

    @classmethod
    def create(cls, subparsers) -> Self:
        raise NotImplementedError

    def run(self, args: argparse.Namespace) -> None:
        raise NotImplementedError
