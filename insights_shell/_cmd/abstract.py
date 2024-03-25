import argparse
from typing import Self


class AbstractCommand:
    NAME: str

    @classmethod
    def create(cls, subparsers) -> Self:
        raise NotImplementedError

    def run(self, args: argparse.Namespace) -> None:
        raise NotImplementedError


FORMAT_FLAG = "--format"
FORMAT_FLAG_ARGS = {
    "choices": ["human", "json"],
    "default": "human",
    "help": "output format",
}
