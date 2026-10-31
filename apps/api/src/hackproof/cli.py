import argparse
import asyncio
import logging

from hackproof.export.jobs import run_export
from hackproof.github.jobs import run_discover, run_scan
from hackproof.indexer.sync import run_sync
from hackproof.linking.reconcile import run_reconcile


def main() -> None:
    parser = argparse.ArgumentParser(prog="hackproof")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("sync", help="index the hack window from testnet")
    discover = commands.add_parser("discover", help="find candidate repos on github")
    discover.add_argument(
        "--strings", action="store_true", help="also run the network string code queries"
    )
    scan = commands.add_parser("scan", help="scan discovered repos for chain fingerprints")
    scan.add_argument("--force", action="store_true", help="rescan repos already scanned")
    scan.add_argument(
        "--projects", action="store_true", help="only scan repos that are already projects"
    )
    commands.add_parser("reconcile", help="link chain activity to repos and build projects")
    export_cmd = commands.add_parser("export", help="write the json and yaml export and its schema")
    export_cmd.add_argument(
        "--schemas-only",
        action="store_true",
        help="generate API schemas and index.json without requiring database connection",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    match args.command:
        case "sync":
            asyncio.run(run_sync())
        case "discover":
            asyncio.run(run_discover(args.strings))
        case "scan":
            asyncio.run(run_scan(args.force, args.projects))
        case "reconcile":
            asyncio.run(run_reconcile())
        case "export":
            if getattr(args, "schemas_only", False):
                from hackproof.export.api_schemas import export_api_schemas

                export_api_schemas()
            else:
                asyncio.run(run_export())
