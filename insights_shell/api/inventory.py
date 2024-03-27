import dataclasses
from typing import List, Optional, Self

from insights_shell.api.connection import Connection


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

    @classmethod
    def from_json(cls, data: dict) -> Self:
        return cls(**data)


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
        return cls(**data)


class InventoryConnection(Connection):
    # TODO Detect stage
    # URL = "https://cert.cloud.redhat.com/api/inventory/v1"
    HOST = "cert.cloud.stage.redhat.com"
    PORT = 443
    PATH = "/api/inventory/v1"


class Inventory:
    def __init__(self, connection: Optional[InventoryConnection] = None):
        self.connection = connection if connection is not None else InventoryConnection()

    def get_hosts(self, machine_id: str) -> list[Host]:
        # FIXME This should probably iterate over all the hosts?
        raw: dict = self.connection.get("/hosts", params={"insights_id": machine_id})
        return Hosts.from_json(raw).results

    def delete_host(self, insights_id: str) -> None:
        self.connection.delete(f"/hosts/{insights_id}")
        return None
