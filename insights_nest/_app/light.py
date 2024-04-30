import json
from typing import Optional

from insights_nest._app import flag, pprint, logger
from insights_nest._core import system, egg
from insights_nest.api import inventory


class Checkin:
    @classmethod
    def run(cls, *, format: flag.Format):
        if system.get_inventory_host() is None:
            return pprint("This host is not registered.", format=format, ok=False)

        logger.info("Checking in.")

        try:
            egg.Egg.load()
            import insights.anchor.v1
        except ImportError:
            logger.exception("Could not load the Insights Core.")
            return pprint("Could not load the Insights Core.", format=format, ok=False)

        try:
            facts_archive: insights.anchor.v1.SimpleResult = (
                insights.anchor.v1.CanonicalFacts().run()
            )
        except Exception:
            logger.exception("Could not collect canonical facts.")
            return pprint("Could not collect canonical facts.", format=format, ok=False)

        try:
            _: inventory.Host = inventory.Inventory().checkin(facts_archive.data)
        except Exception:
            logger.exception("Could not check in with Inventory.")
            return pprint("Could not check in with Inventory.", format=format, ok=False)

        return pprint("Successfully checked in.", format=format, ok=True)


class Identity:
    @classmethod
    def run(cls, *, format: flag.Format):
        """Display system status."""
        host: Optional[inventory.Host] = system.get_inventory_host()
        if host is None:
            return pprint("This host is not registered.", format=format, ok=True)

        logger.info("Determining system identity.")

        if format == flag.Format.JSON:
            print(
                json.dumps(
                    {
                        "insights_id": getattr(host, "id", None),
                        "insights_client_id": getattr(host, "insights_id", None),
                        "subscription_manager_id": getattr(host, "subscription_manager_id", None),
                        "fqdn": getattr(host, "fqdn", None),
                        "display_name": getattr(host, "display_name", None),
                        "ansible_host": getattr(host, "ansible_host", None),
                    }
                )
            )
            return 0

        if format == flag.Format.HUMAN:
            print(f"Insights UUID:             {host.id or 'unknown'}")
            print(f"Insights Client UUID:      {host.insights_id or 'unknown'}")
            print(f"Subscription Manager UUID: {host.subscription_manager_id or 'unknown'}")

            if host.fqdn:
                print(f"FQDN:                      {host.fqdn}")
            if host.display_name:
                print(f"Display name:              {host.display_name}")
            if host.ansible_host:
                print(f"Ansible hostname:          {host.ansible_host}")
            return 0
