import argparse
import logging
import os
import pathlib
import sys

from insights_nest._cmd import abstract
from insights_nest._core import system, egg
from insights_nest.api import ingress

logger = logging.getLogger(__name__)


class AdvisorScanCommand(abstract.AbstractCommand):
    NAME = "scan-advisor"
    HELP = "scan the system and upload the results to Insights Advisor"

    @classmethod
    def create(cls, subparsers) -> "AdvisorScanCommand":
        _ = subparsers.add_parser(cls.NAME, help=cls.HELP)
        # TODO Add Core parameters
        return cls()

    def run(self, args: argparse.Namespace) -> None:
        if not system.is_registered():
            print("This host is not registered.")
            sys.exit(1)

        try:
            canonical_facts: dict = egg.Egg().run("checkin")
        except RuntimeError:
            logger.error("Could not collect canonical facts.")
            print("Could not collect canonical facts.")
            return

        result = egg.Egg().run("advisor")
        payload_path = pathlib.Path(result["payload"])

        ingress.Ingress().upload(
            archive=payload_path,
            content_type=result["content_type"],
            facts=canonical_facts,
        )
        if payload_path.exists():
            os.remove(payload_path)
