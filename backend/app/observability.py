import sys
import logging
import os
import structlog
import sentry_sdk

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator


_SENTRY_DEFAULT_ENVIRONMENT = "staging"


def _sentry_config(integrations=None) -> dict | None:
    """Sentry init kwargs when a DSN is configured; ``None`` is the no-op case."""
    dsn = os.getenv("SENTRY_DSN", "")
    if not dsn:
        return None
    config = {
        "dsn": dsn,
        "traces_sample_rate": 1.0,
        "environment": os.getenv("ENVIRONMENT", _SENTRY_DEFAULT_ENVIRONMENT),
    }
    if integrations is not None:
        config["integrations"] = integrations
    return config


def setup_sentry() -> bool:
    """Initialize the Sentry SDK when a DSN is configured; ``False`` (no
    client, no-op) when ``SENTRY_DSN`` is empty or missing."""
    config = _sentry_config()
    if config is None:
        return False
    sentry_sdk.init(**config)
    return True


def setup_observability():
    setup_sentry()


    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def setup_worker_sentry() -> bool:
    """Initialize the Sentry SDK inside a Celery worker process (F9).

    Reuses the API's Sentry configuration and adds the Celery integration so
    task failures are reported. Called from a ``worker_process_init`` handler so
    the SDK is initialized in each forked worker process, never at Celery
    import or master-process time. Returns ``False`` when no DSN is configured
    (a no-op).
    """
    from sentry_sdk.integrations.celery import CeleryIntegration

    config = _sentry_config(integrations=[CeleryIntegration()])
    if config is None:
        return False
    sentry_sdk.init(**config)
    return True


def setup_metrics(app: FastAPI):
    # FastAPI 0.138+ wraps included routers in _IncludedRouter, which lacks
    # the .path attribute that prometheus-fastapi-instrumentator 7.1.0
    # expects. Patch _get_route_name to handle _IncludedRouter by recursing
    # into original_router.routes.
    import prometheus_fastapi_instrumentator.routing as pfi_routing
    from starlette.routing import Match

    _orig_get_route_name = pfi_routing._get_route_name

    def _safe_get_route_name(scope, routes, route_name=None):
        for route in routes:
            match, child_scope = route.matches(scope)
            if match == Match.FULL:
                if hasattr(route, "path"):
                    route_name = route.path
                elif hasattr(route, "routes"):
                    child = _safe_get_route_name(child_scope, route.routes, route_name)
                    return child
                elif hasattr(route, "original_router"):
                    child = _safe_get_route_name(scope, route.original_router.routes, route_name)
                    return child
                return route_name
        return None

    pfi_routing._get_route_name = _safe_get_route_name
    Instrumentator().instrument(app).expose(app)