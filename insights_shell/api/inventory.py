import dataclasses
import http.client
import json
import logging
from typing import List, Optional, Self

from insights_shell import config
from insights_shell.api import dto
from insights_shell.api.connection import Connection

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
    def from_json(cls, data: dict):
        return dto.from_json(cls, data)


@dataclasses.dataclass(frozen=True)
class Hosts:
    total: int
    count: int
    page: int
    per_page: int
    results: List[Host]

    @classmethod
    def from_json(cls, data: dict) -> Self:
        data["results"] = [Host.from_json(host) for host in data["results"]]
        return dto.from_json(cls, data)


class InventoryConnection(Connection):
    HOST = config.get().api.host
    PORT = config.get().api.port
    PATH = "/api/inventory/v1"


class Inventory:
    def __init__(self, connection: Optional[InventoryConnection] = None):
        self.connection = connection if connection is not None else InventoryConnection()

    def get_hosts(self, machine_id: str) -> list[Host]:
        # FIXME This should probably iterate over all the hosts? The endpoint is paginated.
        logging.debug("Getting the list of hosts.")
        raw: http.client.HTTPResponse = self.connection.get(
            "/hosts", params={"insights_id": machine_id}
        )
        return Hosts.from_json(json.load(raw)).results

    def delete_host(self, insights_id: str) -> None:
        logging.debug(f"Deleting host.")
        self.connection.delete(f"/hosts/{insights_id}")
        return None
