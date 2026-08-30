# =============================================================================
#
# Photo Manager
#
# Copyright (c) 2026 Geoff [dev.photomanager@gmail.com](mailto:dev.photomanager@gmail.com)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# =============================================================================

"""
Photo Manager Control Tower

## Purpose

Provides the main graphical user interface for Photo Manager.

## Responsibilities

- Display the application workflow.
- Display the current activity.
- Display application status information.
- Display available workflow actions.
- Provide a consistent responsive application layout.

## Notes

The Control Tower is a presentation component.

It does not contain application workflow logic.

The Window Manager controls what information is displayed
and monitors user interaction with the GUI.
"""

from pathlib import Path
from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from photo_manager.stage_status import StageStatus
from photo_manager.workflow_stage import WorkflowStage
from photo_manager.constants import (
    APPLICATION_NAME,
    CONTROL_TOWER_MINIMUM_HEIGHT,
    CONTROL_TOWER_MINIMUM_WIDTH,
)
from photo_manager.project_selection import (
    ProjectSelectionRecord,
)
from photo_manager.project_selection_widget import (
    ProjectSelectionWidget,
)

from photo_manager.editor_activity import EditorActivity
from photo_manager.finalise_activity import FinaliseActivity

# ---------------------------------------------------------------------
# Workflow Stage Panel
# ---------------------------------------------------------------------

class WorkflowStagePanel(QFrame):
    """
    Displays the user-facing state of a single Workflow Stage.
    """

    # -----------------------------------------------------------------
    # Constructor
    # -----------------------------------------------------------------

    def __init__(
        self,
        stage: WorkflowStage,
    ) -> None:
        """
        Initialise a Workflow Stage panel.
        """

        super().__init__()

        self._stage = stage

        self.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        self.setFixedHeight(
            72
        )

        self._build_interface()

    # -----------------------------------------------------------------
    # Build Interface
    # -----------------------------------------------------------------

    def _build_interface(self) -> None:
        """
        Construct the Workflow Stage panel.
        """

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            6,
            4,
            6,
            4,
        )

        layout.setSpacing(
            2
        )

        self._title_label = QLabel(
            self._stage.name.replace(
                "_",
                " ",
            )
        )

        self._title_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
        )

        self._status_label = QLabel()

        self._status_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
        )

        self._result_label = QLabel()

        self._result_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
        )

        self._result_label.setWordWrap(
            True
        )

        layout.addWidget(
            self._title_label,
            0,
        )

        layout.addWidget(
            self._status_label,
            0,
        )

        layout.addWidget(
            self._result_label,
            1,
        )

        self.set_status(
            StageStatus.PENDING
        )

    # -----------------------------------------------------------------
    # Set Status
    # -----------------------------------------------------------------

    def set_status(
        self,
        status: StageStatus,
    ) -> None:
        """
        Set the displayed Workflow Stage status.
        """

        status_display = {
            StageStatus.PENDING: (
                '<span style="color: black;">■</span> PENDING'
            ),
            StageStatus.IN_PROGRESS: (
                '<span style="color: blue;">▶</span> IN PROGRESS'
            ),
            StageStatus.COMPLETED: (
                '<span style="color: green;">●</span> COMPLETED'
            ),
            StageStatus.ERROR: (
                '<span style="color: red;">!</span> ERROR'
            ),
        }

        self._status_label.setText(
            status_display[status]
        )

    # -----------------------------------------------------------------
    # Set Result
    # -----------------------------------------------------------------

    def set_result(
        self,
        result: str,
    ) -> None:
        """
        Set the displayed Workflow Stage result.
        """

        self._result_label.setText(
            result
        )


# ---------------------------------------------------------------------
# Control Tower
# -----------------------------------------------python -m photo_manager.project_selection_widget----------------------

