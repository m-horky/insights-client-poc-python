import enum
import logging
import os.path
import pathlib
import shutil
import subprocess
import sys
import tempfile
from typing import Optional

from insights_nest import config
from insights_nest.api import module_update_router
from insights_nest.api import insights
from insights_nest.api.connection import Response

logger = logging.getLogger(__name__)

UNTRUSTED_EGG_PATH: pathlib.Path = config.get().egg.egg_directory / "untrusted.egg"
UNTRUSTED_SIG_PATH: pathlib.Path = config.get().egg.egg_directory / "untrusted.egg.asc"
TRUSTED_EGG_PATH: pathlib.Path = config.get().egg.egg_directory / "current.egg"
TRUSTED_SIG_PATH: pathlib.Path = config.get().egg.egg_directory / "current.egg.asc"

EGG_ETAG_PATH: pathlib.Path = config.get().egg.metadata_directory / ".insights-core.etag"
SIG_ETAG_PATH: pathlib.Path = config.get().egg.metadata_directory / ".insights-core-gpg-sig.etag"


TEMPORARY_GPG_HOME_PARENT_DIRECTORY = pathlib.Path("/var/lib/insights/")


class EggUpdateResult(enum.Enum):
    NO_UPDATE_NEEDED = "The egg is already up to date."
    UPDATE_SUCCESS = "The egg has been updated to newer version."
    FETCH_FAILED = "The egg or its signature could not be downloaded."
    VERIFICATION_FAILED = "The egg signature could not be verified."

    @property
    def ok(self) -> bool:
        return self in (type(self).UPDATE_SUCCESS, type(self).NO_UPDATE_NEEDED)


def _get_route() -> module_update_router.Route:
    logger.debug("Fetching route.")

    if config.get().egg.canary:
        logger.debug("Using canary egg route as requested in the configuration file.")
        return module_update_router.Route(url="/testing")

    route = module_update_router.ModuleUpdateRouter().get_module_route("insights-core")
    return route


def _update_egg(*, route: module_update_router.Route, force: bool = False) -> EggUpdateResult:
    """Update the egg binary."""
    etag: Optional[str] = None
    if os.path.exists(EGG_ETAG_PATH):
        with open(EGG_ETAG_PATH, "r") as f:
            etag = f.read()

    logger.debug("Fetching the egg.")
    egg: Response = insights.Insights().get_egg(route=route, etag=etag)

    new_etag: str = egg.headers.get("Etag", "")
    if etag == new_etag:
        logger.debug("Etag matches, we don't need to download anything.")
        if not force:
            return EggUpdateResult.NO_UPDATE_NEEDED
        logger.debug("Force downloading the egg anyway.")

    logger.debug(f"Updating egg etag {EGG_ETAG_PATH!s}: {etag} -> {new_etag}.")
    with EGG_ETAG_PATH.open("w") as f:
        f.write(new_etag)

    logger.debug(f"Saving the egg into {UNTRUSTED_EGG_PATH!s} (size is {len(egg.data)} bytes).")
    with UNTRUSTED_EGG_PATH.open("wb") as f:
        f.write(egg.data)

    return EggUpdateResult.UPDATE_SUCCESS


def _update_egg_signature(*, route: module_update_router.Route):
    """Update the egg binary signature."""
    logger.debug("Fetching the egg signature.")
    signature: Response = insights.Insights().get_egg_signature(route=route)

    logger.debug(
        f"Saving the egg signature into {UNTRUSTED_SIG_PATH!s} (size is {len(signature.data)} bytes)."
    )
    with UNTRUSTED_SIG_PATH.open("wb") as f:
        f.write(signature.data)


def _remove_gpg_home(home: str) -> None:
    """Clean GPG's temporary home directory."""
    shutdown_process = subprocess.run(
        ["/usr/bin/gpgconf", "--homedir", home, "--kill", "all"],
        capture_output=True,
        text=True,
    )
    if shutdown_process.returncode != 0:
        logger.debug(
            "Could not clean GPG's temporary home, "
            f"'gpgconf' exited with code '{shutdown_process.returncode}'"
        )
        return

    shutil.rmtree(home)


def _format_subprocess_std(process: subprocess.CompletedProcess) -> str:
    """Format the standard output and error of a subprocess for easy logging."""
    return "\n".join(
        [
            *[f"stdout>{line}" for line in process.stdout.splitlines()],
            *[f"stderr>{line}" for line in process.stderr.splitlines()],
        ]
    )


def _verify_egg_signature(egg: pathlib.Path, signature: pathlib.Path) -> bool:
    """Verify the GPG signature of an egg.

    :returns bool: `True` if the signature matches.
    """
    logger.info("Verifying the egg signature.")
    home = tempfile.mkdtemp(dir=TEMPORARY_GPG_HOME_PARENT_DIRECTORY)

    import_process = subprocess.run(
        ["/usr/bin/gpg", "--homedir", home, "--import", config.get().egg.gpg_public_key],
        capture_output=True,
        text=True,
    )
    if import_process.returncode != 0:
        logger.debug(f"Could not import the GPG key.\n{_format_subprocess_std(import_process)}")
        _remove_gpg_home(home)
        return False

    verify_process = subprocess.run(
        ["/usr/bin/gpg", "--homedir", home, "--verify", f"{signature!s}", f"{egg!s}"],
        capture_output=True,
        text=True,
    )
    if verify_process.returncode != 0:
        logger.debug(
            f"Verification of the GPG signature failed.\n{_format_subprocess_std(verify_process)}"
        )
        _remove_gpg_home(home)
        return False

    return True


