# OpenLearn-AI — Staging Rollback Runbook

## Purpose

This runbook describes the safe rollback procedure for the OpenLearn-AI staging environment.

A rollback deploys a previously known-good immutable application image identified by its Git SHA. It does **not** reset the Git branch or rebuild the application from source.

---

## 1. Before Rollback

### 1.1 Identify the target release

Choose a previously known-good SHA for which both backend and frontend images exist in GHCR.

Example known-good release:

```text
sha-480e93748baa93072d49c8c5a737e3ec1b0a4a08
```

Verify that the target images exist:

```bash
docker manifest inspect ghcr.io/openlearn-ai/openlearn-backend:sha-480e93748baa93072d49c8c5a737e3ec1b0a4a08
docker manifest inspect ghcr.io/openlearn-ai/openlearn-frontend:sha-480e93748baa93072d49c8c5a737e3ec1b0a4a08
```

Both commands must succeed before continuing.

### 1.2 Verify GHCR authentication

If the VPS is not authenticated to GHCR:

```bash
echo "$GHCR_PAT" | docker login ghcr.io -u <github-username> --password-stdin
```

Do not place the token in the repository, compose files, scripts, or this runbook.

### 1.3 Check disk space

```bash
df -h /
docker system df
```

Do **not** use:

```bash
docker system prune -a
docker volume prune
docker compose down -v
docker rmi -f
```

Do not manually delete Docker or containerd storage.

---

## 2. Application Rollback

Run the rollback from the staging repository on the VPS:

```bash
cd ~/OpenLearn-AI
```

Confirm that the VPS contains the deployment script required for the rollback:

```bash
grep -nE 'SKIP_MIGRATIONS|SKIP_DISK_GUARD|IMAGE_TAG' infra/deploy.sh
```

Then deploy the known-good immutable SHA:

```bash
SKIP_MIGRATIONS=1 ./infra/deploy.sh sha-480e93748baa93072d49c8c5a737e3ec1b0a4a08
```

Do not change the Git branch or pull unrelated application changes as part of an incident rollback.

### Why `SKIP_MIGRATIONS=1`?

The rollback command intentionally skips forward database migrations.

The rollback does **not** downgrade the database schema.

This is appropriate when the previous application release is compatible with the current database schema.

If the previous release is **not** compatible with the current schema, do not attempt an automatic database downgrade. Use a forward-compatible fix/new release instead.

---

## 3. Disk Guard During Rollback

The deployment script performs a disk-space guard before pulling images.

If the guard fails, investigate disk usage before bypassing it.

Emergency bypass:

```bash
SKIP_DISK_GUARD=1 SKIP_MIGRATIONS=1 ./infra/deploy.sh sha-<known-good-sha>
```

`SKIP_DISK_GUARD=1` is emergency-only.

Before using it, manually verify that enough disk space is available and that the target images are already present locally or can safely be pulled.

---

## 4. Post-Rollback Verification

Check the deployment status:

```bash
docker compose \
  --env-file infra/.env.runtime \
  -f infra/docker-compose.staging.yml \
  ps
```

Check backend health:

```bash
curl --fail --silent --show-error \
  http://127.0.0.1:8000/health
```

Check frontend:

```bash
curl --fail --silent --show-error \
  http://127.0.0.1:3000/
```

Check the running backend image:

```bash
docker inspect \
  $(docker compose \
    --env-file infra/.env.runtime \
    -f infra/docker-compose.staging.yml \
    ps -q backend) \
  --format '{{.Config.Image}}'
```

Check the running frontend image:

```bash
docker inspect \
  $(docker compose \
    --env-file infra/.env.runtime \
    -f infra/docker-compose.staging.yml \
    ps -q frontend) \
  --format '{{.Config.Image}}'
```

Expected result:

```text
ghcr.io/openlearn-ai/openlearn-backend:sha-<target-sha>
ghcr.io/openlearn-ai/openlearn-frontend:sha-<target-sha>
```

Then verify the public endpoints:

* Backend: `https://openlearn-api-staging.duckdns.org/health`
* Frontend: `https://openlearn-web-staging.duckdns.org/`

