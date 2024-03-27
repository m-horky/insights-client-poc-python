import dataclasses
import http.client
import json
from typing import Optional, Self

from insights_shell.api.connection import Connection


@dataclasses.dataclass(frozen=True)
class Route:
    url: str

    @classmethod
    def from_json(cls, data: dict) -> Self:
        return cls(**data)


class ModuleUpdateRouterConnection(Connection):
    # TODO Detect stage
    HOST = "cert.cloud.stage.redhat.com"
    PORT = 443
    PATH = "/api/module-update-router/v1"


class ModuleUpdateRouter:
    def __init__(self, connection: Optional[ModuleUpdateRouterConnection] = None):
        self.connection = connection if connection is not None else ModuleUpdateRouterConnection()

    def get_module_route(self, module: str) -> Route:
        raw: http.client.HTTPResponse = self.connection.get("/channel", params={"module": module})
        return Route.from_json(json.load(raw))
