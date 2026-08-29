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
Photo Manager Propagation Settings Dialog

Provides the modal dialog used to view and edit project metadata
propagation settings.
"""

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
)

from photo_manager.project import (
    MetadataPolicies,
    MetadataPolicy,
)


# ---------------------------------------------------------------------
# Propagation Settings Dialog
# ---------------------------------------------------------------------

class PropagationSettingsDialog(QDialog):
    """
    Modal dialog for editing metadata propagation settings.
    """

    _PROPAGATION_OPTIONS = (
        ("None", "none"),
        ("Project", "project"),
        ("Group", "group"),
        ("Location", "location"),
    )

    def __init__(
        self,
        metadata_policies: MetadataPolicies,
        parent=None,
    ) -> None:
        """
        Initialise the Propagation Settings dialog.
        """

        super().__init__(
            parent
        )

        self.setWindowTitle(
            "Propagation Settings"
        )

        self.setMinimumWidth(500)

        self._metadata_policies = metadata_policies

        self._event_combo = self._create_combo(
            metadata_policies.event.propagate
        )

        self._year_combo = self._create_combo(
            metadata_policies.year.propagate
        )

        self._location_combo = self._create_combo(
            metadata_policies.location.propagate
        )

        self._info_combo = self._create_combo(
            metadata_policies.info.propagate
        )

        self._build_ui()

    # -------------------------------------------------------------
    # Create Combo Box
    # -------------------------------------------------------------

    def _create_combo(
        self,
        current_value: str,
    ) -> QComboBox:
        """
        Create a propagation selection combo box.
        """

        combo = QComboBox()

        for label, value in self._PROPAGATION_OPTIONS:

            combo.addItem(
                label,
                value,
            )

        index = combo.findData(
            current_value
        )

        if index >= 0:

            combo.setCurrentIndex(
                index
            )

        return combo

    # -------------------------------------------------------------
    # Build UI
    # -------------------------------------------------------------

    def _build_ui(self) -> None:
        """
        Build the dialog interface.
        """

        layout = QVBoxLayout(
            self
        )

        explanation = QLabel(
            "These settings determine whether changes made to "
            "Event, Year, Location and Info are applied to other "
            "unedited photos in this project."
        )

        explanation.setWordWrap(
            True
        )

        layout.addWidget(
            explanation
        )

        description = QLabel(
            "<b>None</b> — Do not propagate the change.<br>"
            "<b>Project</b> — Apply the change to all unedited "
            "photos in the project.<br>"
            "<b>Group</b> — Apply the change to unedited photos "
            "in the same group.<br>"
            "<b>Location</b> — Apply the change to unedited photos "
            "at the same location."
        )

        description.setWordWrap(
            True
        )

        layout.addWidget(
            description
        )

        form_layout = QFormLayout()

        form_layout.addRow(
            "Event",
            self._event_combo,
        )

        form_layout.addRow(
            "Year",
            self._year_combo,
        )

        form_layout.addRow(
            "Location",
            self._location_combo,
        )

        form_layout.addRow(
            "Info",
            self._info_combo,
        )

        layout.addLayout(
            form_layout
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(
            self.accept
        )

        buttons.rejected.connect(
            self.reject
        )

        layout.addWidget(
            buttons
        )

    # -------------------------------------------------------------
    # Metadata Policies
    # -------------------------------------------------------------

    def metadata_policies(self) -> MetadataPolicies:
        """
        Return the metadata policies represented by the dialog.

        The existing priority and default values are preserved.
        """

        return MetadataPolicies(
            event=MetadataPolicy(
                propagate=self._event_combo.currentData(),
                priority=self._metadata_policies.event.priority,
                default=self._metadata_policies.event.default,
            ),
            year=MetadataPolicy(
                propagate=self._year_combo.currentData(),
                priority=self._metadata_policies.year.priority,
                default=self._metadata_policies.year.default,
            ),
            location=MetadataPolicy(
                propagate=self._location_combo.currentData(),
                priority=self._metadata_policies.location.priority,
                default=self._metadata_policies.location.default,
            ),
            info=MetadataPolicy(
                propagate=self._info_combo.currentData(),
                priority=self._metadata_policies.info.priority,
                default=self._metadata_policies.info.default,
            ),
        )
