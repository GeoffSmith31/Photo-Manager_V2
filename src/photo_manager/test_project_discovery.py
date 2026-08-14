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
Photo Manager Project Discovery Test Harness

Tests the startup path required for project discovery:

    Settings Service
        ↓
    Workspace validation
        ↓
    Project Service
        ↓
    ProjectSelectionRecord[]

This harness deliberately does not create a Window Manager or GUI.
"""

import logging
import os

from photo_manager.logging import (
    configure_logging,
    get_logger,
)

from photo_manager.settings import load_settings
from photo_manager.project import discover_available_projects


logger = get_logger("Project Discovery Test")


# ---------------------------------------------------------------------
# Validate Workspace
# ---------------------------------------------------------------------

def validate_workspace(workspace):
    """
    Validate the configured workspace.

    This mirrors the workspace validation currently performed by the
    Orchestrator, without involving the GUI.
    """

    if workspace is None:
        raise RuntimeError(
            "No workspace has been configured."
        )

    if not workspace.exists():
        raise RuntimeError(
            f"Configured workspace does not exist: {workspace}"
        )

    if not workspace.is_dir():
        raise RuntimeError(
            f"Configured workspace is not a directory: {workspace}"
        )

    if not os.access(workspace, os.R_OK):
        raise RuntimeError(
            f"Configured workspace is not readable: {workspace}"
        )

    if not os.access(workspace, os.W_OK):
        raise RuntimeError(
            f"Configured workspace is not writable: {workspace}"
        )

    return workspace


# ---------------------------------------------------------------------
# Display Project Records
# ---------------------------------------------------------------------

def display_project_records(records):
    """
    Display the discovered ProjectSelectionRecords.
    """

    print()
    print("=" * 72)
    print("PROJECT DISCOVERY TEST")
    print("=" * 72)

    print()
    print(f"Projects discovered: {len(records)}")
    print()

    for index, record in enumerate(records, start=1):

        print(f"[{index}]")
        print(f"  Project Name : {record.project_name}")
        print(f"  Project JSON : {record.project_json_path}")
        print(f"  Image Folder : {record.image_folder}")
        print(f"  Thumbnail    : {record.thumbnail_path}")
        print(f"  New Project  : {record.is_new_project}")
        print(f"  Valid        : {record.valid}")
        print()


# ---------------------------------------------------------------------
# Main Test
# ---------------------------------------------------------------------

def main():
    """
    Run the project discovery test.
    """

    configure_logging(
        level=logging.INFO,
        console_logging=True,
    )

    logger.info(
        "Starting project discovery test."
    )

    # -------------------------------------------------------------
    # Load application settings.
    # -------------------------------------------------------------

    logger.info(
        "Loading application settings."
    )

    settings = load_settings()

    print()
    print(
        f"Configured workspace: "
        f"{settings.workspace_directory}"
    )

    # -------------------------------------------------------------
    # Validate workspace.
    # -------------------------------------------------------------

    logger.info(
        "Validating configured workspace."
    )

    workspace = validate_workspace(
        settings.workspace_directory
    )

    print(
        f"Validated workspace:  {workspace}"
    )

    # -------------------------------------------------------------
    # Discover projects.
    # -------------------------------------------------------------

    logger.info(
        "Discovering available projects."
    )

    records = discover_available_projects(
        workspace
    )

    # -------------------------------------------------------------
    # Display results.
    # -------------------------------------------------------------

    display_project_records(
        records
    )

    logger.info(
        "Project discovery test complete."
    )


# ---------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------

if __name__ == "__main__":
    main()
