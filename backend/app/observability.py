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
    Instrumentator().instrument(app).expose(app)