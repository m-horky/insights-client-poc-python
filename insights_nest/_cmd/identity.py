import argparse
import json
import sys
from typing import Self

from insights_nest._cmd import abstract
from insights_nest._shell import system


class IdentityCommand(abstract.AbstractCommand):
    NAME = "identity"
    HELP = "display host identity"

    @classmethod
    def create(cls, subparsers) -> Self:
        parser = subparsers.add_parser(cls.NAME, help=cls.HELP)
        parser.add_argument(abstract.FORMAT_FLAG, **abstract.FORMAT_FLAG_ARGS)
        return cls()

    def run(self, args: argparse.Namespace) -> None:
        host = system.get_inventory_entry()

        # --format json
        if args.format == "json":
            data = {
                "insights_id": getattr(host, "id", None),
                "insights_client_id": getattr(host, "insights_id", None),
                "subscription_manager_id": getattr(host, "subscription_manager_id", None),
            }
            print(json.dumps(data))
            sys.exit(0)

        # --format human
        if host is None:
            print("This host is not registered.")
            sys.exit(0)

        print(f"Insights UUID:                {host.id or 'unknown'}")
        print(f"Insights Client UUID:         {host.insights_id or 'unknown'}")
        print(f"Subscription Management UUID: {host.subscription_manager_id or 'unknown'}")
