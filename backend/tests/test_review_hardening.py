"""Tests for the Week 9 backend-review fixes (reaper, course cleanup, metrics,
docs, CORS, token audience, pool settings)."""

import asyncio
import json
import os
import subprocess
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text, update

from app.config import settings
from app.db.session import engine
from app.main import app
from app.models.course import Course
from app.models.material import (
    FAILED_STATUS,
    PENDING_STATUS,
    PROCESSING_STATUS,
    READY_STATUS,
    Material,
)
from app.services import course_service, material_service, storage
from app.services.auth import oidc
from app.workers import celery_app
from app.workers.tasks import maintenance_tasks
from conftest import _create_material, _create_user
from test_oidc import _build_token

BACKEND_DIR = Path(__file__).resolve().parents[1]


async def _create_course(db, owner) -> Course:
    course = Course(owner_id=owner.id, title="Cleanup course", description="x")
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


async def _age(db, material: Material, minutes: int) -> None:
    await db.execute(
        update(Material)
        .where(Material.id == material.id)
        .values(updated_at=datetime.now(UTC) - timedelta(minutes=minutes))
    )
    await db.commit()


# --- stuck-material reaper (B-07 / P-05) ------------------------------------


@pytest.mark.asyncio
async def test_fail_stuck_materials_only_moves_old_active_rows(db_session):
    owner = await _create_user(db_session, "reaper-owner", "reaper-owner@example.com")
    course = await _create_course(db_session, owner)
    old_pending = await _create_material(db_session, course, owner, status=PENDING_STATUS)
    old_processing = await _create_material(
        db_session, course, owner, status=PROCESSING_STATUS
    )
    old_ready = await _create_material(db_session, course, owner, status=READY_STATUS)
    fresh_pending = await _create_material(db_session, course, owner, status=PENDING_STATUS)
    for material in (old_pending, old_processing, old_ready):
        await _age(db_session, material, minutes=120)

    stuck = await material_service.fail_stuck_materials(
        db_session, timedelta(minutes=30)
    )

    assert set(stuck) == {old_pending.id, old_processing.id}
    for material, expected in (
        (old_pending, FAILED_STATUS),
        (old_processing, FAILED_STATUS),
        (old_ready, READY_STATUS),
        (fresh_pending, PENDING_STATUS),
    ):
        await db_session.refresh(material)
        assert material.status == expected

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_material_updated_at_moves_on_status_change(db_session):
    owner = await _create_user(db_session, "touch-owner", "touch-owner@example.com")
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    before = material.updated_at

    await asyncio.sleep(0.01)
    material.status = PROCESSING_STATUS
    await db_session.commit()
    await db_session.refresh(material)

    assert material.updated_at > before

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_reap_stuck_materials_task_marks_failed(db_session):
    owner = await _create_user(db_session, "reaper-task-owner", "reaper-task@example.com")
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner, status=PROCESSING_STATUS)
    await _age(db_session, material, minutes=settings.material_stuck_timeout_minutes + 5)

    # The task owns its event loop and engine, like a real worker process.
    count = await asyncio.to_thread(maintenance_tasks.reap_stuck_materials.run)

    assert count >= 1
    await db_session.refresh(material)
    assert material.status == FAILED_STATUS

    await db_session.delete(owner)
    await db_session.commit()


def test_reaper_is_scheduled_by_celery_beat():
    entry = celery_app.celery_app.conf.beat_schedule["reap-stuck-materials"]
    assert entry["task"] == maintenance_tasks.reap_stuck_materials.name
    assert (
        maintenance_tasks.reap_stuck_materials.name
        in celery_app.celery_app.tasks
    )


# --- course deletion cleans up storage and vectors (B-06) -------------------


async def _insert_vector(db, material_id: uuid.UUID) -> None:
    vector = "[" + ",".join(["0.1"] * 1024) + "]"
    await db.execute(
        text(
            "INSERT INTO vector_records (id, embedding, content, metadata) "
            "VALUES (:id, CAST(:emb AS vector), 'c', CAST(:meta AS jsonb))"
        ),
        {
            "id": f"test-{uuid.uuid4()}",
            "emb": vector,
            "meta": json.dumps({"material_id": str(material_id)}),
        },
    )


async def _vector_count(db, material_id: uuid.UUID) -> int:
    result = await db.execute(
        text("SELECT COUNT(*) FROM vector_records WHERE metadata @> CAST(:m AS jsonb)"),
        {"m": json.dumps({"material_id": str(material_id)})},
    )
    return int(result.scalar_one())


