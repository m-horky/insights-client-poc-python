import os.path
import logging

from insights_shell.api import inventory


logger = logging.getLogger(__name__)


def is_registered() -> bool:
    """Detect registration status."""
    logger.debug("Determining system registration status.")
    return get_inventory_entry() is not None


def get_inventory_entry() -> inventory.Host | None:
    logger.debug("Requesting the host from Inventory.")
    if not os.path.isfile("/etc/insights-client/machine-id"):
        return None

    with open("/etc/insights-client/machine-id") as f:
        machine_id = f.read()

    hosts: list[inventory.Host]
    hosts = inventory.Inventory(inventory.InventoryConnection()).get_hosts(machine_id)

    if not hosts:
        return None
    if len(hosts) > 1:
        logger.debug(
            "Inventory returned more than one host. Using the first one and ignoring others."
        )
    return hosts[0]
