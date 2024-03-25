import dataclasses
from typing import List, Optional

from insights_shell._shell.api.connection import Connection


@dataclasses.dataclass(frozen=True)
class Host:
    insights_id: str
    subscription_manger_id: Optional[str]
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


@dataclasses.dataclass(frozen=True)
class Hosts:
    total: int
    count: int
    page: int
    per_page: int
    results: List[Host]


class InventoryConnection(Connection):
    # TODO Detect stage
    # URL = "https://cert.cloud.redhat.com/api/inventory/v1"
    HOST = "cert.cloud.stage.redhat.com"
    PORT = 443
    PATH = "/api/inventory/v1"


class Inventory:
    def __init__(self, connection: InventoryConnection):
        self.connection = connection

    def get_hosts(self, machine_id: str) -> list[Host]:
        # FIXME This should probably iterate over all the hosts?
        raw: dict = self.connection.get("/hosts", params={"insights_id": machine_id})
        return Hosts(**raw).results

    def delete_host(self, insights_id: str) -> None:
        # This method does not return anything
        self.connection.delete(f"/hosts/{insights_id}")
