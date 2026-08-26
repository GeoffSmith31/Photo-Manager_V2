# =============================================================================
# Photo Manager
#
# Copyright (c) 2026 Geoff [dev.photomanager@gmail.com]
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# =============================================================================

"""
Photo Manager Multi-OS Support

Provides operating-system-specific functionality used by Photo Manager.

All platform-dependent implementation should be contained in this module
where practical, allowing the remainder of the application to remain
operating-system independent.
"""
import platform
import shutil
import subprocess
from .constants import (
    MAPS_BROWSER_PROFILE_DIRECTORY,
    SUPPORTED_BROWSERS,
)
# ---------------------------------------------------------------------
# Browser Discovery
# ---------------------------------------------------------------------

def find_supported_browser() -> dict | None:
    """
    Find the preferred supported web browser installed on this system.

    Browsers are checked in the order defined by SUPPORTED_BROWSERS.

    Returns:
        The supported browser definition when one is available.
        None when no supported browser is installed.
    """

    system_name = platform.system()

    if system_name == "Linux":
        platform_name = "linux"

    elif system_name == "Windows":
        platform_name = "windows"

    elif system_name == "Darwin":
        platform_name = "macos"

    else:
        return None

    for browser in SUPPORTED_BROWSERS:

        executables = browser["executables"].get(
            platform_name,
            (),
        )

        for executable in executables:

            executable_path = shutil.which(
                executable
            )

            if executable_path is not None:

                return {
                    "name": browser["name"],
                    "executable": executable_path,
                }

    return None
    
# ---------------------------------------------------------------------
# Browser Launch
# ---------------------------------------------------------------------

def launch_browser(
    browser: dict,
    url: str,
) -> subprocess.Popen:
    """
    Launch a supported web browser for Google Maps.

    A dedicated Photo Manager browser profile is used so that the
    browser instance can be owned and controlled by Photo Manager
    independently of the user's normal browser session.

    The browser definition must have been returned by
    find_supported_browser().

    Returns:
        The running browser process.

    Raises:
        OSError: If the browser cannot be launched.
        ValueError: If the browser definition is invalid or the
                    operating system is unsupported.
    """

    executable = browser.get(
        "executable"
    )

    if not executable:
        raise ValueError(
            "Browser definition does not contain an executable."
        )

    MAPS_BROWSER_PROFILE_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    system_name = platform.system()

    if system_name == "Linux":

        command = [
            executable,
            "--user-data-dir="
            + str(MAPS_BROWSER_PROFILE_DIRECTORY),
            "--no-first-run",
            "--no-default-browser-check",
            "--new-window",
            url,
        ]

    elif system_name == "Windows":

        command = [
            executable,
            "--user-data-dir="
            + str(MAPS_BROWSER_PROFILE_DIRECTORY),
            "--no-first-run",
            "--no-default-browser-check",
            "--new-window",
            url,
        ]

    elif system_name == "Darwin":

        command = [
            executable,
            "--user-data-dir="
            + str(MAPS_BROWSER_PROFILE_DIRECTORY),
            "--no-first-run",
            "--no-default-browser-check",
            "--new-window",
            url,
        ]

    else:

        raise ValueError(
            f"Unsupported operating system: {system_name}"
        )

    return subprocess.Popen(
        command,
    )
