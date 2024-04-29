import argparse
import logging
import os
import pathlib
import sys

from insights_nest._cmd import abstract
from insights_nest._core import system, egg
from insights_nest.api import ingress


logger = logging.getLogger(__name__)


class ComplianceScanCommand(abstract.AbstractCommand):
    NAME = "scan-compliance"
    HELP = "scan the system for compliance and upload the results to Insights"

    @classmethod
    def create(cls, subparsers) -> "ComplianceScanCommand":
        _ = subparsers.add_parser(cls.NAME, help=cls.HELP)
        # TODO Add Compliance parameters
        return cls()

    def run(self, args: argparse.Namespace) -> None:
        if system.get_inventory_host() is None:
            print("This host is not registered.")
            sys.exit(1)

        try:
            canonical_facts: dict = egg.Egg().run("checkin")
        except RuntimeError:
            logger.error("Could not collect canonical facts.")
            print("Could not collect canonical facts.")
            return

        result = egg.Egg().run("compliance")
        payload_path = pathlib.Path(result["payload"])

        ingress.Ingress().upload(
            archive=payload_path,
            content_type=result["content_type"],
            facts=canonical_facts,
        )
        if payload_path.exists():
            os.remove(payload_path)
