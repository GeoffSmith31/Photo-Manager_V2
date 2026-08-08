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
Photo Manager Orchestrator

Purpose
-------
Coordinates the operation of the Photo Manager application.

Responsibilities
----------------
- Coordinate application startup and shutdown.
- Implement the Photo Manager user workflow.
- Coordinate communication between application services.
- Manage the active workspace and project.
- Coordinate user-initiated operations.
- Report application-level errors.

Notes
-----
The Orchestrator is the central coordinator for the application.

Application services do not communicate directly with one another.
Instead, all application workflow is coordinated through the
Orchestrator.

Infrastructure services (Application, Logging and Settings) may be
accessed directly by application components where appropriate.

The Orchestrator is the single source of truth for the application's
operational state.

The Orchestrator owns the application's current state and determines
the sequence in which application services are invoked.
"""

from enum import Enum, auto
from pathlib import Path
import logging
import os
from photo_manager.logging import (
    configure_logging,
    get_logger,
)
from photo_manager.settings import (
    Settings,
    load_settings,
)
from photo_manager.window_manager import WindowManager

logger = get_logger("Orchestrator")


# ---------------------------------------------------------------------
# Application State
# ---------------------------------------------------------------------

class ApplicationState(Enum):
    """
    Represents the application's operational mode.

    The current state determines:

    - the active user workflow step,
    - the primary workspace view,
    - the operations available to the user,
    - the services coordinated by the Orchestrator.
    """

    STARTING = auto()

    PROJECT_SELECTION = auto()

    CONNECTING_SOURCE = auto()

    REGISTERING = auto()

    DOWNLOADING = auto()

    EDITING = auto()

    SHUTTING_DOWN = auto()


# ---------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------

class Orchestrator:
    """
    Coordinates the operation of the Photo Manager application.
    """

    def __init__(self):
        """
        Initialise the Orchestrator.
        """

        # Current application state.
        self._state = ApplicationState.STARTING

        # Previous application state.
        self._previous_state = ApplicationState.STARTING

        # Current application settings.
        self._settings = None

        # Active workspace.
        self._workspace = None
        
        self._window_manager = WindowManager()

        # Active project.
        self._project = None

        # Active importer.
        self._importer = None

    @property
    def state(self) -> ApplicationState:
        """
        Return the application's current operational state.
        """

        return self._state

    # -----------------------------------------------------------------
    # Set Application State
    # -----------------------------------------------------------------

    def _set_state(
        self,
        state: ApplicationState,
    ) -> None:
        """
        Change the application's operational state.
        """

        if state == self._state:
            return

        logger.info(
            "Application state changed: %s -> %s",
            self._state.name,
            state.name,
        )

        self._previous_state = self._state
        self._state = state

        # Future enhancements:
        #
        # - Notify the GUI.
        # - Update the workflow panel.
        # - Enable/disable user commands.
        # - Publish state change events.
        
    # -----------------------------------------------------------------
    # Start Up
    # -----------------------------------------------------------------
    def startup(self) -> None:
        """
        Initialise the Photo Manager application.
        """

        logger.info(
            "Starting Photo Manager."
        )

        self._set_state(
            ApplicationState.STARTING,
        )

        self._load_settings()
        
        # Ensures a valid workspace is available.
        # May request that the user selects one.
        self._validate_workspace()

        self._discover_projects()

        self._present_project_selection()

        logger.info(
            "Startup complete."
        )
    
    # -----------------------------------------------------------------
    # Load Settings
    # -----------------------------------------------------------------

    def _load_settings(self) -> None:
        """
        Load the application settings.
        """
        logger.debug(
        "Loading application settings."
        )
        self._settings = load_settings()

        logger.debug(
            "Application settings loaded."
        )
        
        self._window_manager.status_message(
            "Loading application settings."
        )


    # -----------------------------------------------------------------
    # Validate Workspace
    # -----------------------------------------------------------------

    def _validate_workspace(self) -> None:
        """
        Validate the configured workspace.
        """

        logger.debug(
            "Validating workspace."
        )
        
        self._window_manager.status_message(
            "Validating workspace."
        )

        workspace = self._settings.workspace_directory

        valid = True
        validation_message = None

        # -------------------------------------------------------------
        # Validate the configured workspace.
        # -------------------------------------------------------------

        if workspace is None:

            valid = False
            validation_message = (
                "No workspace has been configured."
            )

        elif not workspace.exists():

            valid = False
            validation_message = (
                f"Configured workspace does not exist: {workspace}"
            )

        elif not workspace.is_dir():

            valid = False
            validation_message = (
                f"Configured workspace is not a directory: {workspace}"
            )

        elif not os.access(
            workspace,
            os.R_OK,
        ):

            valid = False
            validation_message = (
                f"Configured workspace is not readable: {workspace}"
            )

        elif not os.access(
            workspace,
            os.W_OK,
        ):

            valid = False
            validation_message = (
                f"Configured workspace is not writable: {workspace}"
            )

        # -------------------------------------------------------------
        # Validation successful.
        # -------------------------------------------------------------

        if valid:

            self._workspace = workspace

            logger.debug(
                "Workspace validated."
            )

            return

        # -------------------------------------------------------------
        # Validation failed.
        # -------------------------------------------------------------

        logger.warning(
            validation_message
        )

        self._select_workspace(
            validation_message,
        )

    # -----------------------------------------------------------------
    # Discover Projects
    # -----------------------------------------------------------------

    def _discover_projects(self) -> None:
        """
        Discover available projects in the workspace.
        """
        logger.debug(
        "Discovering available projects."
        )
        pass


    # -----------------------------------------------------------------
    # Present Project Selection
    # -----------------------------------------------------------------

    def _present_project_selection(self) -> None:
        """
        Present the available projects to the user.
        """
        logger.debug(
        "Presenting project selection."
        )
        pass

    # -----------------------------------------------------------------
    # Select Workspace
    # -----------------------------------------------------------------

    def _select_workspace(
        self,
        message: str,
        ) -> Path | None:
        """
        Request that the user selects a workspace.

        Parameters
        ----------
        message
            Explanation presented to the user describing why a new
            workspace must be selected.

        Returns
        -------
        Path
            The directory selected by the user.

        None
            The user cancelled the selection.
        """

        logger.debug(
            "Selecting workspace."
        )

        self._window_manager.user_interaction(
            title="Workspace Required",
            message=message,
        )

        return self._window_manager.select_directory(
            title="Select Workspace",
        )
        
# ============================================================================
# Standalone test harness
# ============================================================================

if __name__ == "__main__":

    configure_logging(
        level=logging.DEBUG,
        console_logging=True,
    )

    orchestrator = Orchestrator()

    orchestrator.startup()

    print(
        f"Current State : {orchestrator.state.name}"
    )
