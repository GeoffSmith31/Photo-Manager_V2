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
    QUrl,
    QRect,
    QTimer,
)
from PySide6.QtGui import (
    QDesktopServices,
)
from photo_manager.settings_dialog import SettingsDialog
from photo_manager.control_tower import ControlTower
from photo_manager.stage_status import StageStatus
from photo_manager.workflow_stage import WorkflowStage
from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
)
from photo_manager.project_selection import (
    ProjectSelectionRecord,
)
from photo_manager.constants import (
    CONTROL_TOWER_DEFAULT_HEIGHT,
    CONTROL_TOWER_DEFAULT_WIDTH,
    CONTROL_TOWER_MINIMUM_HEIGHT,
    CONTROL_TOWER_MINIMUM_WIDTH,
    HELP_URL,
    )
from photo_manager.multi_os import (
    find_supported_browser,
    launch_browser,
)
from photo_manager.logging import (
    configure_logging,
    get_logger,
)
from photo_manager.project import (
    MetadataPolicies,
)
from photo_manager.propagation_settings_dialog import (
    PropagationSettingsDialog,
)
from photo_manager.settings import Settings

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
        
        self._maps_process = None
        
        self._maps_browser = (
            find_supported_browser()
        )

        if self._maps_browser is not None:

            logger.info(
                "Maps browser selected: %s (%s).",
                self._maps_browser["name"],
                self._maps_browser["executable"],
            )

        else:

            logger.info(
                "No supported web browser available for Maps."
            )

        self._control_tower_screen = None

        self._discover_screens()

        self._control_tower = ControlTower()
        
        self._project_selected_callback = None
        self._action_requested_callback = None

        self._control_tower.project_selected.connect(
            self._handle_project_selected
        )

        self._control_tower.action_requested.connect(
            self._handle_action_requested
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
    # Show Application Settings
    # -------------------------------------------------------------

    def show_settings(
        self,
        settings: Settings,
        workspace_editable: bool,
    ) -> Settings | None:
        """
        Display the Application Settings dialog.

        Returns the selected Settings when OK is pressed,
        or None when the dialog is cancelled.
        """

        logger.debug(
            "Presenting Application Settings dialog."
        )

        dialog = SettingsDialog(
            settings,
            workspace_editable,
            self._control_tower,
        )

        if dialog.exec():

            logger.debug(
                "Application Settings dialog accepted."
            )

            return dialog.settings()

        logger.debug(
            "Application Settings dialog cancelled."
        )

        return None

    # -------------------------------------------------------------
    # Show Propagation Settings
    # -------------------------------------------------------------

    def show_propagation_settings(
        self,
        metadata_policies: MetadataPolicies,
    ) -> MetadataPolicies | None:
        """
        Display the Propagation Settings dialog.

        Returns
        -------
        MetadataPolicies
            The settings selected by the user when OK is pressed.

        None
            The user cancelled the dialog.
        """

        logger.debug(
            "Presenting Propagation Settings dialog."
        )

        dialog = PropagationSettingsDialog(
            metadata_policies,
            self._control_tower,
        )

        if dialog.exec():

            logger.debug(
                "Propagation Settings dialog accepted."
            )

            return dialog.metadata_policies()

        logger.debug(
            "Propagation Settings dialog cancelled."
        )

        return None

    # -------------------------------------------------------------
    # Close Google Maps
    # -------------------------------------------------------------

    def close_google_maps(
        self,
    ) -> None:
        """
        Close the Google Maps browser opened by Photo Manager.

        Closing an already-closed browser is treated as a normal
        condition.
        """

        if self._maps_process is None:
            return

        if self._maps_process.poll() is None:

            logger.debug(
                "Closing Google Maps browser."
            )

            self._maps_process.terminate()

        else:

            logger.debug(
                "Google Maps browser is already closed."
            )

        self._maps_process = None

    # -------------------------------------------------------------
    # Show Google Maps
    # -------------------------------------------------------------

    def show_google_maps(
        self,
        latitude: float,
        longitude: float,
    ) -> None:
        """
        Open the supplied coordinates in Google Maps.

        Photo Manager opens a dedicated browser window for the
        current photo. The browser is closed when Window Manager
        subsequently presents another Activity.
        """

        if self._maps_browser is None:

            logger.warning(
                "Cannot open Google Maps: "
                "no supported web browser is available."
            )

            self.user_interaction(
                "Unable to Open Maps",
                (
                    "No supported web browser is installed.\n\n"
                    "Google Maps cannot be opened."
                ),
            )

            return

        # ---------------------------------------------------------
        # Remove stale process reference
        # ---------------------------------------------------------

        if self._maps_process is not None:

            if self._maps_process.poll() is not None:

                logger.debug(
                    "Previous Google Maps browser "
                    "has already closed."
                )

                self._maps_process = None

            else:

                logger.debug(
                    "Google Maps browser is already running."
                )

                return

        # ---------------------------------------------------------
        # Build Google Maps URL
        # ---------------------------------------------------------

        url = (
            "https://www.google.com/maps/place/"
            f"{latitude},{longitude}"
        )

        logger.debug(
            "Opening Google Maps: %s",
            url,
        )

        # ---------------------------------------------------------
        # Launch browser
        # ---------------------------------------------------------

        try:

            self._maps_process = launch_browser(
                self._maps_browser,
                url,
            )

            logger.debug(
                "Google Maps browser launched: %s (PID %d).",
                self._maps_browser["name"],
                self._maps_process.pid,
            )

        except (
            OSError,
            ValueError,
        ) as error:

            logger.error(
                "Unable to launch Google Maps browser: %s",
                error,
            )

            self._maps_process = None

            self.user_interaction(
                "Unable to Open Maps",
                (
                    "The web browser could not be opened.\n\n"
                    "Google Maps cannot be displayed."
                ),
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
    # Set Action Requested Callback
    # -------------------------------------------------------------

    def set_action_requested_callback(
        self,
        callback,
    ) -> None:
        """
        Set the callback invoked when the user requests an action.
        """

        self._action_requested_callback = callback

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
    # Handle Action Requested
    # -------------------------------------------------------------

    def _handle_action_requested(
        self,
        action: str,
        payload,
    ) -> None:
        """
        Forward a requested user action to the application.
        """

        if self._action_requested_callback is not None:

            self._action_requested_callback(
                action,
                payload,
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

        self._control_tower.set_workflow_actions(
            stage,
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

        dialog = QMessageBox(
            self._control_tower
        )

        dialog.setIcon(
            QMessageBox.Warning
        )

        dialog.setWindowTitle(
            title
        )

        dialog.setText(
            message
        )

        dialog.setStandardButtons(
            QMessageBox.Ok
        )

        dialog.exec()

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
        self.close_google_maps()
        self.clear_activity()
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
    # Show Help
    # -------------------------------------------------------------

    def show_help(
        self,
    ) -> None:
        """
        Open the Photo Manager Help website in the user's
        default web browser.
        """

        logger.debug(
            "Opening Photo Manager Help."
        )

        QDesktopServices.openUrl(
            QUrl(HELP_URL)
        )

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
        find_criterion: str | None = None,
        find_text: str | None = None,
    ) -> None:
        """
        Present the Editor Activity to the user.
        """
        self.close_google_maps()

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
            find_criterion=find_criterion,
            find_text=find_text,
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

    # -------------------------------------------------------------
    # Confirm Shutdown
    # -------------------------------------------------------------

    def confirm_shutdown(
        self,
    ) -> bool:
        """
        Ask the user to confirm application shutdown.

        Returns True when the user chooses Yes.
        """

        logger.info(
            "Requesting shutdown confirmation."
        )

        dialog = QMessageBox(
            self._control_tower
        )

        dialog.setIcon(
            QMessageBox.Question
        )

        dialog.setWindowTitle(
            "Close Photo Manager"
        )

        dialog.setText(
            "Are you sure you want to close Photo Manager?"
        )

        dialog.setStandardButtons(
            QMessageBox.Yes
            | QMessageBox.No
        )

        dialog.setDefaultButton(
            QMessageBox.No
        )

        return (
            dialog.exec()
            == QMessageBox.Yes
        )

    # -------------------------------------------------------------
    # Shutdown
    # -------------------------------------------------------------

    def shutdown(
        self,
    ) -> None:
        """
        Release Window Manager resources during application shutdown.
        """

        logger.debug(
            "Window Manager shutdown."
        )

        self.close_google_maps()

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
