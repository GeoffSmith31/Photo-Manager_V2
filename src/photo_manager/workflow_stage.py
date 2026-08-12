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
Photo Manager Workflow Stages

## Purpose

Defines the user-facing Workflow Stages used by Photo Manager.

## Responsibilities

- Define the major stages of the Photo Manager user workflow.
- Provide stable stage identifiers for communication between the
  Orchestrator, Window Manager and Control Tower.

## Notes

This module contains Workflow Stage definitions only.

Workflow Stages represent major user-facing phases of the application.
They do not necessarily correspond one-to-one with the internal states
of the Orchestrator state machine.
"""

from enum import Enum


# ---------------------------------------------------------------------
# Workflow Stages
# ---------------------------------------------------------------------

class WorkflowStage(Enum):
    """
    Major user-facing stages of the Photo Manager workflow.
    """

    INITIALISATION = "initialisation"

    PROJECT_SELECTION = "project_selection"

    SOURCE_SELECTION = "source_selection"

    IMPORTING = "importing"

    EDITING = "editing"

    FINALISATION = "finalisation"


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

__all__ = [
    "WorkflowStage",
]
