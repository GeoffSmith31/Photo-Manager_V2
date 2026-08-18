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
Photo Manager Editor Activity

Provides the graphical interface for editing photo metadata.
"""

from pathlib import Path

from PySide6.QtCore import (
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QIcon,
    QImageReader,
    QKeySequence,
    QPixmap,
    QShortcut,
)
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QComboBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

class InfoTextEdit(QTextEdit):
    """
    QTextEdit used by the Editor Info field.

    Enter requests Save & Next.
    Shift+Enter inserts a new line.
    """

    enter_pressed = Signal()

    def keyPressEvent(
        self,
        event,
    ) -> None:

        if (
            event.key()
            in (
                Qt.Key.Key_Return,
                Qt.Key.Key_Enter,
            )
            and not (
                event.modifiers()
                & Qt.KeyboardModifier.ShiftModifier
            )
        ):

            self.enter_pressed.emit()

            return

        super().keyPressEvent(
            event
        )


class EditorActivity(QWidget):
    """
    Photo Manager photo editor activity.

    Initial version contains the user interface only.
    Application behaviour will be added incrementally.
    """

    def __init__(self) -> None:

        super().__init__()
        
        self._photo_pixmap = None
        
        self._build_interface()

    # -----------------------------------------------------------------
    # Build Interface
    # -----------------------------------------------------------------

    def _build_interface(self) -> None:

        main_layout = QVBoxLayout(
            self
        )

        main_layout.setContentsMargins(
            12,
            12,
            12,
            12,
        )

        main_layout.setSpacing(
            10
        )

        # =============================================================
        # Main Editor Area
        # =============================================================

        editor_layout = QHBoxLayout()

        editor_layout.setSpacing(
            16
        )

        # -------------------------------------------------------------
        # Left Side - Photo
        # -------------------------------------------------------------

        photo_layout = QVBoxLayout()

        photo_layout.setSpacing(
            8
        )

        self._photo_frame = QLabel(
            "PHOTO"
        )

        self._photo_frame.setMinimumSize(
            400,
            300,
        )

        self._photo_frame.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self._photo_frame.setStyleSheet(
            """
            QLabel {
                background: #eeeeee;
                border: 2px solid #aaaaaa;
                border-radius: 10px;
                color: #777777;
                font-size: 24px;
            }
            """
        )

        photo_layout.addWidget(
            self._photo_frame,
            1,
        )

        # -------------------------------------------------------------
        # Photo Number
        # -------------------------------------------------------------

        self._photo_number = QLabel(
            "Photo 1 of 237"
        )

        self._photo_number.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        photo_layout.addWidget(
            self._photo_number
        )

        # -------------------------------------------------------------
        # Navigation
        # -------------------------------------------------------------

        navigation_layout = QHBoxLayout()

        self._back_button = QPushButton(
            "◀ Back"
        )

        self._goto_field = QLineEdit()

        self._goto_field.setPlaceholderText(
            "Photo"
        )

        self._goto_field.setFixedWidth(
            80
        )

        self._goto_button = QPushButton(
            "Goto"
        )

        self._forward_button = QPushButton(
            "Forward ▶"
        )

        navigation_layout.addWidget(
            self._back_button
        )

        navigation_layout.addStretch()

        navigation_layout.addWidget(
            self._goto_field
        )

        navigation_layout.addWidget(
            self._goto_button
        )

        navigation_layout.addStretch()

        navigation_layout.addWidget(
            self._forward_button
        )

        photo_layout.addLayout(
            navigation_layout
        )

        editor_layout.addLayout(
            photo_layout,
            3,
        )

        # =============================================================
        # Right Side - Metadata
        # =============================================================

        metadata_group = QGroupBox(
            "Photo Information"
        )

        metadata_group.setMinimumWidth(
            400
        )

        metadata_layout = QGridLayout(
            metadata_group
        )

        metadata_layout.setContentsMargins(
            12,
            18,
            12,
            12,
        )

        metadata_layout.setVerticalSpacing(
            10
        )

        # -------------------------------------------------------------
        # Event
        # -------------------------------------------------------------

        metadata_layout.addWidget(
            QLabel("Event"),
            0,
            0,
        )

        self._event_field = QLineEdit()

        metadata_layout.addWidget(
            self._event_field,
            0,
            1,
        )

        # -------------------------------------------------------------
        # Year
        # -------------------------------------------------------------

        metadata_layout.addWidget(
            QLabel("Year"),
            1,
            0,
        )

        self._year_field = QLineEdit()

        self._year_field.setFixedWidth(
            100
        )

        metadata_layout.addWidget(
            self._year_field,
            1,
            1,
        )

        # -------------------------------------------------------------
        # Location
        # -------------------------------------------------------------

        metadata_layout.addWidget(
            QLabel("Location"),
            2,
            0,
        )

        location_layout = QHBoxLayout()

        self._location_field = QLineEdit()

        self._maps_button = QPushButton()

        self._maps_button.setIcon(
            QIcon(
                str(
                    Path(__file__).parent
                    / "resources"
                    / "map-pin.svg"
                )
            )
        )

        self._maps_button.setIconSize(
            QSize(
                20,
                20,
            )
        )

        self._maps_button.setToolTip(
            "Open location in Google Maps"
        )

        self._maps_button.setAccessibleName(
            "Open location in Google Maps"
        )

        self._maps_button.setToolTip(
            "Launch Google Maps"
        )

        self._maps_button.setFixedWidth(
            40
        )

        self._maps_button.setEnabled(
            False
        )

        location_layout.addWidget(
            self._location_field,
            1,
        )

        location_layout.addWidget(
            self._maps_button
        )

        metadata_layout.addLayout(
            location_layout,
            2,
            1,
        )

        # -------------------------------------------------------------
        # Info
        # -------------------------------------------------------------

        metadata_layout.addWidget(
            QLabel("Info"),
            3,
            0,
            Qt.AlignmentFlag.AlignTop,
        )

        self._info_field = InfoTextEdit(
            self
        )

        self._info_field.setMinimumHeight(
            80
        )

        metadata_layout.addWidget(
            self._info_field,
            3,
            1,
        )

        # -------------------------------------------------------------
        # Save
        # -------------------------------------------------------------

        self._save_button = QPushButton(
            "Save && Next"
        )

        self._save_button.setMinimumHeight(
            40
        )

        metadata_layout.addWidget(
            self._save_button,
            4,
            1,
            
        )

        editor_layout.addWidget(
            metadata_group,
            2,
        )

        main_layout.addLayout(
            editor_layout,
            1,
        )

        # =============================================================
        # Search
        # =============================================================

        search_group = QGroupBox(
            "Search"
        )

        search_layout = QHBoxLayout(
            search_group
        )

        search_layout.setSpacing(
            8
        )

        # =============================================================
        # Search
        # =============================================================

        search_group = QGroupBox(
            "Search"
        )

        search_layout = QHBoxLayout(
            search_group
        )

        search_layout.setSpacing(
            8
        )

        # -------------------------------------------------------------
        # Search Criterion
        # -------------------------------------------------------------

        self._search_criterion = QComboBox()

        self._search_criterion.addItems(
            [
                "Unedited",
                "Missing Event",
                "Missing Year",
                "Missing Location",
                "Missing Info",
                "Containing Text...",
            ]
        )

        self._search_criterion.setFixedWidth(
            200
        )

        # -------------------------------------------------------------
        # Search Text
        # -------------------------------------------------------------

        self._search_text = QLineEdit()

        self._search_text.setPlaceholderText(
            "Text to find..."
        )

        self._search_text.setEnabled(
            False
        )

        # -------------------------------------------------------------
        # Search Buttons
        # -------------------------------------------------------------

        self._search_button = QPushButton(
            "Search"
        )

        self._search_button.setFixedWidth(
            90
        )

        self._search_previous_button = QPushButton(
            "◀ Previous"
        )

        self._search_previous_button.setFixedWidth(
            100
        )

        self._search_next_button = QPushButton(
            "Next ▶"
        )

        self._search_next_button.setFixedWidth(
            80
        )

        # -------------------------------------------------------------
        # Search Button Group
        # -------------------------------------------------------------

        search_button_layout = QHBoxLayout()

        search_button_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        search_button_layout.setSpacing(
            8
        )

        search_button_layout.addWidget(
            self._search_button
        )

        search_button_layout.addWidget(
            self._search_previous_button
        )

        search_button_layout.addWidget(
            self._search_next_button
        )

        # -------------------------------------------------------------
        # Search Layout
        # -------------------------------------------------------------

        search_layout.addWidget(
            self._search_criterion
        )

        search_layout.addWidget(
            self._search_text,
            1,
        )

        search_layout.addLayout(
            search_button_layout
        )

        main_layout.addWidget(
            search_group
        )

        # -------------------------------------------------------------
        # Search Criterion Changed
        # -------------------------------------------------------------

        self._search_criterion.currentTextChanged.connect(
            self._search_criterion_changed
        )

        # -------------------------------------------------------------
        # Button Actions
        # -------------------------------------------------------------

        self._save_button.clicked.connect(
            self._save_and_next
        )

        self._back_button.clicked.connect(
            self._back
        )

        self._forward_button.clicked.connect(
            self._forward
        )

        self._goto_button.clicked.connect(
            self._goto_photo
        )

        self._search_button.clicked.connect(
            self._search
        )

        self._search_previous_button.clicked.connect(
            self._search_previous
        )

        self._search_next_button.clicked.connect(
            self._search_next
        )

        self._maps_button.clicked.connect(
            self._maps_requested
        )

        self._info_field.enter_pressed.connect(
            self._save_and_next
        )

        # -------------------------------------------------------------
        # Keyboard Shortcuts
        # -------------------------------------------------------------

        self._photo_shortcut = QShortcut(
            QKeySequence("Alt+P"),
            self,
        )

        self._photo_shortcut.activated.connect(
            self._goto_field.setFocus
        )

        self._event_shortcut = QShortcut(
            QKeySequence("Alt+E"),
            self,
        )

        self._event_shortcut.activated.connect(
            self._event_field.setFocus
        )

        self._back_shortcut = QShortcut(
            QKeySequence("Alt+Left"),
            self,
        )

        self._back_shortcut.activated.connect(
            self._back
        )

        self._forward_shortcut = QShortcut(
            QKeySequence("Alt+Right"),
            self,
        )

        self._forward_shortcut.activated.connect(
            self._forward
        )

        # -------------------------------------------------------------
        # Editing Field Enter Actions
        # -------------------------------------------------------------

        self._event_field.returnPressed.connect(
            self._year_field.setFocus
        )

        self._year_field.returnPressed.connect(
            self._location_field.setFocus
        )

        self._location_field.returnPressed.connect(
            self._info_field.setFocus
        )

        self._goto_field.returnPressed.connect(
            self._goto_photo
        )

    # -----------------------------------------------------------------
    # Display Photo
    # -----------------------------------------------------------------

    def display_photo(
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
        Display the photo and its current project metadata.

        All values are supplied by the Orchestrator.
        The Editor does not read project data.
        """

        # -------------------------------------------------------------
        # Photo
        # -------------------------------------------------------------

        reader = QImageReader(
            str(image_path)
        )

        reader.setAutoTransform(
            True
        )

        image = reader.read()

        if image.isNull():

            self._photo_pixmap = None

            self._photo_frame.clear()

            self._photo_frame.setText(
                "Unable to load image"
            )

        else:

            self._photo_pixmap = QPixmap.fromImage(
                image
            )

            self._display_photo()

        # -------------------------------------------------------------
        # Metadata
        # -------------------------------------------------------------

        self._event_field.setText(
            event
        )

        self._year_field.setText(
            year
        )

        self._location_field.setText(
            location
        )

        self._info_field.setPlainText(
            info
        )

        # -------------------------------------------------------------
        # Photo Number
        # -------------------------------------------------------------

        self._photo_number.setText(
            f"Photo {photo_number} of {total_photos}"
        )

        # -------------------------------------------------------------
        # Google Maps
        # -------------------------------------------------------------

        self._maps_button.setEnabled(
            maps_available
        )
        
        # -------------------------------------------------------------
        # Initial Editing Focus
        # -------------------------------------------------------------

        self._event_field.setFocus()

    # -----------------------------------------------------------------
    # Editor Actions - Placeholder
    # -----------------------------------------------------------------

    def _save_and_next(self) -> None:

        print(
            "SAVE & NEXT"
        )

    def _back(self) -> None:

        print(
            "BACK"
        )

    def _forward(self) -> None:

        print(
            "FORWARD"
        )

    def _goto_photo(self) -> None:

        print(
            f"GOTO: {self._goto_field.text()}"
        )

    def _search(self) -> None:

        print(
            "SEARCH"
        )

    def _search_previous(self) -> None:

        print(
            "SEARCH PREVIOUS"
        )

    def _search_next(self) -> None:

        print(
            "SEARCH NEXT"
        )

    def _maps_requested(self) -> None:

        print(
            "MAPS REQUESTED"
        )

    # -----------------------------------------------------------------
    # Search Criterion Changed
    # -----------------------------------------------------------------

    def _search_criterion_changed(
        self,
        criterion: str,
    ) -> None:

        enabled = (
            criterion == "Containing Text..."
        )

        self._search_text.setEnabled(
            enabled
        )

        if not enabled:

            self._search_text.clear()

    # -----------------------------------------------------------------
    # Display Photo
    # -----------------------------------------------------------------

    def _display_photo(self) -> None:

        if self._photo_pixmap is None:
            return

        scaled_pixmap = self._photo_pixmap.scaled(
            self._photo_frame.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self._photo_frame.setPixmap(
            scaled_pixmap
        )
    
    # -----------------------------------------------------------------
    # Resize Event
    # -----------------------------------------------------------------

    def resizeEvent(
        self,
        event,
    ) -> None:

        self._display_photo()

        super().resizeEvent(
            event
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

    editor = EditorActivity()

    editor.setWindowTitle(
        "Photo Manager - Editor"
    )

    editor.resize(
        1200,
        800,
    )

    editor.show()

    editor.display_photo(
        image_path=Path(
            "/home/geoff/Demo-PhotoManager-Workspace/"
            "Alice's Wedding/photos/Cambodia139.jpg"
        ),
        event="Alice & Bob's Wedding",
        year="2025",
        location="Cambodia",
        info="A sample photo for testing the V2 Photo Manager editor.",
        photo_number=17,
        total_photos=237,
        maps_available=True,
    )

    sys.exit(
        application.exec()
    )
