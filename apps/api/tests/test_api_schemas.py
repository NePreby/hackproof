import json
from datetime import UTC, datetime

import jsonschema

from hackproof.config import ROOT
from hackproof.export.api_schemas import (
    API_MODELS,
    build_index,
    export_api_schemas,
    find_export_schema_versions,
)
from hackproof.github.models import DependencyFingerprint
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


def test_index_lists_existing_export_schema_versions():
    versions = find_export_schema_versions(SCHEMA_DIR)
    assert "1.0" in versions
    assert "1.1" in versions
    assert "1.2" in versions

    index = build_index(SCHEMA_DIR)
    assert index["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert index["$id"] == "https://hackproof.vercel.app/schema/index.json"

    export_versions = [s["version"] for s in index["export_schemas"]]
    assert export_versions == versions

    # Ensure every referenced export schema exists
    for s in index["export_schemas"]:
        json_file = SCHEMA_DIR / f"{s['name']}-{s['version']}.json"
        yaml_file = SCHEMA_DIR / f"{s['name']}-{s['version']}.yml"
        assert json_file.exists(), f"Missing export schema file: {json_file}"
        assert yaml_file.exists(), f"Missing export yaml file: {yaml_file}"


def test_api_schemas_generation_and_index():
    written = export_api_schemas(SCHEMA_DIR)
    assert len(written) == len(API_MODELS) + 1  # all model schemas + index.json

    index_file = SCHEMA_DIR / "index.json"
    assert index_file.exists()
    index_data = json.loads(index_file.read_text(encoding="utf-8"))

    api_names = {item["name"] for item in index_data["api_schemas"]}
    assert api_names == set(API_MODELS.keys())


def test_validate_sample_responses_against_schemas():
    now = datetime.now(UTC)

    sample_instances = {
        "stats": Stats(
            projects=10,
            verified_projects=5,
            likely_projects=3,
            possible_projects=2,
            unattributed_accounts=1,
            contracts=15,
            builders=8,
            contributors=12,
            countries=4,
            wasm_uploads=7,
            failed_txs=2,
        ),
        "project": Project(
            project_id="repo:owner/sample",
            full_name="owner/sample",
            url="https://github.com/owner/sample",
            footprint="contracts",
            tier="verified",
            contracts=2,
            classic_ops=0,
            assets=0,
            builders=1,
            wasm_uploads=1,
            failed_txs=0,
            first_activity=now,
            last_activity=now,
            description="Sample project",
            homepage="https://sample.com",
            stars=10,
            forks=2,
            language="Rust",
            license="MIT",
            owner="owner",
            owner_avatar="https://avatars.githubusercontent.com/u/1",
            country="VN",
            dependencies=DependencyFingerprint(packages=["@stellar/stellar-sdk"]),
            window_commits=5,
            total_commits=10,
            stellar_added_in_window=True,
            created_at=now,
            topics=["stellar", "defi"],
            track="genesis",
            integrations=["privy"],
            award=None,
        ),
        "contributor": Contributor(
            login="nepreby",
            url="https://github.com/nepreby",
            avatar_url="https://avatars.githubusercontent.com/u/nepreby",
            contributions=42,
            country="VN",
        ),
        "link": Link(
            subject_kind="contract",
            subject="CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            method="contract_in_repo",
            path="contracts/hello/src/lib.rs",
        ),
        "contract": Contract(
            contract_id="CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            deployer="GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            wasm_hash="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            tx_hash="fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210",
            ledger=123456,
            deployed_at=now,
            project_id="repo:owner/sample",
        ),
        "wasm-upload": WasmUpload(
            wasm_hash="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            uploader="GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            tx_hash="fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210",
            size=1024,
            source_repo="owner/sample",
            full_name="owner/sample",
            contracts=1,
            uploaded_at=now,
        ),
        "failed-tx": FailedTx(
            tx_hash="fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210",
            source_account="GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            kind="invoke_host_function",
            result_code="tx_failed",
            ledger=123456,
            created_at=now,
        ),
        "integration-use": IntegrationUse(
            slug="privy",
            name="Privy",
            method="package",
            evidence="@privy-io/node",
            path="package.json",
        ),
        "project-detail": ProjectDetail(
            project=Project(
                project_id="repo:owner/sample",
                full_name="owner/sample",
                url="https://github.com/owner/sample",
                footprint="contracts",
                tier="verified",
                contracts=1,
                classic_ops=0,
                assets=0,
                builders=1,
                wasm_uploads=1,
                failed_txs=0,
                first_activity=now,
                last_activity=now,
                description="Sample project",
                homepage="https://sample.com",
                stars=10,
                forks=2,
                language="Rust",
                license="MIT",
                owner="owner",
                owner_avatar="https://avatars.githubusercontent.com/u/1",
                country="VN",
                dependencies=None,
                window_commits=5,
                total_commits=10,
                stellar_added_in_window=True,
                created_at=now,
                topics=[],
                track="genesis",
                integrations=[],
                award=None,
            ),
            links=[],
            integration_uses=[],
            contributors=[],
            contracts=[],
            wasm_uploads=[],
            failed_txs=[],
        ),
        "builder": Builder(
            address="GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            projects=[],
            contracts=[],
            wasm_uploads=[],
            failed_txs=[],
        ),
        "timeline-point": TimelinePoint(
            hour=now,
            contracts=5,
        ),
        "integration": Integration(
            slug="privy",
            name="Privy",
            category="Auth",
            site="https://privy.io",
            projects=3,
        ),
        "country-count": CountryCount(
            country="VN",
            contributors=8,
        ),
    }

    for name, instance in sample_instances.items():
        schema_file = SCHEMA_DIR / f"{name}.schema.json"
        assert schema_file.exists(), f"Schema file {schema_file} does not exist"

        schema = json.loads(schema_file.read_text(encoding="utf-8"))
        data = json.loads(instance.model_dump_json())

        # Validate sample payload against schema using jsonschema validator
        jsonschema.validate(instance=data, schema=schema)
