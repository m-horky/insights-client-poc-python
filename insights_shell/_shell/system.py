import os.path
import logging

from insights_shell._shell.api import inventory


logger = logging.getLogger(__name__)


def is_registered() -> bool:
    logger.debug("Determining system registration status.")
    if not os.path.isfile("/etc/insights-client/machine-id"):
        return False

    with open("/etc/insights-client/machine-id") as f:
        machine_id = f.read()

    hosts: list[inventory.Host]
    hosts = inventory.Inventory(inventory.InventoryConnection()).get_hosts(machine_id)
    return len(hosts) > 0
