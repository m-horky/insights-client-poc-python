import os.path
import logging
from typing import Optional

from insights_nest.api import inventory


logger = logging.getLogger(__name__)


def get_inventory_host() -> Optional[inventory.Host]:
    """Request host information from Inventory.

    :returns: Host object if it exists in Inventory; None otherwise.
    """
    logger.debug("Requesting the host from Inventory.")
    if not os.path.isfile("/etc/insights-client/machine-id"):
        logger.debug("machine-id does not exist, host is definitely not registered.")
        return None

    with open("/etc/insights-client/machine-id") as f:
        machine_id = f.read()

    return inventory.Inventory().get_host(machine_id)
