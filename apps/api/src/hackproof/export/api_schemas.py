import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from hackproof.config import ROOT
from hackproof.schemas import (
    Builder,
    Contract,
    Contributor,
    CountryCount,
    FailedTx,
    Integration,
    IntegrationUse,
    Link,
    Project,
    ProjectDetail,
    Stats,
    TimelinePoint,
    WasmUpload,
)

SCHEMA_DIR = ROOT / "apps" / "web" / "public" / "schema"
SITE = "https://hackproof.vercel.app"
API_SCHEMA_VERSION = "1.0"

API_MODELS: dict[str, type[BaseModel]] = {
    "stats": Stats,
    "project": Project,
    "project-detail": ProjectDetail,
    "builder": Builder,
    "contract": Contract,
    "contributor": Contributor,
    "country-count": CountryCount,
    "failed-tx": FailedTx,
    "integration": Integration,
    "integration-use": IntegrationUse,
    "link": Link,
    "timeline-point": TimelinePoint,
    "wasm-upload": WasmUpload,
}


def model_schema(
    name: str, model_cls: type[BaseModel], version: str = API_SCHEMA_VERSION
) -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{SITE}/schema/{name}.schema.json",
        "title": model_cls.__name__,
        "version": version,
        **model_cls.model_json_schema(),
    }


def find_export_schema_versions(schema_dir: Path = SCHEMA_DIR) -> list[str]:
    versions = set()
    if schema_dir.exists():
        for file in schema_dir.glob("hackathon-export-*.json"):
            match = re.search(r"hackathon-export-(\d+(?:\.\d+)*)\.json", file.name)
            if match:
                versions.add(match.group(1))
    return sorted(list(versions), key=lambda v: [int(x) for x in v.split(".")])


def build_index(schema_dir: Path = SCHEMA_DIR) -> dict[str, Any]:
    export_versions = find_export_schema_versions(schema_dir)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{SITE}/schema/index.json",
        "description": (
            "Index of published data export schemas and public API response schemas for HackProof"
        ),
        "export_schemas": [
            {
                "name": "hackathon-export",
                "version": v,
                "json": f"{SITE}/schema/hackathon-export-{v}.json",
                "yaml": f"{SITE}/schema/hackathon-export-{v}.yml",
            }
            for v in export_versions
        ],
        "api_schemas": [
            {
                "name": name,
                "model": model_cls.__name__,
                "version": API_SCHEMA_VERSION,
                "schema": f"{SITE}/schema/{name}.schema.json",
            }
            for name, model_cls in sorted(API_MODELS.items())
        ],
    }


def export_api_schemas(schema_dir: Path = SCHEMA_DIR) -> list[Path]:
    schema_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for name, model_cls in API_MODELS.items():
        schema_dict = model_schema(name, model_cls)
        target = schema_dir / f"{name}.schema.json"
        target.write_text(json.dumps(schema_dict, indent=2) + "\n")
        written.append(target)

    index_dict = build_index(schema_dir)
    index_file = schema_dir / "index.json"
    index_file.write_text(json.dumps(index_dict, indent=2) + "\n")
    written.append(index_file)

    return written
