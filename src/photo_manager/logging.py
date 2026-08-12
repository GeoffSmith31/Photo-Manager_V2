# =============================================================================
# Photo Manager
#
# Copyright (c) 2026 Geoff <dev.photomanager@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# =============================================================================

"""
Photo Manager Logging

Purpose
-------
Provides the application logging service used by all Photo Manager
components.

Responsibilities
----------------
- Configure application logging.
- Create named loggers.
- Apply the configured logging level.
- Write log messages to the configured destinations.

Notes
-----
This module is an infrastructure service.

The logging service is configured during application startup by the
Orchestrator and may subsequently be used directly by application
components.
The logging service determines the names and management of log files.

The application specifies only the directory in which log files are stored.
"""

from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from photo_manager.constants import LOG_FILENAME

# ---------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------

_LOG_FILE_NAME = LOG_FILENAME

_KB = 1024
_MB = 1024 * _KB

_LOG_MAX_BYTES = 5 * _MB

_LOG_BACKUP_COUNT = 5

_LOG_FORMAT = (
    "%(asctime)s "
    "[%(levelname)-7s] "
    "%(name)-20s "
    "%(message)s"
)

_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

#------------------------------------------------------------------------

__all__ = [
    "configure_logging",
    "get_logger",
]


def configure_logging(
    level: int,
    log_directory: Path | None = None,
    console_logging: bool = True,
) -> None:
    """
    Configure the Photo Manager logging service.

    Parameters
    ----------
    level
        Python logging level (e.g. logging.DEBUG).

    log_directory
        Directory in which application log files will be written.
        If None, file logging is disabled.

    console_logging
        If True, log messages are written to the console.
        If False, console logging is disabled.
    """

    # Obtain the application's root logger.
    root_logger = logging.getLogger()

    # Remove any existing handlers so repeated initialisation
    # always starts from a known state.
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)

    # Set the minimum logging level.
    root_logger.setLevel(level)

    # Create the formatter.
    formatter = logging.Formatter(
        _LOG_FORMAT,
        datefmt=_LOG_DATE_FORMAT,
    )

    # -----------------------------------------------------------------
    # Console logging
    # -----------------------------------------------------------------

    if console_logging:

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # -----------------------------------------------------------------
    # File logging
    # -----------------------------------------------------------------

    if log_directory is not None:

        # Ensure the log directory exists.
        log_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Construct the application log filename.
        log_file = log_directory / _LOG_FILE_NAME

        # Create the rotating file handler.
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=_LOG_MAX_BYTES,
            backupCount=_LOG_BACKUP_COUNT,
        )

        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # -----------------------------------------------------------------
    # Log the logging service configuration.
    # -----------------------------------------------------------------

    logger = get_logger("Logging Service")

    logger.info("Logging service initialised.")
    logger.info(
        "Logging level: %s",
        logging.getLevelName(level),
    )

    if log_directory is not None:
        logger.info(
            "Log file: %s",
            log_file.resolve(),
        )
    else:
        logger.info("File logging disabled.")


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger for the specified application component.
    """

    return logging.getLogger(name)


# ============================================================================
# Standalone test harness
# ============================================================================
if __name__ == "__main__":

    configure_logging(
        level=logging.DEBUG,
        log_directory=Path("./logs"),
        console_logging=True,
    )

    logger = get_logger(__name__)

    logger.debug("Debug message")
    logger.info("Information message")
    logger.warning("Warning message")
    logger.error("Error message")
