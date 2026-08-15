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
Photo Manager Project Selection Tile

## Purpose

Provides the graphical representation of a single project in the
Project Selection activity.

## Responsibilities

- Display a project's thumbnail.
- Display the project name.
- Provide a fixed-size clickable tile.
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QImageReader,
    QPixmap,
)
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from photo_manager.project_selection import (
    ProjectSelectionRecord,
)


# ---------------------------------------------------------------------
# Project Selection Tile
# ---------------------------------------------------------------------

class ProjectSelectionTile(QPushButton):
    """
    Displays one ProjectSelectionRecord as a clickable tile.
    """

    TILE_WIDTH = 250
    TILE_HEIGHT = 210

    def __init__(
        self,
        record: ProjectSelectionRecord,
    ) -> None:

        super().__init__()

        self._record = record

        self.setFixedSize(
            self.TILE_WIDTH,
            self.TILE_HEIGHT,
        )

        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self._build_interface()

    # -----------------------------------------------------------------
    # Build Interface
    # -----------------------------------------------------------------

    def _build_interface(self) -> None:

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            8,
            8,
            8,
            8,
        )

        layout.setSpacing(
            4
        )

        # -------------------------------------------------------------
        # Thumbnail Area
        # -------------------------------------------------------------

        self._thumbnail = QLabel()

        self._thumbnail.setFixedSize(
            234,
            165,
        )

        self._thumbnail.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self._thumbnail.setStyleSheet(
            """
            QLabel {
                background: #eeeeee;
                border-radius: 8px;
            }
            """
        )

        self._set_thumbnail()

        layout.addWidget(
            self._thumbnail,
            0,
            Qt.AlignmentFlag.AlignCenter,
        )

        # -------------------------------------------------------------
        # Project Name
        # -------------------------------------------------------------

        self._project_name = QLabel(
            self._record.project_name
        )

        self._project_name.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self._project_name.setWordWrap(
            True
        )

        layout.addWidget(
            self._project_name,
            1,
    )

    # -----------------------------------------------------------------
    # Set Thumbnail
    # -----------------------------------------------------------------

    def _set_thumbnail(self) -> None:

        thumbnail_path = (
            self._record.thumbnail_path
        )

        if (
            thumbnail_path is None
            or not thumbnail_path.is_file()
        ):
            self._thumbnail.setText(
                "No thumbnail"
            )
            return

        reader = QImageReader(
            str(thumbnail_path)
        )

        reader.setAutoTransform(
            True
        )

        image = reader.read()

        if image.isNull():
            self._thumbnail.setText(
                "Unable to load image"
            )
            return

        pixmap = QPixmap.fromImage(
            image
        )

        scaled_pixmap = pixmap.scaled(
            self._thumbnail.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self._thumbnail.setPixmap(
            scaled_pixmap
        )
        
# ============================================================================
# Standalone Test Harness
# ============================================================================

if __name__ == "__main__":

    import sys

    from PySide6.QtWidgets import QApplication

    application = QApplication(
        sys.argv
    )

    record = ProjectSelectionRecord(
        project_name="The Summer Gathering",
        thumbnail_path=Path(
            "/home/geoff/Demo-PhotoManager-Workspace/"
            "Unusual Exception/images/img398.jpg"
        ),
    )

    tile = ProjectSelectionTile(
        record
    )

    tile.show()

    sys.exit(
        application.exec()
    )
