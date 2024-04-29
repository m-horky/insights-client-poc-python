import enum
import glob
import json
import logging
import os.path
import shutil
import sys
import datetime
from typing import Optional

from insights_nest._core import egg, system
from insights_nest.api import inventory

logger = logging.getLogger(__name__)


class Format(enum.Enum):
    HUMAN: str = "HUMAN"
    JSON: str = "JSON"

    @classmethod
    def parse(cls, value: str) -> "Format":
        value = value.lower()
        if value == "human":
            return cls.HUMAN
        if value == "json":
            return cls.JSON
        raise RuntimeError(f"Unknown format: {format}")

    def __str__(self):
        return self.value.lower()

    @classmethod
    def choices(cls) -> list["Format"]:
        return [cls.HUMAN, cls.JSON]


def pprint(message: str, /, format: Format, ok: bool) -> int:
    """Print a message in requested format and return zero or non-zero code."""
    if format == Format.JSON:
        message = json.dumps({"message": message, "ok": ok})
    if format == Format.HUMAN:
        if not ok:
            message = f"Error: {message}"

    print(message, file=sys.stdout)
    return 0 if ok else 1


class Register:
    @classmethod
    def run(cls, *, format: Format) -> int:
        if system.get_inventory_host() is not None:
            return pprint("This host is already registered.", format=format, ok=False)

        logger.info("Registering the host.")

        # FIXME Inventory responds with 404 when you try to check in without uploading an archive before.
        #  Should we try to upload a minimal archive instead, to make the registration quick?
        try:
            egg.Egg.load()

            import insights.anchor.v1

            archive: insights.anchor.v1.SimpleResult = insights.anchor.v1.Checkin.run()
            print(archive.data)
        except RuntimeError:
            logger.exception("Could not collect canonical facts.")
            return pprint("Could not collect canonical facts.", format=format, ok=False)

        try:
            _: inventory.Host = inventory.Inventory().checkin(archive.data)
        except LookupError:
            logger.exception("Could not upload canonical facts to Inventory.")
            return pprint("Error: Could not register with Inventory.", format=format, ok=False)

        # TODO Enable systemd services

        return pprint("The host has been registered.", format=format, ok=True)


class Unregister:
    @classmethod
    def run(cls, *, format: Format) -> int:
        logger.info("Unregistering the host.")

        host: Optional[inventory.Host] = system.get_inventory_host()
        if host is not None:
            logger.debug("Deleting the host from Inventory.")
            inventory.Inventory().delete_host(host.id)

        for path_to_delete in [
            "/etc/insights-client/machine-id",
            "/etc/insights-client/.registered",
            "/etc/rhsm/facts/insights-client.facts",
            *glob.glob("/var/lib/insights/*"),
        ]:
            if os.path.isdir(path_to_delete):
                logger.debug(f"Removing directory {path_to_delete}.")
                shutil.rmtree(path_to_delete)
                continue
            if os.path.exists(path_to_delete):
                logger.debug(f"Removing file {path_to_delete}.")
                os.remove(path_to_delete)
                continue

        logger.debug("Writing /etc/insights-client/.unregistered")
        with open("/etc/insights-client/.unregistered", "w") as f:
            ts: str = datetime.datetime.isoformat(datetime.datetime.now(tz=datetime.timezone.utc))
            f.write(ts)

        # TODO Disable systemd services

        return pprint("The host has been unregistered.", format=format, ok=True)