@pytest.mark.asyncio
async def test_delete_course_removes_vectors_and_stored_files(db_session, monkeypatch):
    owner = await _create_user(db_session, "delete-owner", "delete-owner@example.com")
    course = await _create_course(db_session, owner)
    other_course = await _create_course(db_session, owner)
    first = await _create_material(db_session, course, owner)
    second = await _create_material(db_session, course, owner)
    untouched = await _create_material(db_session, other_course, owner)
    for material in (first, second, untouched):
        await _insert_vector(db_session, material.id)
    await db_session.commit()

    deleted: list[list[str]] = []
    monkeypatch.setattr(
        storage, "delete_material_objects", lambda keys: deleted.append(keys) or []
    )

    await course_service.delete_course(db_session, course)

    assert len(deleted) == 1
    assert set(deleted[0]) == {first.s3_key, second.s3_key}
    assert await _vector_count(db_session, first.id) == 0
    assert await _vector_count(db_session, second.id) == 0
    assert await _vector_count(db_session, untouched.id) == 1

    await db_session.execute(
        text("DELETE FROM vector_records WHERE metadata @> CAST(:m AS jsonb)"),
        {"m": json.dumps({"material_id": str(untouched.id)})},
    )
    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_delete_course_succeeds_when_storage_cleanup_fails(db_session, monkeypatch):
    owner = await _create_user(db_session, "delete-fail-owner", "delete-fail@example.com")
    course = await _create_course(db_session, owner)
    course_id = course.id
    await _create_material(db_session, course, owner)

    def boom(keys):
        raise RuntimeError("storage down")

    monkeypatch.setattr(storage, "delete_material_objects", boom)

    await course_service.delete_course(db_session, course)

    assert await db_session.get(Course, course_id) is None

    await db_session.delete(owner)
    await db_session.commit()


# --- /metrics, docs, CORS (B-03 / B-11) -------------------------------------


def test_metrics_open_outside_production_without_token(monkeypatch):
    monkeypatch.setattr(settings, "metrics_token", "")
    monkeypatch.setattr(settings, "environment", "development")

    response = TestClient(app).get("/metrics")

    assert response.status_code == 200
    assert "http_requests" in response.text or "python_info" in response.text


def test_metrics_hidden_in_production_without_token(monkeypatch):
    monkeypatch.setattr(settings, "metrics_token", "")
    monkeypatch.setattr(settings, "environment", "production")

    assert TestClient(app).get("/metrics").status_code == 404


@pytest.mark.parametrize("environment", ["development", "production"])
def test_metrics_requires_bearer_token_when_configured(monkeypatch, environment):
    monkeypatch.setattr(settings, "metrics_token", "s3cret-metrics")
    monkeypatch.setattr(settings, "environment", environment)
    client = TestClient(app)

    assert client.get("/metrics").status_code == 401
    assert (
        client.get("/metrics", headers={"Authorization": "Bearer wrong"}).status_code
        == 401
    )
    ok = client.get("/metrics", headers={"Authorization": "Bearer s3cret-metrics"})
    assert ok.status_code == 200


def test_docs_and_openapi_are_disabled_in_production():
    code = (
        "from app.main import app; "
        "print(app.docs_url, app.redoc_url, app.openapi_url)"
    )
    env = {**os.environ, "ENVIRONMENT": "production"}
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().splitlines()[-1] == "None None None"


def test_cors_does_not_allow_credentials_and_limits_methods():
    response = TestClient(app).options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "PATCH",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )

    assert response.status_code == 200
    assert "access-control-allow-credentials" not in response.headers
    allowed = response.headers["access-control-allow-methods"]
    assert "PATCH" in allowed
    assert "TRACE" not in allowed and "HEAD" not in allowed


# --- token client check (B-14) and pool (B-18) ------------------------------


def test_token_for_other_client_is_rejected(fake_jwks, rsa_keypair):
    private_key, _ = rsa_keypair

    with pytest.raises(ValueError, match="different client"):
        oidc.decode_access_token(_build_token(private_key, extra={"azp": "other-app"}))


def test_token_for_this_client_is_accepted(fake_jwks, rsa_keypair):
    private_key, _ = rsa_keypair

    claims = oidc.decode_access_token(
        _build_token(private_key, extra={"azp": settings.keycloak_client_id})
    )

    assert claims["azp"] == settings.keycloak_client_id


def test_database_pool_checks_connections_before_use():
    assert engine.pool._pre_ping is True
