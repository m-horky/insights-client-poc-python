import os.path
import logging
from typing import Optional

from insights_nest.api import inventory


logger = logging.getLogger(__name__)


def is_registered() -> bool:
    """Detect registration status."""
    logger.debug("Determining system registration status.")
    return get_inventory_host() is not None


def get_inventory_host() -> Optional[inventory.Host]:
    logger.debug("Requesting the host from Inventory.")
    if not os.path.isfile("/etc/insights-client/machine-id"):
        logger.debug("machine-id does not exist, we are definitely not registered.")
        return None

    with open("/etc/insights-client/machine-id") as f:
        machine_id = f.read()

    return inventory.Inventory().get_host(machine_id)
