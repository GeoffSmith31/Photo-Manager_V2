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
Photo Manager Settings

Purpose
-------
Provides the application settings service used by all Photo Manager
components.

Responsibilities
----------------
- Load application settings.
- Save application settings.
- Create default application settings.
- Validate application settings.
- Recover from missing or invalid settings files.

Notes
-----
This module is an infrastructure service.

The Settings Service is responsible only for application-wide
configuration.

Workspace-specific configuration is stored separately in the
workspace's project.json file.

The Settings Service guarantees that application components receive
a valid Settings object, regardless of whether the settings were
loaded from disk or created using default values.
"""
from dataclasses import dataclass
from pathlib import Path
import logging
import json
from platformdirs import user_config_dir
from photo_manager.application import APPLICATION_ID
from photo_manager.logging import (
    configure_logging,
    get_logger,
)

logger = get_logger("Settings Service")

# ---------------------------------------------------------------------
# Settings Data Model
# ---------------------------------------------------------------------
@dataclass
class Settings:
    """
    Application-wide configuration.

    This class contains persistent application settings only.

    Workspace-specific configuration is stored in project.json.
    """

    logging_level: int
    workspace_directory: Path | None


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------
__all__ = [
    "Settings",
    "create_default_settings",
    "load_settings",
    "save_settings",
]


def create_default_settings() -> Settings:
    """
    Return the default application settings.
    """

    return Settings(
        logging_level=logging.INFO,
        workspace_directory=None,
    )   
    
# ---------------------------------------------------------------------
# Settings File Location
# ---------------------------------------------------------------------    
def get_settings_file() -> Path:
    """
    Return the path to the application's settings file.
    """

    config_directory = Path(
        user_config_dir(APPLICATION_ID)
    )

    config_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return config_directory / "settings.json"

# ---------------------------------------------------------------------
# Convert Settings to Dict
# ---------------------------------------------------------------------  
def settings_to_dict(
    settings: Settings,
) -> dict:
    """
    Convert a Settings object into a JSON-serialisable dictionary.
    """

    return {
        "logging_level": logging.getLevelName(
            settings.logging_level,
        ),
        "workspace_directory": (
            str(settings.workspace_directory)
            if settings.workspace_directory is not None
            else None
        ),
    }


# ---------------------------------------------------------------------
# Convert Settings from Dict
# ---------------------------------------------------------------------

def settings_from_dict(
    data: dict,
) -> Settings:
    """
    Convert a JSON dictionary into a Settings object.
    """

    logging_level_name = data.get(
        "logging_level",
        "INFO",
    )

    workspace_directory = data.get(
        "workspace_directory",
    )

    return Settings(
        logging_level=getattr(
            logging,
            logging_level_name,
        ),
        workspace_directory=(
            Path(workspace_directory)
            if workspace_directory is not None
            else None
        ),
    )
# ---------------------------------------------------------------------
# Save Settings
# ---------------------------------------------------------------------

def save_settings(
    settings: Settings,
) -> None:
    """
    Save the application settings.
    """

    logger.info("Saving application settings.")

    settings_file = get_settings_file()

    settings_dict = settings_to_dict(
        settings,
    )

    with settings_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            settings_dict,
            file,
            indent=4,
            ensure_ascii=False,
        )

    logger.info(
        "Application settings saved to %s",
        settings_file,
    )

# ---------------------------------------------------------------------
# Load Settings
# ---------------------------------------------------------------------
def load_settings() -> Settings:

    logger.info("Loading application settings.")

    settings_file = get_settings_file()

    try:

        with settings_file.open(
            "r",
            encoding="utf-8",
        ) as file:

            settings_dict = json.load(file)

        settings = settings_from_dict(
            settings_dict,
        )

        logger.info(
            "Application settings loaded from %s",
            settings_file,
        )

        return settings

    except FileNotFoundError:

        logger.info(
            "Settings file not found. Creating default settings."
        )

    except (
        json.JSONDecodeError,
        KeyError,
        AttributeError,
        TypeError,
    ) as error:

        logger.warning(
            "Settings file is invalid. Restoring default settings."
        )
        logger.debug(
            "Settings recovery reason: %s",
            error,
        )

    settings = create_default_settings()

    save_settings(settings)

    return settings


# ============================================================================
# Standalone test harness
# ============================================================================
if __name__ == "__main__":

    configure_logging(
        level=logging.DEBUG,
        console_logging=True,
    )

    settings = load_settings()

    print(settings)
