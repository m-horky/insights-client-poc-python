# mypy: ignore-errors

import dataclasses
import logging

logger = logging.getLogger(__name__)


def from_json(cls: dataclasses.dataclass, data: dict):
    """Deserialize the object from a dictionary."""
    fields: set[str] = {field.name for field in dataclasses.fields(cls)}
    omitted: int = len({k for k in data.keys() if k not in fields})
    missing: set[str] = {
        field.name for field in dataclasses.fields(cls) if field.name not in data.keys()
    }
    data = {k: v for k, v in data.items() if k in fields}
    for k in missing:
        data[k] = dataclasses.MISSING
    if omitted:
        logger.debug(f"{omitted} fields were omitted from {cls.__name__}")
    return cls(**data)
