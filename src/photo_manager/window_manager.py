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
import sys
from PySide6.QtCore import (
    QRect,
    QTimer,
)
from photo_manager.control_tower import ControlTower
from photo_manager.stage_status import StageStatus
from photo_manager.workflow_stage import WorkflowStage
from PySide6.QtWidgets import QApplication
from photo_manager.project_selection import (
    ProjectSelectionRecord,
)
from photo_manager.constants import (
    CONTROL_TOWER_DEFAULT_HEIGHT,
    CONTROL_TOWER_DEFAULT_WIDTH,
    CONTROL_TOWER_MINIMUM_HEIGHT,
    CONTROL_TOWER_MINIMUM_WIDTH,
    )

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

        self._screens = []

        self._control_tower_screen = None

        self._discover_screens()

        self._control_tower = ControlTower()
        
        self._project_selected_callback = None

        self._control_tower.project_selected.connect(
            self._handle_project_selected
        )
    # -------------------------------------------------------------
    # Discover Screens
    # -------------------------------------------------------------

    def _discover_screens(self) -> None:
        """
        Discover the available display screens.
        """

        logger.debug(
            "Discovering available screens."
        )

        application = QApplication.instance()

        if application is None:

            raise RuntimeError(
                "QApplication has not been created."
            )

        self._screens = application.screens()

        logger.info(
            "Available screens: %d",
            len(self._screens),
        )

        for index, screen in enumerate(self._screens):

            geometry = screen.availableGeometry()

            logger.debug(
                "Screen %d: %s (%dx%d at %d,%d)",
                index,
                screen.name(),
                geometry.width(),
                geometry.height(),
                geometry.x(),
                geometry.y(),
            )

        self._control_tower_screen = (
            application.primaryScreen()
        )

        if self._control_tower_screen is None:

            raise RuntimeError(
                "No primary screen is available."
            )

        logger.info(
            "Control Tower screen: %s",
            self._control_tower_screen.name(),
        )

    # -------------------------------------------------------------
    # Set Project Selection Callback
    # -------------------------------------------------------------

    def set_project_selected_callback(
        self,
        callback,
    ) -> None:
        """
        Set the callback invoked when the user selects a project.
        """

        self._project_selected_callback = callback
        
    # -------------------------------------------------------------
    # Handle Project Selection
    # -------------------------------------------------------------

    def _handle_project_selected(
        self,
        index: int,
    ) -> None:
        """
        Forward the selected project index to the application.
        """

        if self._project_selected_callback is not None:

            self._project_selected_callback(
                index
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

        self._control_tower.set_status_message(
            message
        )      
    # -------------------------------------------------------------
    # Set Workflow Stage Status
    # -------------------------------------------------------------

    def set_workflow_stage_status(
        self,
        stage: WorkflowStage,
        status: StageStatus,
    ) -> None:
        """
        Set the displayed status of a Workflow Stage.

        The Window Manager provides the interface between the
        application workflow and the Control Tower GUI.
        """

        logger.debug(
            "Setting Workflow Stage status: %s -> %s",
            stage.name,
            status.name,
        )

        self._control_tower.set_workflow_stage_status(
            stage,
            status,
        )

    # -------------------------------------------------------------
    # Set Workflow Stage Result
    # -------------------------------------------------------------

    def set_workflow_stage_result(
        self,
        stage: WorkflowStage,
        result: str,
    ) -> None:
        """
        Set the displayed result of a Workflow Stage.

        The Window Manager provides the interface between the
        application workflow and the Control Tower GUI.
        """

        logger.debug(
            "Setting Workflow Stage result: %s -> %s",
            stage.name,
            result,
        )

        self._control_tower.set_workflow_stage_result(
            stage,
            result,
        )

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

    # -------------------------------------------------------------
    # Present Project Selection
    # -------------------------------------------------------------

    def present_project_selection(
        self,
        project_records: list[ProjectSelectionRecord],
    ) -> None:
        """
        Present the available projects to the user.

        The Orchestrator supplies the project records in the required
        presentation order. The Window Manager passes them to the
        Control Tower for display.
        """

        logger.debug(
            "Presenting %d project selection records.",
            len(project_records),
        )
        
        self._control_tower.set_activity_title(
            "PROJECT SELECTION"
        )

        self._control_tower.set_project_selection(
            project_records
        )

    # -------------------------------------------------------------
    # Clear Activity
    # -------------------------------------------------------------

    def clear_activity(self) -> None:
        """
        Clear the current activity from the Control Tower.
        """

        logger.debug(
            "Clearing current Activity."
        )

        self._control_tower.clear_activity()

    # -------------------------------------------------------------
    # Present Editor Activity
    # -------------------------------------------------------------

    def present_editor_activity(
        self,
        image_path: Path,
        event: str,
        year: str,
        location: str,
        info: str,
        photo_number: int,
        total_photos: int,
        maps_available: bool,
    ) -> None:
        """
        Present the Editor Activity to the user.
        """

        logger.debug(
            "Presenting Editor Activity."
        )

        self._control_tower.set_activity_title(
            "PHOTO EDITOR"
        )

        self._control_tower.set_editor_activity(
            image_path=image_path,
            event=event,
            year=year,
            location=location,
            info=info,
            photo_number=photo_number,
            total_photos=total_photos,
            maps_available=maps_available,
        )

    # -------------------------------------------------------------
    # Show Control Tower
    # -------------------------------------------------------------

    def show_control_tower(
        self,
        width: int | None = None,
        height: int | None = None,
        x: int | None = None,
        y: int | None = None,
    ) -> None:
        """
        Display the Control Tower window.

        Optional geometry may be supplied. Invalid or missing
        geometry is replaced with appropriate defaults.
        """

        self._set_control_tower_geometry(
            width=width,
            height=height,
            x=x,
            y=y,
        )

        self._control_tower.show()
        
    # -------------------------------------------------------------
    # Set Control Tower Geometry
    # -------------------------------------------------------------

    def _set_control_tower_geometry(
        self,
        width: int | None = None,
        height: int | None = None,
        x: int | None = None,
        y: int | None = None,
    ) -> None:
        """
        Set the Control Tower size and position.

        If no size or position is supplied, default geometry is used.

        Supplied size and position values are validated against the
        current screen configuration. Invalid values are replaced
        with appropriate defaults.
        """

        logger.debug(
            "Setting Control Tower geometry."
        )

        # ---------------------------------------------------------
        # Determine Size
        # ---------------------------------------------------------

        size_valid = (
            width is not None
            and height is not None
            and width >= CONTROL_TOWER_MINIMUM_WIDTH
            and height >= CONTROL_TOWER_MINIMUM_HEIGHT
        )

        if size_valid:

            size_valid = any(
                width <= screen.availableGeometry().width()
                and height <= screen.availableGeometry().height()
                for screen in self._screens
            )

        if not size_valid:

            logger.debug(
                "Using default Control Tower size: %dx%d",
                CONTROL_TOWER_DEFAULT_WIDTH,
                CONTROL_TOWER_DEFAULT_HEIGHT,
            )

            width = CONTROL_TOWER_DEFAULT_WIDTH
            height = CONTROL_TOWER_DEFAULT_HEIGHT

        else:

            logger.debug(
                "Using supplied Control Tower size: %dx%d",
                width,
                height,
            )

        # ---------------------------------------------------------
        # Determine Position
        # ---------------------------------------------------------

        position_valid = (
            x is not None
            and y is not None
        )

        if position_valid:

            window_rect = QRect(
                x,
                y,
                width,
                height,
            )

            position_valid = any(
                screen.availableGeometry().intersects(
                    window_rect
                )
                for screen in self._screens
            )

        if not position_valid:

            logger.debug(
                "Using default Control Tower position."
            )

            screen_geometry = (
                self._control_tower_screen.availableGeometry()
            )

            x = (
                screen_geometry.x()
                + (
                    screen_geometry.width()
                    - width
                ) // 2
            )

            y = (
                screen_geometry.y()
                + (
                    screen_geometry.height()
                    - height
                ) // 2
            )

        else:

            logger.debug(
                "Using supplied Control Tower position: %d,%d",
                x,
                y,
            )

        # ---------------------------------------------------------
        # Apply Geometry
        # ---------------------------------------------------------

        self._control_tower.setGeometry(
            x,
            y,
            width,
            height,
        )

        logger.debug(
            "Control Tower geometry set: %dx%d at %d,%d",
            width,
            height,
            x,
            y,
        )

# ============================================================================
# Standalone Test Harness
# ============================================================================

if __name__ == "__main__":

    configure_logging(
        level=logging.DEBUG,
        console_logging=True,
    )

    application = QApplication(
        sys.argv
    )

    windows = WindowManager()
    
    test_records = [
        ProjectSelectionRecord(
            project_name="New Project",
            is_new_project=True,
        ),
        ProjectSelectionRecord(
            project_name="Test Project",
        ),
    ]
    
    # -------------------------------------------------------------
    # Test Sequence
    # -------------------------------------------------------------

    def test_project_selection() -> None:

        logger.info(
            "TEST 1: Project selection."
        )

        windows.present_project_selection(
            test_records
        )

    def test_geometry() -> None:

        logger.info(
            "TEST 1: Default geometry."
        )

        windows.show_control_tower()

        QTimer.singleShot(
            3000,
            test_valid_geometry,
        )

    def test_valid_geometry() -> None:

        logger.info(
            "TEST 2: Valid supplied geometry."
        )

        windows.show_control_tower(
            width=1000,
            height=700,
            x=100,
            y=100,
        )

        QTimer.singleShot(
            3000,
            test_invalid_size,
        )

    def test_invalid_size() -> None:

        logger.info(
            "TEST 3: Invalid size."
        )

        windows.show_control_tower(
            width=400,
            height=300,
        )

        QTimer.singleShot(
            3000,
            test_invalid_position,
        )

    def test_invalid_position() -> None:

        logger.info(
            "TEST 4: Invalid position."
        )

        windows.show_control_tower(
            width=1000,
            height=700,
            x=10000,
            y=10000,
        )

    # -------------------------------------------------------------
    # Start Test Sequence
    # -------------------------------------------------------------

    QTimer.singleShot(
        0,
        test_geometry,
    )

    # -------------------------------------------------------------
    # Start Qt Event Loop
    # -------------------------------------------------------------

    application.exec()
