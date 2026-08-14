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
Photo Manager Project Selection

## Purpose

Defines the data structure used to represent a project presented
to the user during Project Selection.

## Responsibilities

- Represent an existing project available for selection.
- Represent the New Project selection.
- Provide the information required by the Window Manager and
  Control Tower to render a Project Selection button.

## Notes

This module contains data structures only.

Project discovery, project validation, sorting, and workflow
decisions are responsibilities of the Orchestrator.

The Control Tower does not interpret project information.
It only renders the records provided by the Window Manager.
"""

from dataclasses import dataclass
from pathlib import Path


# ---------------------------------------------------------------------
# Project Selection Record
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class ProjectSelectionRecord:
    """
    Represents one selectable item in the Project Selection activity.

    The Orchestrator creates an ordered collection of these records
    and passes it to the Window Manager for presentation.
    """

    project_name: str

    project_json_path: Path | None = None

    image_folder: Path | None = None

    thumbnail_path: Path | None = None

    is_new_project: bool = False
    
    valid: bool = True
