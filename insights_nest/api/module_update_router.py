import dataclasses
import http.client
import json
from typing import Optional, Self

from insights_nest import config
from insights_nest.api import dto
from insights_nest.api.connection import Connection


@dataclasses.dataclass(frozen=True)
class Route:
    url: str

    @classmethod
    def from_json(cls, data: dict) -> Self:
        return dto.from_json(cls, data)


class ModuleUpdateRouterConnection(Connection):
    HOST = config.get().api.host
    PORT = config.get().api.port
    PATH = "/api/module-update-router/v1"


class ModuleUpdateRouter:
    def __init__(self, connection: Optional[ModuleUpdateRouterConnection] = None):
        self.connection = connection if connection is not None else ModuleUpdateRouterConnection()

    def get_module_route(self, module: str) -> Route:
        raw: http.client.HTTPResponse = self.connection.get("/channel", params={"module": module})
        return Route.from_json(json.load(raw))
