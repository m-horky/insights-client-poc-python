import http.client
import json
import logging
import ssl
import time
import urllib.request
import urllib.parse
from typing import Optional


logger = logging.getLogger(__name__)


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
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.load_cert_chain(
            certfile="/etc/pki/consumer/cert.pem",
            keyfile="/etc/pki/consumer/key.pem",
        )
        ctx.load_verify_locations(cafile="/etc/pki/tls/cert.pem")
        return ctx

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        data=None,
    ) -> dict:
        url = f"{self.PATH}{endpoint}"
        if params:
            url += f"?{urllib.parse.urlencode(params)}"
        if headers is None:
            headers = {}

        context: ssl.SSLContext = self._create_tls_context()
        conn = http.client.HTTPSConnection(host=self.HOST, port=self.PORT, context=context)

        logger.debug(f"Request {method} {self.HOST}:{self.PORT}{url} ({headers=})")
        conn.request(method=method, url=url, headers=headers, body=data)

        now: float = time.time()
        response: http.client.HTTPResponse = conn.getresponse()
        delta: float = time.time() - now

        logger.debug(f"Response with code {response.status} after {delta * 100:.1f} ms")

        raw = response.read()
        if not len(raw):
            return {}

        try:
            return json.loads(raw)
        except json.decoder.JSONDecodeError:
            logger.debug(f"Response could not be deserialized: {raw}")
            raise

    def get(
        self,
        endpoint: str,
        *,
        params: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        data=None,
    ) -> dict:
        return self._request("GET", endpoint, params=params, headers=headers, data=data)

    def put(
        self,
        endpoint: str,
        *,
        params: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        data=None,
    ) -> dict:
        return self._request("PUT", endpoint, params=params, headers=headers, data=data)

    def post(
        self,
        endpoint: str,
        *,
        params: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        data=None,
    ) -> dict:
        return self._request("POST", endpoint, params=params, headers=headers, data=data)

    def delete(
        self,
        endpoint: str,
        *,
        params: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        data=None,
    ) -> dict:
        return self._request("DELETE", endpoint, params=params, headers=headers, data=data)
