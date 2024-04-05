import dataclasses
import http.client
import json
import logging
import os
import ssl
import time
import urllib.request
import urllib.parse
from typing import Optional

from insights_nest import config

logger = logging.getLogger(__name__)


# TODO Create Request dataclass and add it as a field to the Response?


@dataclasses.dataclass(frozen=True)
class Response:
    status: int
    headers: dict[str, str]
    data: bytes

    def is_json(self) -> bool:
        for k, v in self.headers.items():
            if k.lower() == "content-type" and v.lower() == "application/json":
                return True
        return False

    def json(self) -> dict:
        return json.loads(self.data)


class Connection:
    HOST: str
    """Hostname. E.g. `example.org`."""
    PORT: int
    """Application port. E.g. `443`."""
    PATH: str
    """API endpoint root. E.g. `/api/v1`."""

    # TODO Add support for proxy
    # TODO Add support for insecure communication
    # TODO Add support for timeouts
    # TODO Add support for connection reuse

    def _create_tls_context(self) -> ssl.SSLContext:
        cfg: config.Configuration = config.get()

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.load_cert_chain(
            certfile=f"{cfg.network.identity_certificate!s}",
            keyfile=f"{cfg.network.identity_key!s}",
        )
        ctx.load_verify_locations(cafile=f"{cfg.network.ca_certificates!s}")
        return ctx

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        data: Optional[bytes] = None,
    ) -> Response:
        url = f"{self.PATH}{endpoint}"
        if params:
            url += f"?{urllib.parse.urlencode(params)}"
        if headers is None:
            headers = {}

        context: ssl.SSLContext = self._create_tls_context()
        conn = http.client.HTTPSConnection(host=self.HOST, port=self.PORT, context=context)

        logger.debug(f"Request {method} {self.HOST}:{self.PORT}{url} (headers={headers})")
        conn.request(method=method, url=url, headers=headers, body=data)

        now: float = time.time()
        raw: http.client.HTTPResponse = conn.getresponse()
        delta: float = time.time() - now
        logger.debug(f"Response with code {raw.status} after {delta * 100:.1f} ms")

        rich = Response(
            status=raw.status,
            headers=dict(raw.headers.items()),
            data=raw.read(),
        )

        if os.environ.get("NEST_DEBUG_HTTP", None) is not None:
            print("NEST_DEBUG_HTTP", rich)

        return rich

    def get(
        self,
        endpoint: str,
        *,
        params: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        data: Optional[bytes] = None,
    ) -> Response:
        return self._request("GET", endpoint, params=params, headers=headers, data=data)

    def put(
        self,
        endpoint: str,
        *,
        params: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        data: Optional[bytes] = None,
    ) -> Response:
        return self._request("PUT", endpoint, params=params, headers=headers, data=data)

    def post(
        self,
        endpoint: str,
        *,
        params: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        data: Optional[bytes] = None,
    ) -> Response:
        return self._request("POST", endpoint, params=params, headers=headers, data=data)

    def patch(
        self,
        endpoint: str,
        *,
        params: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        data: Optional[bytes] = None,
    ) -> Response:
        return self._request("PATCH", endpoint, params=params, headers=headers, data=data)

    def delete(
        self,
        endpoint: str,
        *,
        params: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        data: Optional[bytes] = None,
    ) -> Response:
        return self._request("DELETE", endpoint, params=params, headers=headers, data=data)
