"""Endpoint-level tests for the retrieval search route.

HTTP, routing, dependency resolution, authentication and course
authorization run through the real application on the shared dev database
(same harness as ``test_material_api.py``: fake JWKS + overridden DB
session). Only the external AI boundary is stubbed — the embedding provider
and the session-bound vector store — because "HTTP real / providers fake" is
exactly what these tests must verify. A spy records the order of
ownership-check vs. embedding vs. vector-search so the
authorization-before-inference guarantee is asserted, not assumed.

Cleanup deletes the created users; every other row (courses, materials,
pages) is removed by the models' DB-level ``ON DELETE CASCADE`` foreign keys
(``app/models/material.py``), which avoids double-deleting cascaded rows.
"""

import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.api import retrieval as retrieval_api
from app.config import settings
from app.db.session import get_db
from app.main import app
from app.models.user import User
from app.pal.models.types import VectorSearchResult
from app.pal.providers.embedding.mock_provider import MockEmbeddingProvider
from app.services import retrieval_service as rs
from conftest import _create_material, _create_user

ISSUER = settings.keycloak_issuer
AUDIENCE = settings.keycloak_audience


def _build_token(private_key: str, *, sub: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "iss": ISSUER,
        "aud": AUDIENCE,
        "iat": now,
        "exp": now + timedelta(minutes=15),
        "email": "user@openlearn.dev",
        "realm_access": {"roles": ["instructor"]},
    }
    return jwt.encode(payload, private_key, algorithm="RS256")


async def _create_course(db, owner):
    from app.models.course import Course

    course = Course(owner_id=owner.id, title="Retrieval Course", description="test")
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


@asynccontextmanager
async def _api(db_session, token: str | None = None):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            yield client, headers
    finally:
        app.dependency_overrides.clear()


async def _cleanup(db, *users):
    """Delete created users; FK cascades remove their courses/materials."""
    ids = [user.id for user in users]
    if ids:
        await db.execute(delete(User).where(User.id.in_(ids)))
        await db.commit()
        db.expunge_all()


class _ProviderSpy:
    """Stub the external embedding/vector boundary; record the call order."""

    def __init__(self):
        self.events = []
        self.results_by_material: dict[str, list[VectorSearchResult]] = {}

    def candidate(
        self,
        material_id,
        chunk_id: str = "doc:0",
        score: float = 0.5,
        content: str = "chunk text",
    ) -> VectorSearchResult:
        mid = str(material_id)
        return VectorSearchResult(
            id=f"{mid}:{chunk_id}",
            score=score,
            content=content,
            metadata={
                "material_id": mid,
                "document_id": f"{mid}-doc",
                "chunk_id": chunk_id,
                "pages": [1],
            },
        )

    def install(self, monkeypatch) -> "_ProviderSpy":
        spy = self

        class _StubVectorDB:
            provider_name = "stub"

            async def search(self, vector, *, top_k=5, filters=None):
                assert filters is not None and "material_id" in filters
                mid = filters["material_id"]
                spy.events.append(("vector_search", mid))
                hits = sorted(
                    spy.results_by_material.get(mid, []),
                    key=lambda candidate: (-candidate.score, candidate.id),
                )
                return hits[:top_k]

        def embedding_factory():
            spy.events.append("embed")
            return MockEmbeddingProvider(dimension=1024)

        def vector_factory(provider=None, session=None):
            spy.events.append("construct_vector_db")
            return _StubVectorDB()

        # Keep the real authorization logic: wrap (not replace) the same
        # ``require_owned_course`` the handler uses, recording its success.
        real_require_owned_course = retrieval_api.require_owned_course

        async def recording_owned(db, course_id, user):
            course = await real_require_owned_course(db, course_id, user)
            spy.events.append("owned")
            return course

        monkeypatch.setattr(rs, "_get_embedding_provider", embedding_factory)
        monkeypatch.setattr(rs, "get_vector_db_provider", vector_factory)
        monkeypatch.setattr(retrieval_api, "require_owned_course", recording_owned)
        return self


@pytest.fixture
def provider_spy(monkeypatch) -> _ProviderSpy:
    return _ProviderSpy().install(monkeypatch)


@pytest.mark.asyncio
async def test_owner_can_search_own_course(db_session, rsa_keypair, fake_jwks, provider_spy):
    private_key, _ = rsa_keypair
    users = []
    try:
        instructor = await _create_user(
            db_session, "retrieval-owner-subject", "retrieval-owner@example.com"
        )
        users.append(instructor)
        course = await _create_course(db_session, instructor)
        material = await _create_material(db_session, course, instructor)
        mid = str(material.id)
        provider_spy.results_by_material[mid] = [provider_spy.candidate(mid)]
        token = _build_token(private_key, sub=instructor.keycloak_subject)

        async with _api(db_session, token) as (client, headers):
            response = await client.post(
                f"/v1/courses/{course.id}/materials/search",
                json={"query": "winds of change", "top_k": 5},
                headers=headers,
            )
        body = response.json()
    finally:
        await _cleanup(db_session, *users)

    assert response.status_code == 200
    assert body["course_id"] == str(course.id)
    assert body["results"] == [
        {
            "material_id": mid,
            "chunk_id": "doc:0",
            "content": "chunk text",
            "pages": [1],
            "score": 0.5,
        }
    ]
    # Ownership resolved before embedding, embedding before the per-material
    # vector search, and the filter is the server-side material id.
    assert provider_spy.events == [
        "owned",
        "embed",
        "construct_vector_db",
        ("vector_search", mid),
    ]


