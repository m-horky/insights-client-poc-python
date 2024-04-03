import argparse
import json
import sys
from typing import Self, Optional

from insights_nest.api import inventory
from insights_nest._cmd import abstract
from insights_nest._core import system


class IdentityCommand(abstract.AbstractCommand):
    NAME = "identity"
    HELP = "display host identity"

    commands: dict[str, abstract.AbstractCommand] = {}
    parser = None

    @classmethod
    def create(cls, root_parser) -> Self:
        cls.commands = {}

        cls.parser = root_parser.add_parser(cls.NAME, help=cls.HELP)
        subparsers = cls.parser.add_subparsers(dest="subcommand")
        for subcommand in [
            IdentityShowCommand,
            DisplayNameCommand,
            AnsibleNameCommand,
        ]:
            cls.commands[subcommand.NAME] = subcommand.create(subparsers)
        return cls()

    def run(self, args: argparse.Namespace) -> None:
        if args.subcommand is None:
            type(self).parser.print_help()  # type: ignore
            sys.exit(0)

        if args.subcommand not in type(self).commands.keys():
            print(f"Unknown command: {args.subcommand}")
            sys.exit(1)

        type(self).commands[args.subcommand].run(args)


class IdentityShowCommand(abstract.AbstractCommand):
    NAME = "show"
    HELP = "display host identity"

    @classmethod
    def create(cls, identity_parser) -> Self:
        parser = identity_parser.add_parser(cls.NAME, help=cls.HELP)
        parser.add_argument(abstract.FORMAT_FLAG, **abstract.FORMAT_FLAG_ARGS)
        return cls()

    def run(self, args: argparse.Namespace) -> None:
        host: Optional[inventory.Host] = system.get_inventory_entry()
        if host is None:
            print("This host is not registered.")
            sys.exit(0)

        # --format json
        if args.format == "json":
            data = {
                "insights_id": getattr(host, "id", None),
                "insights_client_id": getattr(host, "insights_id", None),
                "subscription_manager_id": getattr(host, "subscription_manager_id", None),
                "fqdn": getattr(host, "fqdn", None),
                "display_name": getattr(host, "display_name", None),
                "ansible_name": getattr(host, "ansible_host", None),
            }
            print(json.dumps(data))
            sys.exit(0)

        # --format human
        print(f"Insights UUID:                {host.id or 'unknown'}")
        print(f"Insights Client UUID:         {host.insights_id or 'unknown'}")
        print(f"Subscription Management UUID: {host.subscription_manager_id or 'unknown'}")
        if host.fqdn:
            print(f"FQDN:                         {host.fqdn}")
        if host.display_name:
            print(f"Display name:                 {host.display_name}")
        if host.ansible_host:
            print(f"Ansible name:                 {host.ansible_host}")


class DisplayNameCommand(abstract.AbstractCommand):
    NAME = "display-name"
    HELP = "manage display name"

    @classmethod
    def create(cls, identity_parser) -> Self:
        parser = identity_parser.add_parser(cls.NAME, help=cls.HELP)
        action = parser.add_mutually_exclusive_group(required=True)
        action.add_argument("--set", help="set display name")
        # --unset is not supported by Inventory.
        return cls()

    def run(self, args: argparse.Namespace) -> None:
        host: Optional[inventory.Host] = system.get_inventory_entry()
        if host is None:
            print("This host is not registered.")
            sys.exit(0)

        if args.set is not None:
            inventory.Inventory().update_host(host.id, display_name=args.set)
            sys.exit(0)

        raise RuntimeError(f"Impossible arguments: {args}")


class AnsibleNameCommand(abstract.AbstractCommand):
    NAME = "ansible-name"
    HELP = "manage Ansible name"

    @classmethod
    def create(cls, identity_parser) -> Self:
        parser = identity_parser.add_parser(cls.NAME, help=cls.HELP)
        action = parser.add_mutually_exclusive_group(required=True)
        action.add_argument("--set", help="set Ansible name")
        action.add_argument("--unset", help="reset Ansible name", action="store_true")
        return cls()

    def run(self, args: argparse.Namespace) -> None:
        host: Optional[inventory.Host] = system.get_inventory_entry()
        if host is None:
            print("This host is not registered.")
            sys.exit(0)

        if args.unset is True:
            inventory.Inventory().update_host(host.id, ansible_name="")
            sys.exit(0)

        if args.set is not None:
            inventory.Inventory().update_host(host.id, ansible_name=args.set)
            sys.exit(0)

        raise RuntimeError(f"Impossible arguments: {args}")
