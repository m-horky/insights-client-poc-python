import argparse
import logging
import subprocess
import sys
from typing import Self

from insights_nest._cmd import abstract
from insights_nest._core import egg


class VerifyPlaybookCommand(abstract.AbstractCommand):
    NAME = "verify-playbook"
    HELP = "verify an Ansible playbook"

    @classmethod
    def create(cls, subparsers) -> Self:
        _ = subparsers.add_parser(cls.NAME, help=cls.HELP)
        return cls()

    def run(self, args: argparse.Namespace) -> None:
        """Run the playbook verifier via the Core."""
        # FIXME The app has no tests and doesn't include any example playbook that would have signature.
        #  This has not been tested end-to-end.
        try:
            output: subprocess.CompletedProcess = egg.Egg().run_app(
                app="ansible.playbook_verifier",
                argv=["--quiet", "--payload", "noop", "--content-type", "noop"],
            )
        except RuntimeError:
            logging.error("Playbook Verifier failed.")
            print("Playbook Verifier failed.")
            return

        print(output.stdout, file=sys.stderr)
