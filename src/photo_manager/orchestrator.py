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
        
        self._project_records = []
        
        self._window_manager = WindowManager()

        self._window_manager.set_project_selected_callback(
            self._project_selected
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

        print()
        print("PROJECT GLOBAL DATA")
        print("-" * 72)
        print(
            f"Photo Count      : "
            f"{self._project_global.photo_count}"
        )
        print(
            f"Metadata Policies: "
            f"{self._project_global.metadata_policies}"
        )        

        print()
        print("=" * 72)
        print("PROJECT SELECTED")
        print("=" * 72)
        print()
        print(f"Index        : {index}")
        print(f"Project Name : {record.project_name}")
        print(f"Project JSON : {record.project_json_path}")
        print(f"Image Folder : {record.image_folder}")
        print(f"Thumbnail    : {record.thumbnail_path}")
        print(f"New Project  : {record.is_new_project}")
        print(f"Valid        : {record.valid}")
        
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
        print()
        print("=" * 72)
        print("OPEN PROJECT")
        print("=" * 72)

        # -------------------------------------------------------------
        # Receive Project Information
        # -------------------------------------------------------------

        print("[OPEN PROJECT] Receive Project Information")
        pass

        # -------------------------------------------------------------
        # Load Project Global Data
        # -------------------------------------------------------------

        print("[OPEN PROJECT] Load Project Global Data")
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

        print(
            f"[OPEN PROJECT] Registration Complete? "
            f"→ {'Y' if registration_complete else 'N'}"
        )

        if not registration_complete:

            # ---------------------------------------------------------
            # Registration path — skeleton for now.
            # ---------------------------------------------------------

            print("[STUB] Resume Registration")
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

        print(
            f"[OPEN PROJECT] Acquisition Complete? "
            f"→ {'Y' if download_complete else 'N'}"
        )

        if not download_complete:

            # ---------------------------------------------------------
            # Acquisition path — skeleton for now.
            # ---------------------------------------------------------

            print("[STUB] Resume Acquisition")
            pass

        # -------------------------------------------------------------
        # Auth System Open?
        # -------------------------------------------------------------

        auth_system_open = False

        print(
            f"[OPEN PROJECT] Auth System Open? "
            f"→ {'Y' if auth_system_open else 'N'}"
        )

        if auth_system_open:

            print("[STUB] Close Auth System")
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

        print("[OPEN PROJECT] Open Photo")

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

        print()
        print("PHOTO EDIT DATA")
        print("-" * 72)
        print(
            f"File             : "
            f"{photo_edit_data.file}"
        )
        print(
            f"Event            : "
            f"{photo_edit_data.event}"
        )
        print(
            f"Year             : "
            f"{photo_edit_data.year}"
        )
        print(
            f"Location         : "
            f"{photo_edit_data.location}"
        )
        print(
            f"Info             : "
            f"{photo_edit_data.info}"
        )
        print(
            f"Has Coordinates  : "
            f"{photo_edit_data.has_coordinates}"
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

    orchestrator = Orchestrator()

    orchestrator._window_manager.show_control_tower()

    orchestrator.startup()
    
    print()
    print("=" * 72)
    print("PROJECT SELECTION RECORDS")
    print("=" * 72)

    for index, record in enumerate(
        orchestrator._project_records
    ):
        print()
        print(f"[{index}]")
        print(f"  Project Name : {record.project_name}")
        print(f"  Project JSON : {record.project_json_path}")
        print(f"  Image Folder : {record.image_folder}")
        print(f"  Thumbnail    : {record.thumbnail_path}")
        print(f"  New Project  : {record.is_new_project}")
        print(f"  Valid        : {record.valid}")

    print(
        f"Current State : {orchestrator.state.name}"
    )

    application.exec()
