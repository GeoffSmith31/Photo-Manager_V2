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
Photo Manager Workflow Stage Status

## Purpose

Defines the status states used to represent the progress of a
Photo Manager Workflow Stage.

## Responsibilities

- Define the possible Workflow Stage status states.
- Provide stable status identifiers for communication between the
  Orchestrator, Window Manager and Control Tower.

## Notes

This module contains status definitions only.

The status of a Workflow Stage is a user-facing representation of
workflow progress. It is not intended to duplicate or replace the
Orchestrator's internal state machine.
"""

from enum import Enum


# ---------------------------------------------------------------------
# Workflow Stage Status
# ---------------------------------------------------------------------

class StageStatus(Enum):
    """
    Status states used by Workflow Stage panels.
    """

    PENDING = "pending"

    IN_PROGRESS = "in_progress"

    COMPLETED = "completed"

    ERROR = "error"


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

__all__ = [
    "StageStatus",
]
