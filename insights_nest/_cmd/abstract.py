import argparse


class AbstractCommand:
    NAME: str
    HELP: str

    @classmethod
    def create(cls, subparsers) -> "AbstractCommand":
        raise NotImplementedError

    def run(self, args: argparse.Namespace) -> None:
        raise NotImplementedError


FORMAT_FLAG = "--format"
FORMAT_FLAG_ARGS = {
    "choices": ["human", "json"],
    "default": "human",
    "help": "output format",
}
