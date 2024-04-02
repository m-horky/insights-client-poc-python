import argparse
import datetime
import glob
import logging
import os.path
import shutil
from typing import Self

from insights_shell.api import inventory
from insights_shell._cmd import abstract
from insights_shell._shell import system


logger = logging.getLogger(__name__)


class UnregisterCommand(abstract.AbstractCommand):
    NAME = "unregister"
    HELP = "unregister the host"

    @classmethod
    def create(cls, subparsers) -> Self:
        parser = subparsers.add_parser(cls.NAME, help=cls.HELP)
        parser.add_argument(abstract.FORMAT_FLAG, **abstract.FORMAT_FLAG_ARGS)
        return cls()

    def run(self, args: argparse.Namespace) -> None:
        logger.info("Unregistering the host.")
        # 1. Query Inventory
        # 2. If we get an object back, call DELETE
        # 3. Ensure machine-id file does not exist
        # 4. Ensure .registered file does not exist
        # 5. Ensure .unregistered file exists
        # 6. Ensure /var/lib/insights/* does not exist
        # 7. Ensure /etc/rhsm/facts/insights-client.json does not exist

        host = system.get_inventory_entry()
        if not host:
            print("The host was not found in Inventory.")
        else:
            logger.debug("Deleting the host from Inventory.")
            inventory.Inventory().delete_host(host.id)

        if os.path.exists("/etc/insights-client/machine-id"):
            logger.debug("Deleting /etc/insights-client/machine-id.")
            os.remove("/etc/insights-client/machine-id")

        if os.path.exists("/etc/insights-client/.registered"):
            logger.debug("Deleting /etc/insights-client/.registered.")
            os.remove("/etc/insights-client/.registered")

        if not os.path.exists("/etc/insights-client/.unregistered"):
            logger.debug("Writing /etc/insights-client/.unregistered")
            with open("/etc/insights-client/.unregistered", "w") as f:
                f.write(
                    datetime.datetime.isoformat(datetime.datetime.now(tz=datetime.timezone.utc))
                )

        var_lib_files = glob.glob("/var/lib/insights/*")
        if var_lib_files:
            logger.debug("Deleting files in /var/lib/insights/")
            for file in var_lib_files:
                if os.path.isfile(file):
                    os.remove(file)
                elif os.path.isdir(file):
                    shutil.rmtree(file)

        if os.path.exists("/etc/rhsm/facts/insights-client.json"):
            logger.debug("Deleting /etc/rhsm/facts/insights-client.json")
            os.remove("/etc/rhsm/facts/insights-client.json")
