from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent


class Settings(BaseSettings):
    # TODO(REMOVE BEFORE DEPLOYMENT): the defaults for ``environment``,
    # ``debug``, ``database_url`` (dev password) and the ``keycloak_*`` http
    # URLs below are local-development conveniences only. Before any
    # deployment, delete these defaults so a missing environment variable
    # fails at start-up instead of silently using a known password or an
    # http issuer (review finding B-09).
    app_name: str = "OpenLearn AI"
    environment: str = "development"
    debug: bool = False
    cors_origins: str = "http://localhost:3000"
    database_url: str = (  # TODO(REMOVE BEFORE DEPLOYMENT): dev password default
        "postgresql+asyncpg://openlearn:devpassword@localhost:5432/openlearn_dev"
    )

    # Keycloak / OIDC
    # TODO(REMOVE BEFORE DEPLOYMENT): http dev defaults; require https URLs.
    keycloak_issuer: str = "http://localhost:8080/realms/openlearn"
    keycloak_jwks_url: str = (
        "http://localhost:8080/realms/openlearn/protocol/openid-connect/certs"
    )
    keycloak_audience: str = "openlearn-api"
    # Frontend client that obtains the tokens; a token whose ``azp`` claim
    # names another client is rejected (review finding B-14).
    keycloak_client_id: str = "openlearn-frontend"

    # Observability (review findings B-03, B-12). ``metrics_token`` protects
    # GET /metrics: when set, the endpoint requires ``Authorization: Bearer
    # <token>``; when empty it is exposed only outside production.
    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = 0.1
    metrics_token: str = ""

    # Per-user limit for the write endpoints (upload-url, register, process,
    # create course), requests per minute. 0 disables the limit.
    rate_limit_writes_per_minute: int = 30

    # PAL / AI Settings
    ai_ocr_provider: str = "mock"
    ai_ocr_fallbacks: str = ""
    # Direct Gemini OCR model (google-genai generate_content; the LiteLLM
    # gateway is not in the OCR path). gemini-2.5-flash is rejected with
    # HTTP 404 "no longer available to new users" on this Google account
    # (B6 reasoning runtime attempt; B8 OCR staging run b8v1791396817).
    # gemini-3.6-flash is the model runtime-proven available to this account
    # (B6-CLOSEOUT / B7 RSN_CALL evidence) — see
    # docs/tasks/ai-week7-8/progress.md before changing this value.
    ai_ocr_model: str = "gemini-3.6-flash"
    gemini_api_key: str = ""
    ai_embedding_provider: str = "mock"
    ai_embedding_fallbacks: str = ""
    ai_embedding_model: str = "BAAI/bge-m3"
    ai_embedding_dimension: int = 1024
    # Device for local embedding inference: "auto" (CUDA if available, else
    # CPU), "cpu" (forced CPU), or "cuda" (requires an actual CUDA device).
    ai_embedding_device: str = "auto"
    ai_reasoning_provider: str = "mock"
    ai_reasoning_fallbacks: str = ""
    # Must equal the gateway's model_list alias (infra/litellm-config.yaml);
    # the worker sends it as the chat-completion model name.
    ai_reasoning_model: str = "gemini-3.6-flash"

    # LiteLLM gateway (ADR-0005) — OpenAI-compatible reasoning surface.
    # The key is a LiteLLM virtual/master key; staging env wiring is a
    # DevOps task (H1), not an application concern.
    litellm_api_base: str = "http://litellm:4000"
    litellm_api_key: str = ""
    ai_vector_db_provider: str = "mock"

    # Chunking
    chunk_size: int = 1200
    chunk_overlap: int = 150

    # OCR text-length gate (targeted-OCR eligibility; services/ocr.py)
    ocr_min_text_chars: int = 50

    # ── Redis / Celery broker ────────────────────────────────────────────
    # Resolved through this Settings contract by BOTH the API process and the
    # Celery worker (app/workers/celery_app.py). Single source of truth: the
    # previous raw os.getenv("REDIS_PASSWORD") in celery_app.py was reachable
    # only through the process environment, which the documented API start
    # command (uvicorn app.main:app --reload --port 8000) never satisfies —
    # the root cause of the HTTP-500 material-registration failure.
    #
    # Precedence (pydantic-settings): process environment > backend/.env >
    # repository-root .env.local (the LATER env_file below wins for keys it
    # shares) > the defaults here. The generated credentials live ONLY in
    # .env.local (written by scripts/setup-dev.sh, git-ignored); staging
    # supplies real environment variables and has no .env.local, so the
    # container-network default host below is what staging composes.
    redis_url: str = ""          # full-URL override; wins outright when set
    redis_password: str = ""     # required unless redis_url is set
    redis_host: str = "redis"    # container-network hostname (staging default)
    redis_port: int = 6379

    # S3-compatible object storage (MinIO) for course materials
    # Credentials are deployment configuration and must never be hardcoded.
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_bucket_name: str = "openlearn-materials"
    s3_region_name: str = "us-east-1"
    # Upload URL lifetime: short, because the URL can overwrite the object
    # until it expires (review findings B-02 / P-01).
    s3_url_expiration_seconds: int = 900
    # Hard cap enforced by the presigned POST policy and re-checked at
    # registration (review findings B-02 / P-02): 10 MiB.
    max_upload_size_bytes: int = 10 * 1024 * 1024

    # Materials stuck in pending/processing longer than this are marked
    # failed by the periodic reaper (review finding B-07). Must stay above the
    # Celery hard time limit (11 minutes) plus the automatic-retry backoff.
    material_stuck_timeout_minutes: int = 30

    model_config = SettingsConfigDict(
        # Order matters: for keys defined in BOTH files the LATER file wins
        # (verified empirically against pydantic-settings==2.15.0), so
        # backend/.env stays the authoritative backend configuration and the
        # root .env.local (infrastructure secrets generated by
        # scripts/setup-dev.sh) fills the gaps — e.g. REDIS_PASSWORD, which
        # intentionally lives only there. Process-environment variables beat
        # both files; a missing file is silently skipped, which keeps
        # staging (no .env.local) and fresh clones unaffected.
        env_file=(REPO_ROOT / ".env.local", BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def redis_connection_url(self) -> str:
        """Effective Redis URL for the Celery broker and result backends.

        An explicit ``redis_url`` wins outright (it is expected to embed its
        own credentials, so no password is required in that case). Otherwise
        the URL is composed from ``redis_password``/``redis_host``/
        ``redis_port``. An unresolvable configuration fails fast here with an
        actionable diagnostic — never fall back to an unauthenticated or
        invented default. The password value itself is never included in the
        error text.
        """
        if self.redis_url:
            return self.redis_url
        if not self.redis_password:
            raise RuntimeError(
                "Redis connection settings could not be resolved for the "
                "Celery app.\n"
                "The API and the worker resolve Redis configuration through "
                "app.config.Settings, from (in order of precedence):\n"
                "  1. the process environment (REDIS_URL or REDIS_PASSWORD),\n"
                "  2. backend/.env,\n"
                "  3. the repository-root .env.local written by "
                "scripts/setup-dev.sh.\n"
                "None of them provided REDIS_URL or REDIS_PASSWORD.\n"
                "Fix: run 'bash scripts/setup-dev.sh' (writes the local Redis "
                "credentials into .env.local), or start the worker with "
                "'bash scripts/run-worker-dev.sh', or export REDIS_PASSWORD "
                "before starting the API with uvicorn."
            )
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}"

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def ocr_fallback_list(self) -> list[str]:
        return [f.strip() for f in self.ai_ocr_fallbacks.split(",") if f.strip()]

    @property
    def embedding_fallback_list(self) -> list[str]:
        return [f.strip() for f in self.ai_embedding_fallbacks.split(",") if f.strip()]

    @property
    def reasoning_fallback_list(self) -> list[str]:
        return [f.strip() for f in self.ai_reasoning_fallbacks.split(",") if f.strip()]



settings = Settings()
