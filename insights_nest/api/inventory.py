import dataclasses
import json
import logging
from typing import List, Optional

from insights_nest import config
from insights_nest.api import dto
from insights_nest.api.connection import Connection, Response

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class Host:
    insights_id: str
    subscription_manager_id: Optional[str]
    satellite_id: Optional[str]
    bios_uuid: Optional[str]
    ip_addresses: list[str]
    fqdn: str
    mac_addresses: list[str]
    provider_id: Optional[str]
    provider_type: Optional[str]
    id: str
    account: int
    org_id: int
    display_name: str
    ansible_host: Optional[str]
    facts: list
    reporter: str
    per_reporter_staleness: dict
    stale_timestamp: str
    stale_warning_timestamp: str
    culled_timestamp: str
    created: str
    updated: str
    groups: list
    tags: Optional[list]
    system_profile: Optional[dict]

    @classmethod
    def from_json(cls, data: dict) -> "Host":
        return dto.from_json(cls, data)


@dataclasses.dataclass(frozen=True)
class Hosts:
    total: int
    count: int
    page: int
    per_page: int
    results: List[Host]

    @classmethod
    def from_json(cls, data: dict) -> "Hosts":
        data["results"] = [Host.from_json(host) for host in data.get("results", [])]
        return dto.from_json(cls, data)


class InventoryConnection(Connection):
    HOST = config.get().api.host
    PORT = config.get().api.port
    PATH = "/api/inventory/v1"


class Inventory:
    def __init__(self, connection: Optional[InventoryConnection] = None):
        self.connection = connection if connection is not None else InventoryConnection()

    def get_host(self, machine_id: str) -> Optional[Host]:
        """Get the inventory host entry.

        :param machine_id: The Insights Client UUID.
        """
        # The API endpoint contains many different parameters we can pass. For the
        # use-case of insights-client, where we only want this specific system, we
        # only need the machine-id UUID value. See
        # https://developers.redhat.com/api-catalog/api/inventory#operation-get-/hosts.
        logging.debug("Querying hosts by machine-id.")
        raw: Response = self.connection.get("/hosts", params={"insights_id": machine_id})
        hosts: Hosts = Hosts.from_json(raw.json())
        if len(hosts.results) == 0:
            logger.debug(f"Host with Client UUID '{machine_id}' not found.")
            return None
        if len(hosts.results) > 1:
            logger.warning("Inventory returned more than one host. Using the first one.")
        return hosts.results[0]

    def update_host(
        self,
        insights_id: str,
        *,
        display_name: Optional[str] = None,
        ansible_name: Optional[str] = None,
    ) -> None:
        """Update the inventory host.

        :param insights_id: The Insights Inventory UUID.
        :param display_name: Set custom display name. This does not allow resetting.
        :param ansible_name: Set custom ansible name. Pass an empty string to reset.
        """
        logging.debug("Updating the host.")
        # FIXME Should we prevent zero-length display-name from reaching the API?
        #  Or should we 'reset' it ourselves by passing in the FQDN?

        data = {}
        if display_name is not None:
            data["display_name"] = display_name
        if ansible_name is not None:
            data["ansible_host"] = ansible_name

        _: Response = self.connection.patch(
            f"/hosts/{insights_id}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(data).encode("utf-8"),
        )
        return None

    def delete_host(self, insights_id: str) -> None:
        """Delete the Inventory host.

        :param insights_id: The Insights Inventory UUID.
        """
        logging.debug("Deleting host.")
        self.connection.delete(f"/hosts/{insights_id}")
        return None

    def checkin(self, facts: dict) -> Host:
        """Upload lightweight facts to Inventory.

        :param facts: A set of checkin facts.
        """
        logging.debug("Uploading canonical facts.")
        raw: Response = self.connection.post(
            "/hosts/checkin",
            headers={"Content-Type": "application/json"},
            data=json.dumps(facts).encode("utf-8"),
        )

        if raw.status == 201:
            return Host.from_json(raw.json())

        logging.debug(
            f"API returned unexpected status code {raw.status}. "
            f"Response: {raw.data.decode('utf-8')}."
        )
        raise LookupError(f"Facts were rejected by the server with status code {raw.status}.")
