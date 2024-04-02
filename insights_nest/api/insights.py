import http.client
from typing import Optional

from insights_nest import config
from insights_nest.api.connection import Connection
from insights_nest.api.module_update_router import Route


class InsightsConnection(Connection):
    HOST = config.get().api.host
    PORT = config.get().api.port
    PATH = "/api/v1"


class Insights:
    def __init__(self, connection: Optional[InsightsConnection] = None):
        self.connection = connection if connection is not None else InsightsConnection()

    def get_egg(self, route: Route, *, etag: Optional[str] = None) -> http.client.HTTPResponse:
        """Download the egg.

        :param route: Route (e.g. `/release`, `/testing`) to the release of the egg.
        :param etag: Timestamp of local egg.
        :returns: Binary content (the egg, if present) and headers from the response.
        """
        headers: dict = {}
        if etag is not None:
            headers["If-None-Match"] = etag

        raw: http.client.HTTPResponse = self.connection.get(
            f"/static{route.url}/insights-core.egg", headers=headers
        )
        return raw

    def get_egg_signature(self, route: Route) -> http.client.HTTPResponse:
        raw: http.client.HTTPResponse = self.connection.get(
            f"/static{route.url}/insights-core.egg.asc"
        )
        return raw
