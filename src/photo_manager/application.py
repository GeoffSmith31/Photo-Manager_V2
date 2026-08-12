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
Photo Manager Application

## Purpose

Manages the application lifecycle.

## Responsibilities

- Create and manage the Qt application instance.
- Start the Photo Manager application.

## Notes

The Application service owns the Qt application instance and
event loop.

The Orchestrator owns the Photo Manager application workflow
and application state.

The Window Manager owns and coordinates the application's
GUI windows.
"""

import sys
from photo_manager.window_manager import WindowManager
from PySide6.QtWidgets import QApplication
from photo_manager.constants import (
    APPLICATION_NAME,
    APPLICATION_ORGANISATION,
)


# -----------------------------------------------------------------
# Application
# -----------------------------------------------------------------

class Application:
    """
    Owns the Photo Manager application lifecycle.
    """

    # -------------------------------------------------------------
    # Constructor
    # -------------------------------------------------------------

    def __init__(self) -> None:
        """
        Initialise the Photo Manager application.
        """

        self._application = QApplication(
            sys.argv
        )

        self._application.setApplicationName(
            APPLICATION_NAME
        )

        self._application.setApplicationDisplayName(
            APPLICATION_NAME
        )

        self._application.setOrganizationName(
            APPLICATION_ORGANISATION
        )

        self._window_manager = WindowManager()

    # -------------------------------------------------------------
    # Run
    # -------------------------------------------------------------

    def run(self) -> int:
        """
        Start the Qt application event loop.

        Returns
        -------
        int
            Application exit code.
        """
        self._window_manager.show_control_tower()

        return self._application.exec()


# ============================================================================
# Standalone Test Harness
# ============================================================================

if __name__ == "__main__":

    application = Application()

    sys.exit(
        application.run()
    )
