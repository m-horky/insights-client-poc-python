import http.client
import logging
import os.path
import pathlib
import shutil
import subprocess
import tempfile
from typing import Optional

from insights_shell import config
from insights_shell.api import module_update_router
from insights_shell.api import insights

logger = logging.getLogger(__name__)

UNTRUSTED_EGG_PATH = pathlib.Path("/var/lib/insights/untrusted.egg")
UNTRUSTED_SIG_PATH = pathlib.Path("/var/lib/insights/untrusted.egg.asc")
TRUSTED_EGG_PATH = pathlib.Path("/var/lib/insights/current.egg")
TRUSTED_SIG_PATH = pathlib.Path("/var/lib/insights/current.egg.asc")

EGG_ETAG_PATH = pathlib.Path("/etc/insights-client/.insights-core.etag")
SIG_ETAG_PATH = pathlib.Path("/etc/insights-client/.insights-core-gpg-sig.etag")

TEMPORARY_GPG_HOME_PARENT_DIRECTORY = pathlib.Path("/var/lib/insights/")
GPG_KEY_PATH = pathlib.Path("/etc/insights-client/redhattools.pub.gpg")


def _get_route() -> module_update_router.Route:
    logger.debug("Fetching route.")

    if config.get().egg.canary:
        logger.debug("Using canary egg route as requested in the configuration file.")
        return module_update_router.Route(url="/testing")

    route = module_update_router.ModuleUpdateRouter().get_module_route("insights-core")
    return route


def _update_egg(*, route: module_update_router.Route, force: bool = False) -> bool:
    """Update the egg binary.

    :returns bool: `True` if the egg was updated, `False` otherwise.
    """
    etag: Optional[str] = None
    if os.path.exists(EGG_ETAG_PATH):
        with open(EGG_ETAG_PATH, "r") as f:
            etag = f.read()

    logger.debug("Fetching the egg.")
    resp_egg: http.client.HTTPResponse = insights.Insights().get_egg(route=route, etag=etag)

    new_etag: str = resp_egg.headers.get("Etag")
    if resp_egg.status == 304 or etag == new_etag:
        logger.info("Local egg is already up to date.")
        if not force:
            return False
        logger.debug("Force downloading the egg anyway.")

    logger.debug(f"Updating egg etag {EGG_ETAG_PATH!s}: {etag} -> {new_etag}.")
    with EGG_ETAG_PATH.open("w") as f:
        f.write(new_etag)

    egg: bytes = resp_egg.read()
    logger.debug(f"Saving the egg into {UNTRUSTED_EGG_PATH!s} (size is {len(egg)} bytes).")
    with UNTRUSTED_EGG_PATH.open("wb") as f:
        f.write(egg)

    return True


def _update_egg_signature(*, route: module_update_router.Route):
    """Update the egg binary signature."""
    logger.debug("Fetching the egg signature.")
    resp_sig: http.client.HTTPResponse = insights.Insights().get_egg_signature(route=route)
    signature: bytes = resp_sig.read()

    logger.debug(
        f"Saving the egg signature into {UNTRUSTED_SIG_PATH!s} (size is {len(signature)} bytes)."
    )
    with UNTRUSTED_SIG_PATH.open("wb") as f:
        f.write(signature)


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


def _verify_egg_signature(egg: pathlib.Path, signature: pathlib.Path) -> bool:
    """Verify the GPG signature of an egg.

    :returns bool: `True` if the signature matches.
    """
    home = tempfile.mkdtemp(dir=TEMPORARY_GPG_HOME_PARENT_DIRECTORY)

    import_process = subprocess.run(
        ["/usr/bin/gpg", "--homedir", home, "--import", GPG_KEY_PATH],
        capture_output=True,
        text=True,
    )
    if import_process.returncode != 0:
        _remove_gpg_home(home)
        return False

    verify_process = subprocess.run(
        ["/usr/bin/gpg", "--homedir", home, "--verify", f"{signature!s}", f"{egg!s}"],
        capture_output=True,
        text=True,
    )
    if verify_process.returncode != 0:
        _remove_gpg_home(home)
        return False

    return True


def update():
    """Update the egg to a new release."""
    # TODO Allow force redownload of the egg
    # TODO Allow to skip the GPG verification
    logger.info("Updating the Egg.")
    # 1. Fetch the egg and signature into untrusted
    # 2. Verify the signature
    # 3. Move it to place

    route: module_update_router.Route = _get_route()

    updated: bool = _update_egg(route=route)
    if updated:
        _update_egg_signature(route=route)

    ok: bool = _verify_egg_signature(UNTRUSTED_EGG_PATH, UNTRUSTED_SIG_PATH)
    if not ok:
        # TODO Delete the files
        pass
        return

    logger.debug("Moving the verified egg in place.")
    shutil.move(UNTRUSTED_EGG_PATH, TRUSTED_EGG_PATH)
    shutil.move(UNTRUSTED_SIG_PATH, TRUSTED_SIG_PATH)
