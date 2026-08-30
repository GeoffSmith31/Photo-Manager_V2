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
Photo Manager Finalise Activity

Purpose
-------
Provides the Control Tower Activity widget used to display progress
while a project is being finalised.

Responsibilities
----------------
- Display the current Finalise stage.
- Display completed Finalise stages.
- Display the current activity message.
- Display progress through a multi-item operation.
- Display the current filename where applicable.

Notes
-----
This widget contains presentation logic only.

It does not perform filesystem operations and does not contain
Finalise workflow logic.

The Orchestrator controls the Finalise workflow and updates this
widget through the Window Manager.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QProgressBar,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from photo_manager.finalise import FinaliseStage

# ---------------------------------------------------------------------
# Finalise Stages
# ---------------------------------------------------------------------

FINALISE_STAGES = (
    "Checking project",
    "Checking project photos",
    "Selecting destination",
    "Validating destination",
    "Analysing filenames",
    "Resolving filename conflicts",
    "Copying photos",
    "Verifying copied photos",
    "Removing project files",
    "Removing source photos",
    "Completing Finalise",
)


# ---------------------------------------------------------------------
# Finalise Activity
# ---------------------------------------------------------------------

class FinaliseActivity(QWidget):
    """
    Display progress during project finalisation.
    """

    # -----------------------------------------------------------------
    # Constructor
    # -----------------------------------------------------------------

    def __init__(self) -> None:
        """
        Initialise the Finalise Activity.
        """

        super().__init__()

        self._stage_labels: list[QLabel] = []

        self._current_stage: FinaliseStage | None = None

        self._create_ui()

    # -----------------------------------------------------------------
    # Create UI
    # -----------------------------------------------------------------

    def _create_ui(self) -> None:
        """
        Create the Finalise Activity user interface.
        """

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            16,
            16,
            16,
            16,
        )

        layout.setSpacing(
            8
        )

        # -------------------------------------------------------------
        # Activity Message
        # -------------------------------------------------------------

        self._activity_message = QLabel(
            "Preparing Finalise..."
        )

        self._activity_message.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self._activity_message.setWordWrap(
            True
        )

        self._activity_message.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        layout.addWidget(
            self._activity_message,
            0,
        )

        # -------------------------------------------------------------
        # Current File
        # -------------------------------------------------------------

        self._current_file = QLabel(
            ""
        )

        self._current_file.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self._current_file.setWordWrap(
            True
        )

        layout.addWidget(
            self._current_file,
            0,
        )

        # -------------------------------------------------------------
        # Progress Text
        # -------------------------------------------------------------

        self._progress_text = QLabel(
            ""
        )

        self._progress_text.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            self._progress_text,
            0,
        )

        # -------------------------------------------------------------
        # Progress Bar
        # -------------------------------------------------------------

        self._progress_bar = QProgressBar()

        self._progress_bar.setRange(
            0,
            100,
        )

        self._progress_bar.setValue(
            0
        )

        self._progress_bar.setTextVisible(
            True
        )

        layout.addWidget(
            self._progress_bar,
            0,
        )

        # -------------------------------------------------------------
        # Stage Panel
        # -------------------------------------------------------------

        stage_panel = QFrame()

        stage_panel.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        stage_panel.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        stage_layout = QVBoxLayout(
            stage_panel
        )

        stage_layout.setContentsMargins(
            12,
            12,
            12,
            12,
        )

        stage_layout.setSpacing(
            4
        )

        for stage in FINALISE_STAGES:

            label = QLabel(
                f"○ {stage}"
            )

            label.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Preferred,
            )

            stage_layout.addWidget(
                label
            )

            self._stage_labels.append(
                label
            )

        stage_layout.addStretch()

        layout.addWidget(
            stage_panel,
            1,
        )

    # -----------------------------------------------------------------
    # Set Stage
    # -----------------------------------------------------------------

    def set_stage(
        self,
        stage: FinaliseStage,
    ) -> None:
        """
        Set the currently active Finalise stage.
        """

        self._current_stage = stage

        stages = list(
            FinaliseStage
        )

        current_index = stages.index(
            stage
        )

        for index, label in enumerate(
            self._stage_labels
        ):

            if index < current_index:

                label.setText(
                    f"✓ {FINALISE_STAGES[index]}"
                )

            elif index == current_index:

                label.setText(
                    f"● {FINALISE_STAGES[index]}"
                )

            else:

                label.setText(
                    f"○ {FINALISE_STAGES[index]}"
                )
    # -----------------------------------------------------------------
    # Complete Stage
    # -----------------------------------------------------------------

    def complete_stage(
        self,
        stage: FinaliseStage,
    ) -> None:
        """
        Mark a Finalise stage as completed.
        """

        stages = list(
            FinaliseStage
        )

        stage_index = stages.index(
            stage
        )

        self._stage_labels[
            stage_index
        ].setText(
            f"✓ {FINALISE_STAGES[stage_index]}"
        )

    # -----------------------------------------------------------------
    # Set Message
    # -----------------------------------------------------------------

    def set_message(
        self,
        message: str,
    ) -> None:
        """
        Set the current Finalise activity message.
        """

        self._activity_message.setText(
            message
        )

    # -----------------------------------------------------------------
    # Set Current File
    # -----------------------------------------------------------------

    def set_current_file(
        self,
        filename: str | None,
    ) -> None:
        """
        Display the filename currently being processed.
        """

        if filename:

            self._current_file.setText(
                f"Current file: {filename}"
            )

        else:

            self._current_file.clear()

    # -----------------------------------------------------------------
    # Set Progress
    # -----------------------------------------------------------------

    def set_progress(
        self,
        current: int,
        total: int,
    ) -> None:
        """
        Display progress through a multi-item operation.
        """

        if total <= 0:

            self._progress_text.clear()

            self._progress_bar.setValue(
                0
            )

            return

        current = max(
            0,
            min(
                current,
                total,
            ),
        )

        percentage = int(
            current * 100 / total
        )

        self._progress_text.setText(
            f"{current} / {total}"
        )

        self._progress_bar.setValue(
            percentage
        )

    # -----------------------------------------------------------------
    # Clear Progress
    # -----------------------------------------------------------------

    def clear_progress(self) -> None:
        """
        Clear the current progress information.
        """

        self._progress_text.clear()

        self._progress_bar.setValue(
            0
        )

        self._current_file.clear()
        
