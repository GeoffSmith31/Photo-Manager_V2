# =============================================================================
# Photo Manager
#
# Copyright (c) 2026 Geoff [dev.photomanager@gmail.com]
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# =============================================================================

"""
Photo Manager Project Selection Widget

Provides the graphical interface for selecting an existing project
or creating a new project.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QScrollArea,
    QWidget,
)

from photo_manager.project_selection import (
    ProjectSelectionRecord,
)

from photo_manager.project_selection_tile import (
    ProjectSelectionTile,
)


class ProjectSelectionWidget(QWidget):
    """
    Displays ProjectSelectionRecord objects as project tiles.
    """

    TILE_WIDTH = 250
    TILE_HEIGHT = 210
    TILE_SPACING = 12

    def __init__(
        self,
        project_records: list[ProjectSelectionRecord],
    ) -> None:

        super().__init__()

        self._project_records = project_records
        self._tiles = []

        self._build_interface()

    def _build_interface(self) -> None:

        self._scroll_area = QScrollArea(
            self
        )

        self._scroll_area.setWidgetResizable(
            True
        )

        self._scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self._scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # -------------------------------------------------------------
        # Tile Container
        # -------------------------------------------------------------

        self._tile_container = QWidget()

        self._layout = QGridLayout(
            self._tile_container
        )

        self._layout.setContentsMargins(
            8,
            8,
            8,
            8,
        )

        self._layout.setHorizontalSpacing(
            self.TILE_SPACING
        )

        self._layout.setVerticalSpacing(
            self.TILE_SPACING
        )

        # -------------------------------------------------------------
        # Create Tiles
        # -------------------------------------------------------------

        for record in self._project_records:

            tile = ProjectSelectionTile(
                record
            )

            self._tiles.append(
                tile
            )

        self._scroll_area.setWidget(
            self._tile_container
        )

        # -------------------------------------------------------------
        # Main Layout
        # -------------------------------------------------------------

        from PySide6.QtWidgets import QVBoxLayout

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.addWidget(
            self._scroll_area
        )

        self._arrange_tiles()


    def _arrange_tiles(self) -> None:

        if not self._tiles:
            return

        while self._layout.count():

            item = self._layout.takeAt(
                0
            )

            if item.widget() is not None:

                item.widget().setParent(
                    self
                )

        available_width = (
            self._scroll_area.viewport().width()
        )

        columns = max(
            1,
            (
                available_width
                - 16
                + self.TILE_SPACING
            )
            // (
                self.TILE_WIDTH
                + self.TILE_SPACING
            ),
        )

        for index, tile in enumerate(
            self._tiles
        ):

            row = index // columns
            column = index % columns

            self._layout.addWidget(
                tile,
                row,
                column,
                Qt.AlignmentFlag.AlignTop
                | Qt.AlignmentFlag.AlignLeft,
            )

    # -----------------------------------------------------------------
    # Show Event
    # -----------------------------------------------------------------

    def showEvent(
        self,
        event,
    ) -> None:

        super().showEvent(
            event
        )

        self._arrange_tiles()

    # -----------------------------------------------------------------
    # Resize Event
    # -----------------------------------------------------------------

    def resizeEvent(
        self,
        event,
    ) -> None:

        super().resizeEvent(
            event
        )
        
        self._arrange_tiles()
        
# ============================================================================
# Standalone Test Harness
# ============================================================================

if __name__ == "__main__":

    import sys
    from pathlib import Path

    from PySide6.QtWidgets import QApplication

    application = QApplication(
        sys.argv
    )

    test_records = [
        ProjectSelectionRecord(
            project_name="Alice & Bob's Wedding",
            thumbnail_path=Path(
                "/home/geoff/Demo-PhotoManager-Workspace/"
                "Alice's Wedding/photos/Cambodia139.jpg"
            ),
        ),

        ProjectSelectionRecord(
            project_name="Christmas with the Family",
        ),

        ProjectSelectionRecord(
            project_name="Darling Downs Bicycle Tour",
            thumbnail_path=Path(
                "/home/geoff/Demo-PhotoManager-Workspace/"
                "Darling-Downs_Bike_tour/photos/Frank_Edwards.jpg"
            ),
        ),
    ]

    widget = ProjectSelectionWidget(
        test_records
    )

    widget.show()

    sys.exit(
        application.exec()
    )
