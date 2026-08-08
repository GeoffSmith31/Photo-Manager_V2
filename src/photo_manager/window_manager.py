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
Photo Manager Window Manager

Purpose
-------
Coordinates all windows used by the Photo Manager application.

Responsibilities
----------------
- Display the Control Tower window.
- Display application status information.
- Display user interaction dialogs.
- Coordinate modal dialogs.
- Coordinate external application windows (e.g. Playwright).
- Manage window activation and focus.

Notes
-----
This module is an infrastructure service.

Application components do not communicate directly with GUI windows.

Instead, all window management is coordinated through the
Window Manager.

The Window Manager provides a consistent interface for
application components to interact with the user without
knowing the underlying GUI implementation.
"""

from pathlib import Path
import logging

from photo_manager.logging import (
    configure_logging,
    get_logger,
)

logger = get_logger("Window Manager")


# ---------------------------------------------------------------------
# Window Manager
# ---------------------------------------------------------------------

class WindowManager:
    """
    Coordinates all application windows.
    """

    # -------------------------------------------------------------
    # Constructor
    # -------------------------------------------------------------

    def __init__(self) -> None:

        logger.debug(
            "Initialising Window Manager."
        )

    # -------------------------------------------------------------
    # Status Message
    # -------------------------------------------------------------

    def status_message(
        self,
        message: str,
    ) -> None:
        """
        Display a status message in the Control Tower.

        Status messages provide information about the
        application's current activity and do not require
        user acknowledgement.
        """

        logger.info(
            "STATUS: %s",
            message,
        )

        # TODO:
        # Update the Control Tower activity panel.

    # -------------------------------------------------------------
    # User Interaction
    # -------------------------------------------------------------

    def user_interaction(
        self,
        title: str,
        message: str,
    ) -> None:
        """
        Display a modal dialog requiring user acknowledgement.
        """

        logger.info(
            "USER INTERACTION: %s",
            title,
        )

        logger.info(
            "%s",
            message,
        )

        # TODO:
        # Display a modal dialog.

    # -------------------------------------------------------------
    # Select Directory
    # -------------------------------------------------------------

    def select_directory(
        self,
        title: str,
    ) -> Path | None:
        """
        Request the user selects a directory.

        Returns
        -------
        Path
            The selected directory.

        None
            The user cancelled the selection.
        """

        logger.info(
            "Selecting directory: %s",
            title,
        )

        # TODO:
        # Display directory picker.

        return None


# ============================================================================
# Standalone Test Harness
# ============================================================================

if __name__ == "__main__":

    configure_logging(
        level=logging.DEBUG,
        console_logging=True,
    )

    windows = WindowManager()

    windows.status_message(
        "Loading application settings."
    )

    windows.user_interaction(
        title="Workspace Required",
        message="No workspace has been configured.",
    )

    workspace = windows.select_directory(
        title="Select Workspace",
    )

    print(
        f"Selected Workspace: {workspace}"
    )
