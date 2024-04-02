import configparser
import dataclasses
import functools
import pathlib


CONFIGURATION_FILE_PATH = pathlib.Path("/etc/insights-client/insights-nest.conf")
CONFIGURATION_DIRECTORY_PATH = pathlib.Path("/etc/insights-client/insights-nest.conf.d/")
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
    """Path to the RHSM identity certificate keypair."""
    ca_certificates: pathlib.Path
    """TLS certificate bundle."""
    insecure: bool
    """Do not verify TLS certificates."""

    @property
    def identity_certificate(self) -> pathlib.Path:
        """RHSM identity certificate."""
        return self.identity_directory / "cert.pem"

    @property
    def identity_key(self) -> pathlib.Path:
        """RHSM identity private key."""
        return self.identity_directory / "key.pem"


@dataclasses.dataclass(frozen=True)
class API:
    host: str
    port: int


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


_RHSM_CONFIGURATION_DEFAULTS: dict = {
    "server": {
        "proxy_hostname": "",
        "proxy_scheme": "http",
        "proxy_port": "",
        "proxy_user": "",
        "proxy_password": "",
    },
}

_CONFIGURATION_DEFAULTS: dict = {
    "api": {"host": "cert.cloud.redhat.com", "port": 443},
    "network": {
        "ca_certificates": "/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem",
        "insecure": False,
    },
    "egg": {
        "egg_directory": "/var/lib/insights",
        "metadata_directory": "/etc/insights-client/",
        "gpg_public_key": "/etc/insights-client/redhattools.pub.gpg",
        "canary": False,
    },
    "logging": {"insights_nest": "INFO", "insights_nest.api": "WARNING"},
}


@functools.cache
def get() -> Configuration:
    """Load the configuration."""

    rhsm_cfg = configparser.ConfigParser()
    rhsm_cfg.read_dict(_RHSM_CONFIGURATION_DEFAULTS)
    rhsm_cfg.read(f"{RHSM_CONFIGURATION_FILE_PATH!s}")

    try:
        network_proxy_port: int = rhsm_cfg.getint("server", "proxy_port")
    except ValueError:
        network_proxy_port = 0

    cfg = configparser.ConfigParser()
    cfg.read_dict(_CONFIGURATION_DEFAULTS)
    cfg.read(f"{CONFIGURATION_FILE_PATH!s}")
    for file in sorted(CONFIGURATION_DIRECTORY_PATH.glob("*.conf")):
        cfg.read(f"{file!s}")

    return Configuration(
        network=Network(
            ca_certificates=pathlib.Path(cfg.get("network", "ca_certificates")),
            insecure=cfg.getboolean("network", "insecure"),
            proxy=Proxy(
                host=rhsm_cfg.get("server", "proxy_hostname"),
                scheme=rhsm_cfg.get("server", "proxy_scheme"),
                port=network_proxy_port,
                username=rhsm_cfg.get("server", "proxy_user"),
                password=rhsm_cfg.get("server", "proxy_password"),
            ),
            identity_directory=pathlib.Path(rhsm_cfg.get("rhsm", "consumerCertDir")),
        ),
        api=API(
            host=cfg.get("api", "host"),
            port=cfg.getint("api", "port"),
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