---

## 5. Database Safety

Rollback does not automatically reverse database migrations.

### Same-schema rollback

If the target application release is compatible with the current schema:

```bash
SKIP_MIGRATIONS=1 ./infra/deploy.sh sha-<known-good-sha>
```

### Schema-incompatible rollback

If the target application requires an older database schema:

* Do not downgrade the database automatically.
* Do not manually delete migration state.
* Do not run destructive SQL as part of the rollback.
* Stop the rollback and prepare a forward-compatible application fix.

The database remains at its current schema version.

---

## 6. Third-Party Digest Pin Updates

Third-party container images in `docker-compose.staging.yml` are pinned by immutable digest.

A digest update must be deliberate.

### Update procedure

1. Obtain the new image digest from the trusted upstream registry.
2. Update only the intended image reference in `docker-compose.staging.yml`.
3. Verify the digest:

```bash
docker manifest inspect <image>@sha256:<new-digest>
```

4. Validate the compose configuration:

```bash
docker compose \
  --env-file infra/.env.runtime \
  -f infra/docker-compose.staging.yml \
  config
```

5. Run CI.
6. Deploy the resulting staging change.
7. Verify service health.

### Digest rollback

If a digest update causes a staging problem:

1. Restore the previously known-good digest in `docker-compose.staging.yml`.
2. Run compose validation again.
3. Run CI.
4. Deploy the reverted digest configuration.
5. Verify service health.

Do not replace a digest pin with a floating tag such as:

```text
:latest
:main-latest
```

---

## 7. What Not To Do

Never perform these actions during rollback:

```bash
docker compose down -v
docker volume prune
docker system prune -a
docker rmi -f
```

Do not:

* manually delete `/var/lib/docker`;
* manually delete `/var/lib/containerd`;
* delete PostgreSQL volumes;
* downgrade the database automatically;
* use timestamp-based image deletion;
* remove images that are referenced by running or stopped containers;
* force-delete images to make disk space available.

The deployment script performs safe SHA-image cleanup after successful health checks.

---

## 8. Rollback Principle

The rollback target must be an existing immutable GHCR SHA.

The Git commit and the container image are separate concerns:

```text
Known-good Git SHA
        ↓
Existing GHCR backend image
        +
Existing GHCR frontend image
        ↓
deploy.sh
        ↓
Health checks
        ↓
Staging restored
```

A Git commit is **not** by itself a rollback artifact unless the corresponding container images are available in GHCR.

---

## 9. Current Verified Rollback Target

The following release has been verified as an available rollback artifact on the staging VPS:

```text
sha-480e93748baa93072d49c8c5a737e3ec1b0a4a08
```

Backend image was successfully pulled and verified.

Frontend image was successfully pulled and verified.

No rollback was performed as part of this runbook validation.

---

## 10. Week 7 Material Processing: Hard-Kill/OOM Recovery Backstop

If a material remains stuck in `processing` because the Celery worker was
hard-killed or OOM-killed and the task's failure handler could not run, an
operator may manually mark it `failed`:

```sql
UPDATE materials
SET status = 'failed'
WHERE id = :material_id
  AND status = 'processing';
```

- Only perform this after confirming the worker is no longer processing that material.
- This is a manual recovery backstop for the known hard-kill/OOM case only.
- This is **not** an automatic recovery mechanism.

---

## 11. Rollback Completion Checklist

* [ ] Target backend SHA exists in GHCR.
* [ ] Target frontend SHA exists in GHCR.
* [ ] VPS has GHCR authentication.
* [ ] Disk space was checked.
* [ ] Database schema compatibility was considered.
* [ ] `SKIP_MIGRATIONS=1` was used when appropriate.
* [ ] Disk guard was not bypassed unless necessary.
* [ ] Backend health check passes.
* [ ] Frontend health check passes.
* [ ] Running containers use the intended SHA.
* [ ] Public staging endpoints respond successfully.
* [ ] No destructive Docker cleanup was performed.
* [ ] No database downgrade was performed.
* [ ] Incident and rollback details were recorded.
