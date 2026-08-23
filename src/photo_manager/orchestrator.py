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
import sys
from PySide6.QtWidgets import QApplication
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
import argparse
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
from photo_manager.constants import (
    APPLICATION_LOG_DIRECTORY,
)
from photo_manager.project import (
    MetadataPolicies,
    discover_available_projects,
    get_project_global,
    get_registration_status,
    get_download_status,
    get_photo_availability,
    get_photo_edit_data,
)
from photo_manager.project_selection import (
    ProjectSelectionRecord,
)
from photo_manager.stage_status import StageStatus
from photo_manager.workflow_stage import WorkflowStage
from photo_manager.window_manager import WindowManager

logger = get_logger("Orchestrator")

# ---------------------------------------------------------------------
# Project Global Data
# ---------------------------------------------------------------------

@dataclass
class ProjectGlobal:
    """
    Project-level information retained by the Orchestrator
    while a project is open.
    """

    photo_count: int
    metadata_policies: MetadataPolicies
    source: str
    source_title: str
    current_photo: int

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

    def __init__(
        self,
        settings: Settings,
    ):
        """
        Initialise the Orchestrator.
        """

        # Current application state.
        self._state = ApplicationState.STARTING

        # Previous application state.
        self._previous_state = ApplicationState.STARTING

        # Current application settings.
        self._settings = settings

        # Active workspace.
        self._workspace = None
        
        self._project_records = []
        
        self._window_manager = WindowManager()

        self._window_manager.set_project_selected_callback(
            self._project_selected
        )

        self._window_manager.set_action_requested_callback(
            self._action_requested
        )

        # Active project.
        self._project = None

        # Active importer.
        self._importer = None
        
        # Active project-level data.
        self._project_global = None

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

        The Orchestrator remains the authoritative source of the
        application state and informs the Window Manager when that
        state changes.
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

        # -------------------------------------------------------------
        # Initialisation
        # -------------------------------------------------------------

        self._window_manager.set_workflow_stage_status(
            WorkflowStage.INITIALISATION,
            StageStatus.IN_PROGRESS,
        )

        self._load_settings()

        # Ensures a valid workspace is available.
        # May request that the user selects one.

        self._validate_workspace()

        self._discover_projects()

        # -------------------------------------------------------------
        # Initialisation Complete
        # -------------------------------------------------------------

        self._window_manager.set_workflow_stage_status(
            WorkflowStage.INITIALISATION,
            StageStatus.COMPLETED,
        )

        self._window_manager.set_workflow_stage_result(
            WorkflowStage.INITIALISATION,
            "Success",
        )

        # -------------------------------------------------------------
        # Project Selection
        # -------------------------------------------------------------

        self._set_state(
            ApplicationState.PROJECT_SELECTION,
        )

        self._window_manager.set_workflow_stage_status(
            WorkflowStage.PROJECT_SELECTION,
            StageStatus.IN_PROGRESS,
        )
        
        self._window_manager.status_message(
            "Awaiting Project Selection"
        )

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
        Discover and prepare projects for Project Selection.
        """

        logger.debug(
            "Discovering available projects."
        )

        self._project_records = discover_available_projects(
            self._workspace
        )

        self._project_records.sort(
            key=lambda record: record.project_name.lower()
        )

        new_project = ProjectSelectionRecord(
            project_name="New Project",
            is_new_project=True,
        )

        self._project_records.insert(
            0,
            new_project,
        )


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

        self._window_manager.present_project_selection(
            self._project_records
        )

    # -----------------------------------------------------------------
    # Clear Project Global Data
    # -----------------------------------------------------------------

    def _clear_project_global(self) -> None:
        """
        Clear project-level data belonging to the previously
        active project.
        """

        self._project_global = None

    # -----------------------------------------------------------------
    # Project Selected
    # -----------------------------------------------------------------

    def _project_selected(
        self,
        index: int,
    ) -> None:
        """
        Handle a project selected by the user.
        """

        record = self._project_records[index]
        
        self._project = record
        
        # -------------------------------------------------------------
        # Clear any data belonging to the previously active project.
        # -------------------------------------------------------------

        self._clear_project_global()

        # -------------------------------------------------------------
        # Load project-level data for the newly selected project.
        # -------------------------------------------------------------

        (
            photo_count,
            metadata_policies,
            source,
            source_title,
        ) = get_project_global(
            record.project_json_path
        )

        self._project_global = ProjectGlobal(
            photo_count=photo_count,
            metadata_policies=metadata_policies,
            source=source,
            source_title=source_title,
            current_photo=0,
        )

        self._window_manager.set_workflow_stage_status(
            WorkflowStage.PROJECT_SELECTION,
            StageStatus.COMPLETED,
        )

        self._window_manager.set_workflow_stage_result(
            WorkflowStage.PROJECT_SELECTION,
            record.project_name,
        )
        
        self._window_manager.set_workflow_stage_status(
            WorkflowStage.SOURCE_SELECTION,
            StageStatus.COMPLETED,
        )

        self._window_manager.set_workflow_stage_result(
            WorkflowStage.SOURCE_SELECTION,
            f"{self._project_global.source} — "
            f"{self._project_global.source_title}",
        )

        logger.debug(
            "Project global data: photos=%s, metadata_policies=%s",
            self._project_global.photo_count,
            self._project_global.metadata_policies,
        )

        logger.debug(
            "Project selected: index=%s, name=%s, json=%s, "
            "image_folder=%s, thumbnail=%s, new_project=%s, valid=%s",
            index,
            record.project_name,
            record.project_json_path,
            record.image_folder,
            record.thumbnail_path,
            record.is_new_project,
            record.valid,
        )
        
        self._open_project()
    
    # -----------------------------------------------------------------
    # Open Project
    # -----------------------------------------------------------------

    def _open_project(self) -> None:
        """
        Open the selected project and follow the Open Project workflow.

        This is currently the architectural skeleton.  Processes that
        have not yet been implemented are represented by telltales and
        pass statements so that the complete workflow can be exercised.
        """
        logger.info(
            "Opening project: %s",
            self._project.project_name,
        )
        logger.info(
            "Opening project workflow."
        )

        # -------------------------------------------------------------
        # Receive Project Information
        # -------------------------------------------------------------

        logger.debug(
            "[OPEN PROJECT] Receive Project Information."
        )
        pass

        # -------------------------------------------------------------
        # Load Project Global Data
        # -------------------------------------------------------------

        logger.debug(
            "[OPEN PROJECT] Load Project Global Data."
        )
        pass

        # -------------------------------------------------------------
        # Registration Complete?
        # -------------------------------------------------------------

        registration_status = get_registration_status(
            self._project.project_json_path
        )

        registration_complete = (
            registration_status == "COMPLETE"
        )

        logger.debug(
            "[OPEN PROJECT] Registration complete: %s",
            registration_complete,
        )

        if not registration_complete:

            # ---------------------------------------------------------
            # Registration path — skeleton for now.
            # ---------------------------------------------------------

            logger.debug(
                "[STUB] Resume Registration."
            )
            pass

        # -------------------------------------------------------------
        # Acquisition Complete?
        # -------------------------------------------------------------

        download_status = get_download_status(
            self._project.project_json_path
        )

        download_complete = (
            download_status == "COMPLETE"
        )

        logger.debug(
            "[OPEN PROJECT] Acquisition complete: %s",
            download_complete,
        )

        if not download_complete:

            # ---------------------------------------------------------
            # Acquisition path — skeleton for now.
            # ---------------------------------------------------------

            logger.debug(
                "[STUB] Resume Acquisition."
            )
            pass

        # -------------------------------------------------------------
        # Auth System Open?
        # -------------------------------------------------------------

        auth_system_open = False

        logger.debug(
            "[OPEN PROJECT] Auth system open: %s",
            auth_system_open,
        )

        if auth_system_open:

            logger.debug(
                "[STUB] Close Auth System."
            )
            pass

        # -----------------------------------------------------------------
        # Complete Importing
        # -----------------------------------------------------------------

        registered, present = get_photo_availability(
            self._project.project_json_path
        )

        self._window_manager.set_workflow_stage_status(
            WorkflowStage.IMPORTING,
            StageStatus.COMPLETED,
        )

        self._window_manager.set_workflow_stage_result(
            WorkflowStage.IMPORTING,
            f"Reg: {registered}   Avail: {present}",
        )

        # -----------------------------------------------------------------
        # Enter Editing
        # -----------------------------------------------------------------

        self._set_state(
            ApplicationState.EDITING,
        )

        self._window_manager.set_workflow_stage_status(
            WorkflowStage.EDITING,
            StageStatus.IN_PROGRESS,
        )

        # -----------------------------------------------------------------
        # Clear Project Selection Activity
        # -----------------------------------------------------------------

        self._window_manager.clear_activity()

        # -------------------------------------------------------------
        # Open Photo
        # -------------------------------------------------------------

        logger.debug(
            "[OPEN PROJECT] Open Photo."
        )

        self._load_current_photo()
    
    # -----------------------------------------------------------------
    # Load Current Photo
    # -----------------------------------------------------------------

    def _load_current_photo(self) -> None:
        """
        Request the current photo's editing data from the
        Project Service.
        """

        if self._project is None:
            logger.error(
                "Cannot load photo: no active project."
            )
            raise RuntimeError(
                "Cannot load photo without an active project."
            )

        if self._project_global is None:
            logger.error(
                "Cannot load photo: no project global data."
            )
            raise RuntimeError(
                "Cannot load photo without project global data."
            )

        photo_edit_data = get_photo_edit_data(
            self._project.project_json_path,
            self._project_global.current_photo,
        )

        logger.debug(
            "Photo edit data: file=%s, event=%s, year=%s, "
            "location=%s, info=%s, has_coordinates=%s",
            photo_edit_data.file,
            photo_edit_data.event,
            photo_edit_data.year,
            photo_edit_data.location,
            photo_edit_data.info,
            photo_edit_data.has_coordinates,
        )

        # -------------------------------------------------------------
        # Present Editor Activity
        # -------------------------------------------------------------

        self._window_manager.present_editor_activity(
            image_path=photo_edit_data.file,
            event=photo_edit_data.event,
            year=photo_edit_data.year,
            location=photo_edit_data.location,
            info=photo_edit_data.info,
            photo_number=self._project_global.current_photo,
            total_photos=self._project_global.photo_count,
            maps_available=photo_edit_data.has_coordinates,
        )

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

    # -----------------------------------------------------------------
    # Action Requested
    # -----------------------------------------------------------------

    def _action_requested(
        self,
        action: str,
    ) -> None:
        """
        Handle an action requested by the user.

        The meaning of an action is determined by the
        current Orchestrator state.
        """

        logger.debug(
            "User action requested: %s",
            action,
        )

        if action == "Cancel":
            logger.info(
                "Cancel requested."
            )

        elif action == "Retry":
            logger.info(
                "Retry requested."
            )

        elif action == "Change Project":
            logger.info(
                "Change Project requested."
            )

        elif action == "Finalise":
            logger.info(
                "Finalise requested."
            )

        elif action == "Back":
            self._navigate_back()

        elif action == "Forward":
            self._navigate_forward()
            
        elif action.startswith("Goto:"):
            requested_photo = action[5:]

            self._goto_photo(
                requested_photo
            )
            
    # -----------------------------------------------------------------
    # Editor Navigation
    # -----------------------------------------------------------------

    def _navigate_back(self) -> None:
        """
        Move to the previous photo in the active project.
        """

        if self._project_global is None:
            logger.error(
                "Cannot navigate back: no project is active."
            )
            return

        if self._project_global.current_photo <= 0:
            logger.debug(
                "Back requested at first photo; ignoring."
            )
            return

        self._project_global.current_photo -= 1

        logger.debug(
            "Navigating back to photo %s.",
            self._project_global.current_photo + 1,
        )

        self._window_manager.clear_activity()
        self._load_current_photo()

    # -----------------------------------------------------------------

    def _navigate_forward(self) -> None:
        """
        Move to the next photo in the active project.
        """

        if self._project_global is None:
            logger.error(
                "Cannot navigate forward: no project is active."
            )
            return

        last_photo = (
            self._project_global.photo_count - 1
        )

        if self._project_global.current_photo >= last_photo:
            logger.debug(
                "Forward requested at last photo; ignoring."
            )
            return

        self._project_global.current_photo += 1

        logger.debug(
            "Navigating forward to photo %s.",
            self._project_global.current_photo + 1,
        )

        self._window_manager.clear_activity()
        self._load_current_photo()

    # -----------------------------------------------------------------
    # Editor Goto
    # -----------------------------------------------------------------

    def _goto_photo(
        self,
        requested_photo: str,
    ) -> None:
        """
        Navigate to a photo specified by the user.
        """

        if self._project_global is None:
            logger.error(
                "Cannot goto photo: no project is active."
            )
            return

        try:
            photo_number = int(
                requested_photo
            )
        except ValueError:
            logger.debug(
                "Invalid GOTO value: %r",
                requested_photo,
            )
            return

        total_photos = (
            self._project_global.photo_count
        )

        if photo_number < 1 or photo_number > total_photos:
            logger.debug(
                "GOTO photo number out of range: %d "
                "(valid range 1-%d).",
                photo_number,
                total_photos,
            )
            return

        self._project_global.current_photo = (
            photo_number - 1
        )

        logger.debug(
            "Navigating to photo %d.",
            photo_number,
        )

        self._window_manager.clear_activity()

        self._load_current_photo()

# ============================================================================
# Standalone Test Harness
# ============================================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Photo Manager"
    )

    parser.add_argument(
        "--dev",
        action="store_true",
        help="Enable development logging.",
    )

    args = parser.parse_args()

    # -------------------------------------------------------------
    # Load application settings
    # -------------------------------------------------------------

    settings = load_settings()

    # -------------------------------------------------------------
    # Configure logging
    # -------------------------------------------------------------

    if args.dev:
        logging_level = logging.DEBUG
        console_logging = True
    else:
        logging_level = settings.logging_level
        console_logging = False

    configure_logging(
        level=logging_level,
        log_directory=APPLICATION_LOG_DIRECTORY,
        console_logging=console_logging,
    )

    application = QApplication(
        sys.argv
    )

    orchestrator = Orchestrator(
        settings=settings,
    )

    orchestrator._window_manager.show_control_tower()

    orchestrator.startup()

    # Existing test-harness code follows...
    
    logger.debug(
        "Project selection records:"
    )

    for index, record in enumerate(
        orchestrator._project_records
    ):
        logger.debug(
            "  [%s] name=%s, json=%s, image_folder=%s, "
            "thumbnail=%s, new_project=%s, valid=%s",
            index,
            record.project_name,
            record.project_json_path,
            record.image_folder,
            record.thumbnail_path,
            record.is_new_project,
            record.valid,
        )

    logger.debug(
        "Current state: %s",
        orchestrator.state.name,
    )

    application.exec()
