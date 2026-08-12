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
Photo Manager User Actions

## Purpose

Defines the user actions that may be presented by the Photo Manager
Control Tower.

## Responsibilities

- Define the application's global user actions.
- Provide stable action identifiers for communication between the
  Orchestrator, Window Manager and Control Tower.

## Notes

This module contains action definitions only.

Actions represent global workflow actions presented through the
Control Tower.

Activity-specific interactions, such as selecting a project or
navigating within the editor, are handled by the appropriate
Activity Panel and are not defined here.
"""

from enum import Enum


# ---------------------------------------------------------------------
# User Actions
# ---------------------------------------------------------------------

class Action(Enum):
    """
    Global user actions presented by the Control Tower.
    """

    CANCEL = "cancel"

    RETRY = "retry"

    CHANGE_PROJECT = "change_project"

    FINALISE = "finalise"


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

__all__ = [
    "Action",
]
