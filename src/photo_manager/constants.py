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
Photo Manager Constants

## Purpose

Provides application-wide constants 

## Responsibilities

- Define the application's identity.
- Provide application naming constants.
- Define standard filenames used by the application.

## Notes


"""
from pathlib import Path

# -----------------------------------------------------------------
# Application Identity
# -----------------------------------------------------------------

APPLICATION_NAME = "Photo Manager"

APPLICATION_ID = "photo_manager"

APPLICATION_ORGANISATION = "Photo Manager"

APPLICATION_AUTHOR = "Geoff"


# -----------------------------------------------------------------
# Application Directories
# -----------------------------------------------------------------

APPLICATION_CONFIG_DIRECTORY = (
    Path.home()
    / ".config"
    / APPLICATION_ID
)

APPLICATION_DATA_DIRECTORY = (
    Path.home()
    / ".local"
    / "share"
    / APPLICATION_ID
)

APPLICATION_LOG_DIRECTORY = (
    APPLICATION_DATA_DIRECTORY
    / "logs"
)

MAPS_BROWSER_PROFILE_DIRECTORY = (
    APPLICATION_DATA_DIRECTORY
    / "maps_browser"
)
# -----------------------------------------------------------------
# Project File
# -----------------------------------------------------------------

SCHEMA_VERSION = 2

# -----------------------------------------------------------------
# Standard Filenames
# -----------------------------------------------------------------

SETTINGS_FILENAME = "settings.json"

PROJECT_FILENAME = "project.json"

LOG_FILENAME = "photo_manager.log"

# -----------------------------------------------------------------
# Help URL
# -----------------------------------------------------------------
HELP_URL = (
    "https://geoffsmith31.github.io/Photo-Manager_V2/"
)
# -----------------------------------------------------------------
# Control Tower Defaults
# -----------------------------------------------------------------

CONTROL_TOWER_DEFAULT_WIDTH = 1200

CONTROL_TOWER_DEFAULT_HEIGHT = 800

CONTROL_TOWER_MINIMUM_WIDTH = 1050

CONTROL_TOWER_MINIMUM_HEIGHT = 600

# -----------------------------------------------------------------
# Public API
# -----------------------------------------------------------------

__all__ = [
    "APPLICATION_NAME",
    "APPLICATION_ID",
    "APPLICATION_ORGANISATION",
    "APPLICATION_AUTHOR",
    "SETTINGS_FILENAME",
    "PROJECT_FILENAME",
    "LOG_FILENAME",
    "MAPS_BROWSER_PROFILE_DIRECTORY",
    "CONTROL_TOWER_DEFAULT_WIDTH",
    "CONTROL_TOWER_DEFAULT_HEIGHT",
    "CONTROL_TOWER_MINIMUM_WIDTH",
    "CONTROL_TOWER_MINIMUM_HEIGHT",
    "HELP_URL",
    "Application",
]
# ---------------------------------------------------------------------
# Supported Web Browsers
# ---------------------------------------------------------------------

SUPPORTED_BROWSERS = (

    {
        "name": "Firefox",
        "executables": {
            "linux": (
                "firefox",
            ),
            "windows": (
                "firefox.exe",
            ),
            "macos": (
                "firefox",
            ),
        },
    },

    {
        "name": "Google Chrome",
        "executables": {
            "linux": (
                "google-chrome",
                "google-chrome-stable",
            ),
            "windows": (
                "chrome.exe",
            ),
            "macos": (
                "Google Chrome",
            ),
        },
    },

)
