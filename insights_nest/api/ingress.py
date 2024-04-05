import dataclasses
import json
import pathlib
from typing import Optional

from insights_nest import config
from insights_nest.api import form, dto
from insights_nest.api.connection import Connection, Response


@dataclasses.dataclass
class Upload:
    account: int
    org_id: int

    @classmethod
    def from_json(cls, data: dict) -> "Upload":
        return dto.from_json(cls, data)


@dataclasses.dataclass
class UploadResponse:
    request_id: str
    upload: Upload

    @classmethod
    def from_json(cls, data: dict) -> "UploadResponse":
        data["upload"] = Upload.from_json(data["upload"])
        return dto.from_json(cls, data)


class IngressConnection(Connection):
    HOST = config.get().api.host
    PORT = config.get().api.port
    PATH = "/api/ingress/v1"


class Ingress:
    def __init__(self, connection: Optional[IngressConnection] = None):
        self.connection = connection if connection is not None else IngressConnection()

    def upload(self, archive: pathlib.Path, content_type: str, facts: dict):
        """Upload an archive to Insights.

        :param archive: Path to payload file.
        :param content_type: Content type of the payload file.
        :param facts: Canonical facts.
        """
        payload = form.Form()
        payload.add_file(
            field="file",
            filename=archive.name,
            content_type=content_type,
            content=archive.open("rb").read(),
        )
        payload.add_file(
            field="metadata",
            filename="metadata",
            content_type=None,
            content=json.dumps(facts).encode("utf-8"),
        )

        raw: Response = self.connection.post(
            "/upload",
            headers={"Content-Type": payload.content_type},
            data=payload.build(),
        )
        return UploadResponse.from_json(raw.json())
