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
Photo Manager Settings Dialog

Provides the user interface for application-wide settings.
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from photo_manager.settings import Settings


# ---------------------------------------------------------------------
# Settings Dialog
# ---------------------------------------------------------------------

class SettingsDialog(QDialog):
    """
    Display and edit application-wide settings.
    """

    def __init__(
        self,
        settings: Settings,
        workspace_editable: bool,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.setWindowTitle(
            "Application Settings"
        )

        self.setModal(True)
        
        self.setMinimumWidth(
            650
        )

        self._settings = settings

        # -------------------------------------------------------------
        # Main layout
        # -------------------------------------------------------------

        main_layout = QVBoxLayout(
            self
        )

        # -------------------------------------------------------------
        # Description
        # -------------------------------------------------------------

        description = QLabel(
            "These settings apply to Photo Manager as a whole."
        )

        description.setWordWrap(
            True
        )

        main_layout.addWidget(
            description
        )

        # -------------------------------------------------------------
        # Settings layout
        # -------------------------------------------------------------

        form_layout = QFormLayout()

        # -------------------------------------------------------------
        # Logging Level
        # -------------------------------------------------------------

        self._logging_level = QComboBox()

        self._logging_level.addItems(
            [
                "DEBUG",
                "INFO",
                "WARNING",
                "ERROR",
            ]
        )

        current_level = settings.logging_level

        level_names = {
            10: "DEBUG",
            20: "INFO",
            30: "WARNING",
            40: "ERROR",
        }

        current_level_name = level_names.get(
            current_level,
            "INFO",
        )

        self._logging_level.setCurrentText(
            current_level_name
        )

        form_layout.addRow(
            "Logging Level",
            self._logging_level,
        )

        # -------------------------------------------------------------
        # Workspace Directory
        # -------------------------------------------------------------

        workspace_layout = QHBoxLayout()

        self._workspace_field = QLineEdit()

        self._workspace_field.setText(
            str(settings.workspace_directory)
            if settings.workspace_directory is not None
            else ""
        )

        self._workspace_field.setReadOnly(
            not workspace_editable
        )

        self._workspace_field.setToolTip(
            "Workspace directory used by Photo Manager."
        )

        workspace_layout.addWidget(
            self._workspace_field,
            1,
        )

        self._browse_button = QPushButton(
            "Browse..."
        )

        self._browse_button.setEnabled(
            workspace_editable
        )

        if workspace_editable:
            self._browse_button.setToolTip(
                "Select the Photo Manager workspace directory."
            )
        else:
            self._browse_button.setToolTip(
                "The workspace directory cannot be changed "
                "while a project operation is in progress."
            )

        self._browse_button.clicked.connect(
            self._browse_workspace
        )

        workspace_layout.addWidget(
            self._browse_button
        )

        form_layout.addRow(
            "Workspace Directory",
            workspace_layout,
        )

        main_layout.addLayout(
            form_layout
        )

        # -------------------------------------------------------------
        # Dialog buttons
        # -------------------------------------------------------------

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        button_box.accepted.connect(
            self.accept
        )

        button_box.rejected.connect(
            self.reject
        )

        main_layout.addWidget(
            button_box
        )

    # -----------------------------------------------------------------
    # Browse Workspace
    # -----------------------------------------------------------------

    def _browse_workspace(
        self,
    ) -> None:
        """
        Allow the user to select a workspace directory.
        """

        current_directory = (
            self._workspace_field.text().strip()
        )

        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Photo Manager Workspace",
            current_directory,
        )

        if directory:
            self._workspace_field.setText(
                directory
            )

    # -----------------------------------------------------------------
    # Settings
    # -----------------------------------------------------------------

    def settings(self) -> Settings:
        """
        Return the settings selected by the user.
        """

        level_names = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
        }

        workspace_text = (
            self._workspace_field.text().strip()
        )

        return Settings(
            logging_level=level_names[
                self._logging_level.currentText()
            ],
            workspace_directory=(
                Path(workspace_text)
                if workspace_text
                else None
            ),
        )