class ControlTower(QMainWindow):
    """
    Main Photo Manager application window.
    """
    project_selected = Signal(int)
    action_requested = Signal(str, object)
    
    # -----------------------------------------------------------------
    # Constructor
    # -----------------------------------------------------------------

    def __init__(self) -> None:
        """
        Initialise the Control Tower window.
        """
      
        super().__init__()

        self.setWindowTitle(
            APPLICATION_NAME
        )

        self.setMinimumSize(
            CONTROL_TOWER_MINIMUM_WIDTH,
            CONTROL_TOWER_MINIMUM_HEIGHT,
        )

        self._workflow_panels = {}

        self._build_interface()

    # -----------------------------------------------------------------
    # Build Interface
    # -----------------------------------------------------------------

    def _build_interface(self) -> None:
        """
        Construct the Control Tower interface.
        """

        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        main_layout = QVBoxLayout(
            central_widget
        )

        main_layout.setContentsMargins(
            8,
            8,
            8,
            8,
        )

        main_layout.setSpacing(
            8
        )

        # -------------------------------------------------------------
        # Main Content Area
        # -------------------------------------------------------------

        content_layout = QHBoxLayout()

        content_layout.setSpacing(
            8
        )

        main_layout.addLayout(
            content_layout,
            1,
        )

        # -------------------------------------------------------------
        # Workflow Panel
        # -------------------------------------------------------------

        workflow_panel = self._create_workflow_panel()

        content_layout.addWidget(
            workflow_panel,
            0,
        )

        # -------------------------------------------------------------
        # Activity Panel
        # -------------------------------------------------------------

        activity_panel = self._create_activity_panel()

        content_layout.addWidget(
            activity_panel,
            1,
        )

        # -------------------------------------------------------------
        # Status Display
        # -------------------------------------------------------------

        status_panel = self._create_status_panel()
        
        status_panel.setVisible(
            False
        )

        main_layout.addWidget(
            status_panel,
            0,
        )

        # -------------------------------------------------------------
        # Action Bar
        # -------------------------------------------------------------

        action_bar = self._create_action_bar()

        main_layout.addWidget(
            action_bar,
            0,
        )

    # -----------------------------------------------------------------
    # Create Workflow Panel
    # -----------------------------------------------------------------

    def _create_workflow_panel(self) -> QFrame:
        """
        Create the Workflow panel containing all workflow stages.
        """

        panel = QFrame()

        panel.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        panel.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding,
        )

        panel.setMinimumWidth(
            220
        )

        layout = QVBoxLayout(
            panel
        )

        layout.setContentsMargins(
            6,
            6,
            6,
            6,
        )

        layout.setSpacing(
            4
        )

        title = QLabel(
            "WORKFLOW"
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            title,
            0,
        )

        # -------------------------------------------------------------
        # Workflow Stage Panels
        # -------------------------------------------------------------

        for stage in WorkflowStage:

            stage_panel = self._create_workflow_stage(
                stage
            )

            self._workflow_panels[
                stage
            ] = stage_panel

            layout.addWidget(
                stage_panel,
                0,
            )
        
        layout.addStretch(
            1,
        )
        
        return panel

    # -----------------------------------------------------------------
    # Create Workflow Stage
    # -----------------------------------------------------------------

    def _create_workflow_stage(
        self,
        stage: WorkflowStage,
    ) -> WorkflowStagePanel:
        """
        Create an individual Workflow Stage panel.
        """

        return WorkflowStagePanel(
            stage
        )
        
    # -----------------------------------------------------------------
    # Set Workflow Stage Status
    # -----------------------------------------------------------------

    def _set_stage_status(
        self,
        label: QLabel,
        status: StageStatus,
    ) -> None:
        """
        Render a Workflow Stage status.
        """

        status_display = {
            StageStatus.PENDING: "■ PENDING",
            StageStatus.IN_PROGRESS: "▶ IN PROGRESS",
            StageStatus.COMPLETED: "● COMPLETED",
            StageStatus.ERROR: "! ERROR",
        }

        label.setText(
            status_display[status]
        )

    # -----------------------------------------------------------------
    # Set Workflow Stage Status
    # -----------------------------------------------------------------

    def set_workflow_stage_status(
        self,
        stage: WorkflowStage,
        status: StageStatus,
    ) -> None:
        """
        Set the displayed status of a Workflow Stage.
        """

        stage_panel = self._workflow_panels.get(
            stage
        )

        if stage_panel is None:
            return

        stage_panel.set_status(
            status
        )
        
    # -----------------------------------------------------------------
    # Set Workflow Stage Result
    # -----------------------------------------------------------------

    def set_workflow_stage_result(
        self,
        stage: WorkflowStage,
        result: str,
    ) -> None:
        """
        Set the displayed result or contextual information for
        a Workflow Stage.
        """

        stage_panel = self._workflow_panels.get(
            stage
        )

        if stage_panel is None:
            return

        stage_panel.set_result(
            result
        )
        
    # -----------------------------------------------------------------
    # Set Status Message
    # -----------------------------------------------------------------

    def set_status_message(
        self,
        message: str,
    ) -> None:
        """
        Set the message displayed in the Status Display.
        """

        self._status_message.setText(
            message
        )

    # -----------------------------------------------------------------
    # Set Project Selection
    # -----------------------------------------------------------------

    def set_project_selection(
        self,
        project_records: list[ProjectSelectionRecord],
    ) -> None:
        """
        Display the supplied project selection records.

        The records are supplied in presentation order by the
        Window Manager. The Control Tower only renders them.
        """

        project_selection_widget = ProjectSelectionWidget(
            project_records
        )

        project_selection_widget.project_selected.connect(
            self.project_selected.emit
        )

        self._activity_layout.addWidget(
            project_selection_widget,
            1,
        )

    # -----------------------------------------------------------------
    # Set Editor Activity
    # -----------------------------------------------------------------

    def set_editor_activity(
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
        Display the Editor Activity for the current photo.
        """

        editor_activity = EditorActivity()

        editor_activity.action_requested.connect(
            self.action_requested.emit
        )

        editor_activity.display_photo(
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

        self._activity_layout.addWidget(
            editor_activity,
            1,
        )
        editor_activity.focus_event_field()

    # -----------------------------------------------------------------
    # Set Finalise Activity
    # -----------------------------------------------------------------

    def set_finalise_activity(
        self,
        activity: FinaliseActivity,
    ) -> None:
        """
        Display the Finalise Activity.
        """

        self._activity_layout.addWidget(
            activity,
            1,
        )

    # -----------------------------------------------------------------
    # Create Activity Panel
    # -----------------------------------------------------------------

    def _create_activity_panel(self) -> QFrame:
        """
        Create the Activity panel.

        The Activity panel is initially empty and will later contain
        the widget associated with the current application activity.
        """

        panel = QFrame()

        panel.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        panel.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self._activity_layout = QVBoxLayout(
            panel
        )

        self._activity_layout.setContentsMargins(
            8,
            8,
            8,
            8,
        )

        self._activity_title = QLabel(
            "ACTIVITY"
        )

        self._activity_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self._activity_layout.addWidget(
            self._activity_title,
            0,
        )

        return panel
        
    # -----------------------------------------------------------------
    # Set Activity Title
    # -----------------------------------------------------------------      
    def set_activity_title(
        self,
        title: str,
    ) -> None:
        """
        Set the title displayed for the current activity.
        """

        self._activity_title.setText(
            title
        )      

    # -----------------------------------------------------------------
    # Clear Activity
    # -----------------------------------------------------------------

    def clear_activity(self) -> None:
        """
        Remove the current activity from the Activity panel.

        The Activity title is retained.

        Activity widgets are hidden and removed from the layout
        immediately. The widget objects are then scheduled for
        deletion.
        """

        while self._activity_layout.count() > 1:

            item = self._activity_layout.takeAt(1)

            widget = item.widget()

            if widget is not None:

                widget.hide()

                widget.setParent(
                    None
                )

                widget.deleteLater()

    # -----------------------------------------------------------------
    # Create Status Panel
    # -----------------------------------------------------------------

    def _create_status_panel(self) -> QFrame:
        """
        Create the application Status Display.
        """

        panel = QFrame()

        panel.setFixedHeight(
            32
        )

        panel.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )

        layout = QHBoxLayout(
            panel
        )

        layout.setContentsMargins(
            8,
            4,
            8,
            4,
        )

        label = QLabel(
            "Status:"
        )

        self._status_message = QLabel(
            ""
        )

        self._status_message.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        layout.addWidget(
            label,
            0,
        )

        layout.addWidget(
            self._status_message,
            1,
        )

        return panel

    # -----------------------------------------------------------------
    # Create Action Bar
    # -----------------------------------------------------------------

    def _create_action_bar(self) -> QFrame:
        """
        Create the Action Bar.

        No action buttons are displayed initially.
        """

        panel = QFrame()

        panel.setStyleSheet(
            "background-color: #f2f2f2f2;"
        )
        
        panel.setMinimumHeight(
            56
        )

        panel.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )

        panel.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        layout = QHBoxLayout(
            panel
        )

        layout.setContentsMargins(
            96,
            4,
            96,
            4,
        )

        # -------------------------------------------------------------
        # Left Action Area
        # -------------------------------------------------------------

        self._left_action_layout = QHBoxLayout()

        self._left_action_layout.setSpacing(
            6
        )

        layout.addLayout(
            self._left_action_layout,
            0,
        )

        # -------------------------------------------------------------
        # Left/Centre Spacer
        # -------------------------------------------------------------

        layout.addStretch(
            1,
        )

        # -------------------------------------------------------------
        # Centre Action Area
        # -------------------------------------------------------------

        self._centre_action_layout = QHBoxLayout()

        self._centre_action_layout.setSpacing(
            6
        )

        layout.addLayout(
            self._centre_action_layout,
            0,
        )

        # -------------------------------------------------------------
        # Centre/Right Spacer
        # -------------------------------------------------------------

        layout.addStretch(
            1,
        )

        # -------------------------------------------------------------
        # Right Action Area
        # -------------------------------------------------------------

        self._right_action_layout = QHBoxLayout()

        self._right_action_layout.setSpacing(
            6
        )

        layout.addLayout(
            self._right_action_layout,
            0,
        )

        return panel

    # -----------------------------------------------------------------
    # Set Workflow Actions
    # -----------------------------------------------------------------

    def set_workflow_actions(
        self,
        stage: WorkflowStage,
    ) -> None:
        """
        Display the common Action Bar controls appropriate to the
        current Workflow Stage.

        Cancel, Settings and Help are always available.
        Finalise becomes available once a project has been selected.
        Activity-specific controls are owned by the activity widget.
        """

        for action_layout in (
            self._left_action_layout,
            self._centre_action_layout,
            self._right_action_layout,
        ):
            while action_layout.count():
                item = action_layout.takeAt(0)
                widget = item.widget()

                if widget is not None:
                    widget.deleteLater()

        left_actions = ["Close"]
        centre_actions = ["Settings", "Help"]
        right_actions = []

        if stage not in (
            WorkflowStage.INITIALISATION,
            WorkflowStage.PROJECT_SELECTION,
            WorkflowStage.SOURCE_SELECTION,
        ):
            right_actions.append("Finalise")

        def add_action_button(
            action: str,
            layout: QHBoxLayout,
        ) -> None:

            button = QPushButton(action)

            button.clicked.connect(
                lambda checked=False, action=action:
                    self.action_requested.emit(
                        action,
                        None,
                    )
            )

            layout.addWidget(button)

        for action in left_actions:
            add_action_button(action, self._left_action_layout)

        for index, action in enumerate(centre_actions):

            add_action_button(
                action,
                self._centre_action_layout,
            )

            if index == 0:
                self._centre_action_layout.addSpacing(
                    200
                )

        for action in right_actions:
            add_action_button(action, self._right_action_layout)

# ============================================================================
# Standalone Test Harness
# ============================================================================

if __name__ == "__main__":

    import sys

    from PySide6.QtWidgets import QApplication

    application = QApplication(
        sys.argv
    )

    control_tower = ControlTower()
    
    control_tower.project_selected.connect(
        lambda index:
            print(
                f"Selected project index: {index}"
            )
    )    

    control_tower.set_workflow_actions(
#        WorkflowStage.PROJECT_SELECTION
        WorkflowStage.IMPORTING
#        WorkflowStage.EDITING
    )
    control_tower.show()

    sys.exit(
        application.exec()
    )