# ---------------------------------------------------------------------
# Standalone Test Harness
# ---------------------------------------------------------------------

if __name__ == "__main__":

    import sys

    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication

    application = QApplication(
        sys.argv
    )

    activity = FinaliseActivity()

    activity.setWindowTitle(
        "Finalise Activity Test"
    )

    activity.resize(
        600,
        700,
    )

    activity.show()

    def stage_1() -> None:

        activity.set_stage(
            FinaliseStage.CHECKING_PROJECT
        )

        activity.set_message(
            "Checking project files..."
        )

        QTimer.singleShot(
            1000,
            stage_2,
        )

    def stage_2() -> None:

        activity.set_stage(
            FinaliseStage.CHECKING_PHOTOS
        )

        activity.set_message(
            "Checking project photos..."
        )

        QTimer.singleShot(
            1000,
            stage_3,
        )

    def stage_3() -> None:

        activity.set_stage(
            FinaliseStage.COPYING_PHOTOS
        )

        activity.set_message(
            "Copying photos..."
        )

        activity.set_current_file(
            "IMG001.jpg"
        )

        activity.set_progress(
            1,
            10,
        )

        QTimer.singleShot(
            500,
            stage_4,
        )

    def stage_4() -> None:

        activity.set_current_file(
            "IMG002.jpg"
        )

        activity.set_progress(
            2,
            10,
        )

        QTimer.singleShot(
            500,
            stage_5,
        )

    def stage_5() -> None:

        activity.set_current_file(
            "IMG003.jpg"
        )

        activity.set_progress(
            3,
            10,
        )

        QTimer.singleShot(
            1000,
            stage_6,
        )

    def stage_6() -> None:

        activity.set_stage(
            FinaliseStage.VERIFYING_COPIES
        )

        activity.set_message(
            "Verifying copied photos..."
        )

        activity.clear_progress()

        QTimer.singleShot(
            1500,
            stage_7,
        )

    def stage_7() -> None:

        activity.set_stage(
            FinaliseStage.REMOVING_PROJECT_FILES
        )

        activity.set_message(
            "Removing project files..."
        )

        QTimer.singleShot(
            1000,
            stage_8,
        )

    def stage_8() -> None:

        activity.set_stage(
            FinaliseStage.COMPLETING
        )

        activity.set_message(
            "Finalise complete."
        )

    QTimer.singleShot(
        0,
        stage_1,
    )

    application.exec()
