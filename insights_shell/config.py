import configparser
import dataclasses
import pathlib


CONFIGURATION_FILE_PATH = pathlib.Path("/etc/insights-client/insights-shell.conf")
RHSM_CONFIGURATION_FILE_PATH = pathlib.Path("/etc/rhsm/rhsm.conf")


@dataclasses.dataclass(frozen=True)
class Proxy:
    host: str
    scheme: str
    port: int
    username: str
    password: str

    @property
    def ok(self):
        if not self.host or not self.port:
            return False
        return True


@dataclasses.dataclass(frozen=True)
class Network:
    proxy: Proxy
    identity_directory: pathlib.Path

    @property
    def identity_certificate(self) -> pathlib.Path:
        return self.identity_directory / "cert.pem"

    @property
    def identity_key(self) -> pathlib.Path:
        return self.identity_directory / "key.pem"


@dataclasses.dataclass(frozen=True)
class API:
    host: str
    port: int
    insecure: bool
    """Do not verify TLS certificates."""
    ca_certificates: pathlib.Path
    """TLS certificate bundle."""


@dataclasses.dataclass(frozen=True)
class Egg:
    egg_directory: pathlib.Path
    """Directory containing eggs."""
    metadata_directory: pathlib.Path
    """Directory containing configuration and runtime files."""
    gpg_public_key: pathlib.Path
    """Path to public GPG key used to verify the eggs."""
    canary: bool
    """Use canary egg instead of production one."""


@dataclasses.dataclass(frozen=True)
class Logging:
    levels: dict[str, str]
    """Mapping between python modules and requested log levels."""


@dataclasses.dataclass(frozen=True)
class Configuration:
    api: API
    network: Network
    egg: Egg
    logging: Logging


def _get_network_configuration() -> Network:
    cfg = configparser.ConfigParser()
    cfg.read(f"{RHSM_CONFIGURATION_FILE_PATH!s}")

    try:
        port: int = cfg.getint("server", "proxy_port")
    except ValueError:
        port = 0

    return Network(
        proxy=Proxy(
            host=cfg.get("server", "proxy_hostname"),
            scheme=cfg.get("server", "proxy_scheme"),
            port=port,
            username=cfg.get("server", "proxy_user"),
            password=cfg.get("server", "proxy_password"),
        ),
        identity_directory=pathlib.Path(cfg.get("rhsm", "consumerCertDir")),
    )


def get() -> Configuration:
    cfg = configparser.ConfigParser()
    cfg.read("/etc/insights-client/insights-shell.conf")

    return Configuration(
        network=_get_network_configuration(),
        api=API(
            host=cfg.get("api", "host"),
            port=cfg.getint("api", "port"),
            insecure=cfg.getboolean("api", "insecure"),
            ca_certificates=pathlib.Path(cfg.get("api", "ca_certificates")),
        ),
        egg=Egg(
            egg_directory=pathlib.Path(cfg.get("egg", "egg_directory")),
            metadata_directory=pathlib.Path(cfg.get("egg", "metadata_directory")),
            gpg_public_key=pathlib.Path(cfg.get("egg", "gpg_public_key")),
            canary=cfg.getboolean("egg", "canary"),
        ),
        logging=Logging(
            levels=dict([s for s in cfg.items() if s[0] == "logging"][0][1]),
        ),
    )
