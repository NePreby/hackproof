import json
import logging

import yaml

from hackproof.config import ROOT
from hackproof.db import open_pool, pool
from hackproof.export.api_schemas import export_api_schemas
from hackproof.export.build import build_export
from hackproof.export.models import SCHEMA_VERSION
from hackproof.export.render import json_schema, to_json, to_yaml
from hackproof.hackathon import get_hackathon

log = logging.getLogger("hackproof.export")

PUBLIC = ROOT / "apps" / "web" / "public"


def _write(path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


async def run_export() -> None:
    hackathon = get_hackathon()
    await open_pool()
    async with pool().acquire() as connection:
        export = await build_export(connection, hackathon)

    data = PUBLIC / "data" / hackathon.slug
    _write(data / "projects.json", to_json(export))
    _write(data / "projects.yml", to_yaml(export))

    schema = json_schema()
    schemas = PUBLIC / "schema"
    _write(schemas / f"hackathon-export-{SCHEMA_VERSION}.json", json.dumps(schema, indent=2) + "\n")
    _write(
        schemas / f"hackathon-export-{SCHEMA_VERSION}.yml",
        yaml.safe_dump(schema, sort_keys=False, allow_unicode=True, width=100),
    )
    log.info("wrote %s projects to %s", len(export.projects), data)

    schema_files = export_api_schemas()
    log.info("wrote %s API schema files and index.json", len(schema_files))
