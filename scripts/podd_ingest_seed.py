#!/usr/bin/env python3
"""podd_ingest_seed.py — W10 Task 1 (Pod D / Hisham)

One-row DB seed for the ingestion runner's local user, reusing B8's proven
seed mechanics (async engine + app models) with ONE deliberate difference:
keycloak_issuer must be the REAL staging issuer, because the runner
authenticates through the real HTTP API with real Keycloak tokens
(B8 used a synthetic issuer and never touched the API).

Run INSIDE the worker container (app import context), e.g.:
  docker exec -e PYTHONPATH=<appdir> staging-celery-worker \
      python /tmp/podd_ingest_seed.py --sub <uuid>

Idempotent: same (issuer, sub) again -> prints existing user, exit 0.
Conflicting email under a different identity -> hard fail with guidance.
"""
import argparse
import asyncio
import json
import sys

SEED_ISSUER_DEFAULT = "https://keycloak-staging.duckdns.org/realms/openlearn"


def out(step, **kw):
    print("PODD|" + json.dumps(
        {"step": step, **kw}, separators=(",", ":"), default=str, ensure_ascii=False
    ), flush=True)


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sub", required=True,
                    help="keycloak_subject (= Keycloak user uuid from bootstrap)")
    ap.add_argument("--issuer", default=SEED_ISSUER_DEFAULT)
    ap.add_argument("--email", default="pod-d-runner@staging.local")
    args = ap.parse_args()

    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import (
        AsyncSession, async_sessionmaker, create_async_engine,
    )
    from app.config import settings
    from app.models.user import User

    engine = create_async_engine(settings.database_url)
    maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    try:
        async with maker() as session:
            existing = (
                await session.execute(
                    select(User).where(
                        User.keycloak_issuer == args.issuer,
                        User.keycloak_subject == args.sub,
                    )
                )
            ).scalar_one_or_none()
            if existing is not None:
                out("already_seeded", user_id=str(existing.id),
                    sub=args.sub, email=existing.email)
                return 0

            clash = (
                await session.execute(
                    select(User).where(User.email == args.email)
                )
            ).scalar_one_or_none()
            if clash is not None:
                out("email_conflict", email=args.email,
                    existing_sub=clash.keycloak_subject,
                    existing_issuer=clash.keycloak_issuer)
                print(">>> FAIL: email already used by a different identity; "
                      "pick another --email or clean up that row.", file=sys.stderr)
                return 1

            user = User(
                keycloak_issuer=args.issuer,
                keycloak_subject=args.sub,
                email=args.email,
                email_verified=True,
                settings={},
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            out("seeded", user_id=str(user.id), sub=args.sub,
                issuer=args.issuer, email=args.email)
            return 0
    finally:
        await engine.dispose()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
