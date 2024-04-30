import enum


class Format(enum.Enum):
    HUMAN: str = "HUMAN"
    JSON: str = "JSON"

    @classmethod
    def parse(cls, value: str) -> "Format":
        value = value.lower()
        if value == "human":
            return cls.HUMAN
        if value == "json":
            return cls.JSON
        raise RuntimeError(f"Unknown format: {format}")

    def __str__(self):
        return self.value.lower()

    @classmethod
    def choices(cls) -> list["Format"]:
        return [cls.HUMAN, cls.JSON]
