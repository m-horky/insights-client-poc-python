import uuid
from typing import Optional


class Form:
    """Object for multipart/form-data uploads."""

    def __init__(self):
        self.boundary: bytes = str(uuid.uuid4()).encode("utf-8")
        self.fields: list[tuple[str, bytes]] = []
        self.files: list[tuple[str, str, Optional[str], bytes]] = []

    @property
    def content_type(self):
        return "multipart/form-data; boundary={boundary}".format(
            boundary=self.boundary.decode("utf-8")
        )

    def add_field(self, *, field: str, content: bytes):
        self.fields.append((field, content))

    def add_file(self, *, field: str, filename: str, content_type: Optional[str], content: bytes):
        self.files.append(
            (field, filename, content_type, content),
        )

    def build(self) -> bytes:
        lines: list[bytes] = []

        for field, content in self.fields:
            lines.append(b"--" + self.boundary)
            lines.append(f'Content-Disposition: form-data; name="{field}"'.encode("utf-8"))
            lines.append(b"")
            lines.append(content)

        for field, filename, content_type, content in self.files:
            lines.append(b"--" + self.boundary)
            lines.append(
                f'Content-Disposition: form-data; name="{field}"; filename="{filename}"'.encode(
                    "utf-8"
                )
            )
            if content_type is not None:
                lines.append(f"Content-Type: {content_type}".encode("utf-8"))
            lines.append(b"")
            lines.append(content)

        lines.append(b"--" + self.boundary + b"--")

        return b"\r\n".join(lines) + b"\r\n"
