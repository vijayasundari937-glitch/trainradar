import logging
import sys
import structlog
from config.settings import settings


def setup_logging():
    """
    Sets up structured logging for the entire app.
    In development: pretty coloured output in your terminal.
    In production: JSON format for log aggregators.
    """

    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if settings.app_env == "development":
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        processors = shared_processors + [
            structlog.processors.JSONRenderer()
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(sys.stdout),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )


def get_logger(name: str):
    """
    Call this in any file to get a logger.
    Usage:  logger = get_logger(__name__)
            logger.info("something happened", value=42)
    """
    return structlog.get_logger(name)