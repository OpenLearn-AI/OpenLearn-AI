import sys
import logging
import os
import structlog
import sentry_sdk

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator


def setup_observability():
  
    
   
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", ""),
        traces_sample_rate=1.0,
        environment=os.getenv("ENVIRONMENT", "staging"),
    )


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