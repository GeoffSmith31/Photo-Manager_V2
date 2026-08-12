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
Photo Manager Project Service

Purpose
-------
Provides the project service used by all Photo Manager components.
Application components do not access project.json directly.
All project operations are coordinated by the Orchestrator.

Responsibilities
----------------
- Load project.json.
- Save project.json.
- Create default projects.
- Validate project data.
- Report missing or invalid project files.

Notes
-----
This module provides the Project Service.

The Project Service manages the complete state of a Photo Manager
workspace.

The project.json file is the authoritative record of project
configuration and photo metadata while a project is open.

Approved metadata is written both to the image file and to the
corresponding photo record in project.json.

The Project Service is responsible for loading, saving and validating
Photo Manager projects.

The Project Service does not create default projects.

Projects are created only through the application's
New Project workflow.

If project.json is missing or invalid, the Project
Service reports the error to the caller. The caller
is responsible for determining the appropriate
recovery action.
"""

from dataclasses import dataclass
from photo_manager.constants import PROJECT_FILENAME


# ---------------------------------------------------------------------
# Metadata Policy
# ---------------------------------------------------------------------

@dataclass
class MetadataPolicy:
    """
    Defines the propagation behaviour for a single metadata field.
    """

    propagate: str
    priority: list[str]
    default: str


# ---------------------------------------------------------------------
# Metadata Policies
# ---------------------------------------------------------------------

@dataclass
class MetadataPolicies:
    """
    Project-wide metadata policies.
    """

    event: MetadataPolicy
    year: MetadataPolicy
    location: MetadataPolicy
    info: MetadataPolicy


# ---------------------------------------------------------------------
# Workspace
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# Workspace
# ---------------------------------------------------------------------

@dataclass
class Workspace:
    """
    Project-wide workspace information.
    """

    # -------------------------------------------------------------
    # Project schema
    # -------------------------------------------------------------

    schema: int

    # -------------------------------------------------------------
    # Import source
    # -------------------------------------------------------------

    importer: str

    source: str
    source_id: str
    source_title: str

    # -------------------------------------------------------------
    # Project status
    # -------------------------------------------------------------

    registration_status: str
    download_status: str

    # -------------------------------------------------------------
    # Project defaults
    # -------------------------------------------------------------

    event: str

    # -------------------------------------------------------------
    # Workspace layout
    # -------------------------------------------------------------

    image_folder: str

    # -------------------------------------------------------------
    # Audit information
    # -------------------------------------------------------------

    created_at: str

# ---------------------------------------------------------------------
# Photo
# ---------------------------------------------------------------------

@dataclass
class Photo:
    """
    Represents a single managed photograph.
    """

    # -------------------------------------------------------------
    # Importer-owned fields
    # -------------------------------------------------------------

    guid: str

    moment_id: str

    latitude: float | None
    longitude: float | None

    # -------------------------------------------------------------
    # Core-owned fields
    # -------------------------------------------------------------

    file: str

    downloaded: bool

    retry_count: int

    status: str

    exif_written: bool

    last_updated: str

    location_key: str | None

    geo_location: str | None

    # -------------------------------------------------------------
    # User-owned fields
    # -------------------------------------------------------------

    event: str

    year: str

    location: str

    info: str


# ---------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------

@dataclass
class Project:
    """
    Complete Photo Manager project.
    """

    workspace: Workspace

    metadata_policies: MetadataPolicies

    photos: list[Photo]
    
# ---------------------------------------------------------------------
# Locate Project File
# ---------------------------------------------------------------------   
    
def get_project_file(
    workspace_directory: Path,
) -> Path:
    """
    Return the path to the project's project.json file.
    """

    logger.debug(
        "Resolving project file in workspace: %s",
        workspace_directory,
    )

    if not workspace_directory.is_dir():
        raise FileNotFoundError(
            f"Workspace does not exist: {workspace_directory}"
        )

    return (
        workspace_directory
        / PROJECT_FILENAME
    )
