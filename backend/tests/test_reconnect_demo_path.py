from types import SimpleNamespace

import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.session import Base
from app.api.v1.scan import confirm_scan_bin
from app.models.scan import Scan, WasteClass
from app.schemas.scan import ScanConfirmationRequest
from app.models.twin import NodeType, TwinEdge, TwinNode
from app.models.user import User
from app.services.advisor.advisor import derive_advisor_context
from app.services.twin.events import ingest_scan_event
from app.services.twin.graph import seed_twin
from app.services.twin.metrics import compute_current_metrics


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(
            lambda sync_connection: Base.metadata.create_all(
                sync_connection,
                tables=[User.__table__, Scan.__table__, TwinNode.__table__, TwinEdge.__table__],
            )
        )

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_confirmed_scans_update_twin_and_persisted_metrics(db_session):
    source = TwinNode(id=1, type=NodeType.SOURCE, name="Canteen", config_json={})
    recyclable_bin = TwinNode(
        id=10,
        type=NodeType.BIN,
        name="Recyclable Bin",
        config_json={"capacity": 10},
    )
    residual_bin = TwinNode(
        id=14,
        type=NodeType.BIN,
        name="Residual Bin",
        config_json={"capacity": 10},
    )
    scans = [
        Scan(
            predicted_class=WasteClass.RECYCLABLE,
            subtype="plastic",
            confidence=0.9,
            top3="[]",
            source_node_id=1,
            confirmed_bin=None,
            latency_ms=10,
        ),
        Scan(
            predicted_class=WasteClass.BIODEGRADABLE,
            subtype="organic",
            confidence=0.8,
            top3="[]",
            source_node_id=1,
            confirmed_bin="recyclable",
            latency_ms=10,
        ),
        Scan(
            predicted_class=WasteClass.RESIDUAL,
            subtype="mixed",
            confidence=0.8,
            top3="[]",
            source_node_id=1,
            confirmed_bin="residual",
            latency_ms=10,
        ),
        Scan(
            predicted_class=WasteClass.RESIDUAL,
            subtype="mixed",
            confidence=0.8,
            top3="[]",
            source_node_id=1,
            latency_ms=10,
        ),
    ]
    db_session.add_all([source, recyclable_bin, residual_bin, *scans])
    await db_session.commit()

    response = await confirm_scan_bin(
        str(scans[0].id),
        ScanConfirmationRequest(confirmed_bin="recyclable"),
        db_session,
        {"demo": True},
    )
    assert response.confirmed_bin == "recyclable"
    with pytest.raises(HTTPException) as duplicate_confirmation:
        await confirm_scan_bin(
            str(scans[0].id),
            ScanConfirmationRequest(confirmed_bin="recyclable"),
            db_session,
            {"demo": True},
        )
    assert getattr(duplicate_confirmation.value, "status_code", None) == 409

    for scan in scans[1:3]:
        await ingest_scan_event(db_session, scan, scan.confirmed_bin)

    metrics = await compute_current_metrics(db_session)
    await db_session.refresh(source)
    await db_session.refresh(recyclable_bin)
    edge = await db_session.get(TwinEdge, 1)

    assert source.config_json["counts"] == {"recyclable": 1, "biodegradable": 1, "residual": 1}
    assert recyclable_bin.config_json["counts"] == {"recyclable": 1, "biodegradable": 1}
    assert edge is not None
    assert edge.from_id == 1 and edge.to_id == 10 and edge.weight == 2
    assert metrics.total_items == 4
    assert metrics.recovered_items == 2
    assert metrics.diversion_rate == 0.5
    assert metrics.contamination_rate == 0.5
    assert metrics.co2e_avoided_kg == 0.48
    assert metrics.pickup_cost == 200


@pytest.mark.asyncio
async def test_twin_seed_is_idempotent_with_multiple_existing_nodes(db_session):
    await seed_twin(db_session)
    first_count = await db_session.scalar(select(func.count()).select_from(TwinNode))

    await seed_twin(db_session)
    second_count = await db_session.scalar(select(func.count()).select_from(TwinNode))

    assert first_count > 1
    assert second_count == first_count


def test_advisor_context_uses_observed_misroutes_only():
    scans = [
        SimpleNamespace(
            predicted_class=WasteClass.BIODEGRADABLE,
            confirmed_bin="recyclable",
            source_node_id=3,
        ),
        SimpleNamespace(
            predicted_class=WasteClass.RECYCLABLE,
            confirmed_bin="recyclable",
            source_node_id=3,
        ),
        SimpleNamespace(
            predicted_class=WasteClass.HAZARDOUS,
            confirmed_bin=None,
            source_node_id=3,
        ),
    ]
    nodes = [SimpleNamespace(id=3, name="Canteen")]

    causes, hotspots = derive_advisor_context(scans, nodes)

    assert causes == [{
        "pair": "biodegradable->recyclable",
        "count": 1,
        "description": "1 biodegradable item(s) were confirmed in the recyclable bin",
    }]
    assert hotspots == [{
        "node": "Canteen",
        "issue": "1 confirmed scan(s) were placed in a different bin than predicted",
        "severity": "low",
    }]