def update(*, force: bool = False) -> EggUpdateResult:
    """Update the egg to a new release.

    :param force: Always download the egg, even if it already exists locally.
    """
    logger.info("Updating the Egg.")
    # 1. Fetch the egg and signature into `untrusted.egg`
    # 2. Verify the signature
    # 3. Rename it as `current.egg`

    route: module_update_router.Route = _get_route()

    try:
        update_status: EggUpdateResult = _update_egg(route=route, force=force)
    except Exception:
        logger.exception("Egg update failed.")
        return EggUpdateResult.FETCH_FAILED

    if update_status == EggUpdateResult.NO_UPDATE_NEEDED:
        logger.info("Local egg is already up to date.")
        return EggUpdateResult.NO_UPDATE_NEEDED

    try:
        _update_egg_signature(route=route)
    except Exception:
        logger.exception("Egg signature update failed.")
        return EggUpdateResult.FETCH_FAILED

    ok: bool = _verify_egg_signature(UNTRUSTED_EGG_PATH, UNTRUSTED_SIG_PATH)
    if not ok:
        logger.debug(
            "Cryptographic verification failed, removing both the egg and its signature."
        )
        UNTRUSTED_EGG_PATH.unlink(missing_ok=True)
        UNTRUSTED_SIG_PATH.unlink(missing_ok=True)
        return EggUpdateResult.VERIFICATION_FAILED

    logger.debug("Moving the verified egg in place.")
    shutil.move(UNTRUSTED_EGG_PATH, TRUSTED_EGG_PATH)
    shutil.move(UNTRUSTED_SIG_PATH, TRUSTED_SIG_PATH)
    return EggUpdateResult.UPDATE_SUCCESS


class Egg:
    """Egg interactions.

    :param path: Path to the egg file.
    """

    path: pathlib.Path

    def __init__(self, path: Optional[pathlib.Path] = None):
        """Create an egg reference.

        :param path: Path to the egg file. If `None`, it is automatically discovered.
        """
        if path is None:
            path = type(self)._discover_path()
        self.path = path

        logger.info(
            "Prepared egg {version} from {path}".format(
                version=self.version(include_commit=True, include_release=True),
                path=path,
            )
        )

    @property
    def pythonpath(self) -> str:
        """Create a PYTHONPATH to be passed to the egg."""
        paths: list[str] = [f"{self.path!s}"]
        pythonpath: str = os.environ.get("PYTHONPATH", "")
        if pythonpath:
            paths.append(pythonpath)
        return ":".join(paths)

    @classmethod
    def _discover_path(cls) -> pathlib.Path:
        """Get the path to the egg that should be used.

        If en `EGG` environment variable is set, the path it points to will be used as the egg.
        If it does not exist, `RuntimeError` will be raised.

        Otherwise,
        - the CURRENT (the latest downloaded version) or
        - the RPM (the egg shipped with the RPM package)
        will be used.

        :raises RuntimeError: No egg was found.
        """
        env = os.environ.get("EGG", None)
        if env is not None:
            env_egg = pathlib.Path(env)
            if env_egg.exists():
                logger.debug("Using the ENV egg.")
                return env_egg
            logger.error(f"EGG={env} was specified, but could not be found.")
            raise RuntimeError("The ENV egg could not be found.")

        paths: dict[str, pathlib.Path] = {
            "CURRENT": TRUSTED_EGG_PATH,
            "RPM": config.get().egg.metadata_directory / "rpm.egg",
        }

        for name, path in paths.items():
            if path.exists():
                logger.debug(f"Using the {name} egg.")
                return path

        raise RuntimeError("No egg found.")

    def version(
        self,
        *,
        include_release: bool = True,
        include_commit: bool = False,
    ) -> str:
        """Get the version of the egg.

        :param include_release:
            Include the egg release, not just the MAJOR.MINOR.PATCH version.
        :param include_commit:
            Include the egg release commit, not just the MAJOR.MINOR.PATCH version.
        :raises RuntimeError: The subprocess failed.
        """
        query: str = "insights.package_info['VERSION']"
        if include_release:
            query += "+ '-' + insights.package_info['RELEASE']"
        if include_commit:
            query += "+ '+' + insights.package_info['COMMIT']"

        version_process = subprocess.run(
            ["python3", "-c", f"import insights; print({query})"],
            env={"PYTHONPATH": self.pythonpath},
            capture_output=True,
            text=True,
        )
        if version_process.returncode != 0:
            logger.error(
                f"Could not query for the egg version.\n{_format_subprocess_std(version_process)}"
            )
            raise RuntimeError("Could not query for the egg version.")

        return version_process.stdout.strip()

    @classmethod
    def load(cls) -> None:
        """Dynamically load the egg into PYTHONPATH."""
        egg_path: pathlib.Path = cls._discover_path()
        logger.debug(f"Adding egg path {egg_path} into PYTHONPATH.")
        sys.path = [f"{egg_path!s}"] + sys.path