@pytest.mark.asyncio
async def test_non_owner_cannot_search(db_session, rsa_keypair, fake_jwks, provider_spy):
    private_key, _ = rsa_keypair
    users = []
    try:
        owner = await _create_user(
            db_session, "retrieval-nonowner-owner-subject", "retrieval-nonowner-owner@example.com"
        )
        intruder = await _create_user(
            db_session, "retrieval-nonowner-intruder-subject", "retrieval-nonowner-intruder@example.com"
        )
        users.extend([owner, intruder])
        course = await _create_course(db_session, owner)
        token = _build_token(private_key, sub=intruder.keycloak_subject)

        async with _api(db_session, token) as (client, headers):
            response = await client.post(
                f"/v1/courses/{course.id}/materials/search",
                json={"query": "anything at all"},
                headers=headers,
            )
    finally:
        await _cleanup(db_session, *users)

    assert response.status_code == 403
    # Authorization ran first: no embedding, no vector provider, ever.
    assert provider_spy.events == []


@pytest.mark.asyncio
async def test_missing_course_returns_404(db_session, rsa_keypair, fake_jwks, provider_spy):
    private_key, _ = rsa_keypair
    users = []
    try:
        instructor = await _create_user(
            db_session, "retrieval-missing-course-subject", "retrieval-missing-course@example.com"
        )
        users.append(instructor)
        token = _build_token(private_key, sub=instructor.keycloak_subject)

        async with _api(db_session, token) as (client, headers):
            response = await client.post(
                f"/v1/courses/{uuid.uuid4()}/materials/search",
                json={"query": "anything at all"},
                headers=headers,
            )
    finally:
        await _cleanup(db_session, *users)

    assert response.status_code == 404
    assert provider_spy.events == []


@pytest.mark.asyncio
async def test_unauthenticated_search_returns_401_and_never_embeds(
    db_session, fake_jwks, provider_spy
):
    async with _api(db_session) as (client, _headers):
        response = await client.post(
            f"/v1/courses/{uuid.uuid4()}/materials/search",
            json={"query": "anything at all"},
        )

    assert response.status_code == 401
    assert provider_spy.events == []


@pytest.mark.asyncio
async def test_retrieval_rate_limit_returns_429(
    db_session, rsa_keypair, fake_jwks, provider_spy, monkeypatch
):
    monkeypatch.setattr(settings, "rate_limit_retrieval_per_minute", 1)
    private_key, _ = rsa_keypair
    users = []
    try:
        instructor = await _create_user(
            db_session, "retrieval-ratelimit-subject", "retrieval-ratelimit@example.com"
        )
        users.append(instructor)
        course = await _create_course(db_session, instructor)
        token = _build_token(private_key, sub=instructor.keycloak_subject)

        async with _api(db_session, token) as (client, headers):
            codes = []
            for _ in range(2):
                codes.append(
                    await client.post(
                        f"/v1/courses/{course.id}/materials/search",
                        json={"query": "anything at all"},
                        headers=headers,
                    )
                )
    finally:
        await _cleanup(db_session, *users)

    assert [r.status_code for r in codes] == [200, 429]
    assert int(codes[1].headers["Retry-After"]) >= 1
    # The first request really completed the search (empty course: no
    # materials resolved, so no vector provider is even constructed).
    assert codes[0].json() == {"course_id": str(course.id), "results": []}


@pytest.mark.asyncio
async def test_invalid_query_returns_422_without_embedding(
    db_session, rsa_keypair, fake_jwks, provider_spy
):
    private_key, _ = rsa_keypair
    users = []
    try:
        instructor = await _create_user(
            db_session, "retrieval-invalid-query-subject", "retrieval-invalid-query@example.com"
        )
        users.append(instructor)
        course = await _create_course(db_session, instructor)
        token = _build_token(private_key, sub=instructor.keycloak_subject)

        async with _api(db_session, token) as (client, headers):
            response = await client.post(
                f"/v1/courses/{course.id}/materials/search",
                json={"query": "   "},  # blank after trim
                headers=headers,
            )
    finally:
        await _cleanup(db_session, *users)

    assert response.status_code == 422
    assert provider_spy.events == []  # request validation precedes all work


@pytest.mark.asyncio
async def test_successful_response_exposes_provenance_not_vector_ids(
    db_session, rsa_keypair, fake_jwks, provider_spy
):
    private_key, _ = rsa_keypair
    users = []
    try:
        instructor = await _create_user(
            db_session, "retrieval-no-vector-id-subject", "retrieval-no-vector-id@example.com"
        )
        users.append(instructor)
        course = await _create_course(db_session, instructor)
        material = await _create_material(db_session, course, instructor)
        mid = str(material.id)
        provider_spy.results_by_material[mid] = [provider_spy.candidate(mid, chunk_id="doc:7")]
        token = _build_token(private_key, sub=instructor.keycloak_subject)

        async with _api(db_session, token) as (client, headers):
            response = await client.post(
                f"/v1/courses/{course.id}/materials/search",
                json={"query": "winds of change"},
                headers=headers,
            )
        body = response.json()
    finally:
        await _cleanup(db_session, *users)

    assert response.status_code == 200
    item = body["results"][0]
    # The documented provenance fields only — never the vector id, which
    # embeds material + document internals.
    assert set(item) == {"material_id", "chunk_id", "content", "pages", "score"}
    assert item["chunk_id"] == "doc:7"
    vector_id = f"{mid}:doc:7"
    assert vector_id not in response.text

    # And the real ownership check still ran ahead of every provider call.
    assert provider_spy.events[:2] == ["owned", "embed"]
