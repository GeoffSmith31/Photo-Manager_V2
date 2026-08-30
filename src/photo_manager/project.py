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

from __future__ import annotations
import json
import piexif
import piexif.helper
from pathlib import Path
from dataclasses import dataclass
from photo_manager.constants import (
    PROJECT_FILENAME,
    SCHEMA_VERSION,
)
from photo_manager.project_selection import ProjectSelectionRecord
from photo_manager.logging import get_logger
from datetime import datetime

logger = get_logger("Project")

# ---------------------------------------------------------------------
# Photo Data for Editing
# ---------------------------------------------------------------------
@dataclass
class PhotoEditData:
    """
    Photo-level data required by the Editor Activity.
    """

    file: str
    event: str
    year: str
    location: str
    info: str
    has_coordinates: bool

# ---------------------------------------------------------------------
# Get Photo Edit Data
# ---------------------------------------------------------------------

def get_photo_edit_data(
    project_json_path: Path,
    photo_index: int,
) -> PhotoEditData:
    """
    Return the current photo data required by the Editor Activity.

    The project.json file is read each time so that the returned
    information is authoritative and not based on a cached photo
    record.
    """

    logger.debug(
        "Loading photo edit data: %s [%d]",
        project_json_path,
        photo_index,
    )

    data = json.loads(
        project_json_path.read_text(
            encoding="utf-8"
        )
    )

    photo = data["photos"][photo_index]

    image_directory = (
        project_json_path.parent
        / data["workspace"]["image_folder"]
    )

    file_path = (
        image_directory
        / photo["file"]
    )

    has_coordinates = (
        photo.get("lat") is not None
        and photo.get("lng") is not None
    )

    return PhotoEditData(
        file=str(file_path),
        event=photo["event"],
        year=photo["year"],
        location=photo["location"],
        info=photo["info"],
        has_coordinates=has_coordinates,
    )


# ---------------------------------------------------------------------
# Get Unedited Photos
# ---------------------------------------------------------------------

def get_unedited_photos(
    project_json_path: Path,
) -> list[dict]:
    """
    Return the project photo records that have not yet had
    their EXIF written.

    A photo is considered edited when its exif_written field is True.
    """

    logger.debug(
        "Loading unedited photos: %s",
        project_json_path,
    )

    data = json.loads(
        project_json_path.read_text(
            encoding="utf-8"
        )
    )

    photos = data["photos"]

    unedited_photos = [
        photo
        for photo in photos
        if not photo["exif_written"]
    ]

    logger.debug(
        "Found %d unedited photo(s).",
        len(unedited_photos),
    )

    return unedited_photos

# ---------------------------------------------------------------------
# Get Project Photo Filenames
# ---------------------------------------------------------------------

def get_project_photo_filenames(
    project_json_path: Path,
) -> list[str]:
    """
    Return the filenames of all photos registered in the project.

    The filenames recorded in project.json are authoritative.
    """

    logger.debug(
        "Loading project photo filenames: %s",
        project_json_path,
    )

    data = json.loads(
        project_json_path.read_text(
            encoding="utf-8"
        )
    )

    photos = data["photos"]

    filenames = [
        photo["file"]
        for photo in photos
    ]

    logger.debug(
        "Found %d registered project photo(s).",
        len(filenames),
    )

    return filenames

# ---------------------------------------------------------------------
# Save Photo Edit Data
# ---------------------------------------------------------------------

def save_photo_edit_data(
    project_json_path: Path,
    photo_index: int,
    metadata: dict,
    metadata_policies: MetadataPolicies,
) -> None:
    """
    Save edited metadata for one photo and apply metadata
    propagation according to the project policies.

    The current photo is always updated.

    Propagation is applied only to other photos where
    exif_written is False.

    Propagation does not modify exif_written or last_updated.
    """

    logger.debug(
        "Saving photo edit data with propagation: %s [%d]",
        project_json_path,
        photo_index,
    )

    data = json.loads(
        project_json_path.read_text(
            encoding="utf-8"
        )
    )

    photos = data["photos"]

    if (
        photo_index < 0
        or photo_index >= len(photos)
    ):
        raise IndexError(
            f"Photo index out of range: {photo_index}"
        )

    current_photo = photos[photo_index]

    # -------------------------------------------------------------
    # Save the current photo's edited metadata.
    # -------------------------------------------------------------

    current_photo["event"] = metadata["event"]
    current_photo["year"] = metadata["year"]
    current_photo["location"] = metadata["location"]
    current_photo["info"] = metadata["info"]

    # -------------------------------------------------------------
    # Propagation policies.
    # -------------------------------------------------------------

    policies = {
        "event": metadata_policies.event,
        "year": metadata_policies.year,
        "location": metadata_policies.location,
        "info": metadata_policies.info,
    }

    propagation_count = 0

    # -------------------------------------------------------------
    # Apply propagation to other unedited photos.
    # -------------------------------------------------------------

    for index, photo in enumerate(photos):

        if index == photo_index:
            continue

        if photo["exif_written"]:
            continue

        for field, policy in policies.items():

            if policy.propagate == "none":
                continue

            if policy.propagate == "project":

                applies = True

            elif policy.propagate == "group":

                applies = (
                    photo["moment_id"]
                    == current_photo["moment_id"]
                )

            elif policy.propagate == "location":

                applies = (
                    photo["location_key"]
                    == current_photo["location_key"]
                )

            else:

                logger.warning(
                    "Unknown propagation policy for %s: %r",
                    field,
                    policy.propagate,
                )

                continue

            if applies:

                photo[field] = metadata[field]

                propagation_count += 1

    # -------------------------------------------------------------
    # Write current metadata and propagation together.
    # -------------------------------------------------------------

    project_json_path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    logger.debug(
        "Photo metadata saved: current=%d, propagated=%d.",
        photo_index,
        propagation_count,
    )
# ---------------------------------------------------------------------
# Find Photo
# ---------------------------------------------------------------------

def find_photo(
    project_json_path: Path,
    current_photo: int,
    criterion: str,
    text: str,
    direction: int,
) -> int | None:
    """
    Find the next matching photo in the requested direction.

    direction:
        1  = forward
       -1  = backward

    The search wraps around the project.

    Returns:
        Zero-based photo index when a match is found.
        None when no photo matches.
    """

    logger.debug(
        "Finding photo: current=%d criterion=%r "
        "text=%r direction=%d",
        current_photo,
        criterion,
        text,
        direction,
    )

    data = json.loads(
        project_json_path.read_text(
            encoding="utf-8"
        )
    )

    photos = data["photos"]

    if not photos:
        return None

    if (
        current_photo < 0
        or current_photo >= len(photos)
    ):
        raise IndexError(
            f"Photo index out of range: {current_photo}"
        )

    if direction not in (-1, 1):
        raise ValueError(
            f"Invalid search direction: {direction}"
        )

    search_text = text.casefold()

    index = (
        current_photo + direction
    ) % len(photos)

    while index != current_photo:

        photo = photos[index]

        match = False

        # ---------------------------------------------------------
        # Unedited
        # ---------------------------------------------------------

        if criterion == "Unedited":

            match = (
                photo.get("exif_written", False)
                is False
            )

        # ---------------------------------------------------------
        # Missing Event
        # ---------------------------------------------------------

        elif criterion == "Missing Event":

            match = not photo.get(
                "event",
                "",
            )

        # ---------------------------------------------------------
        # Missing Year
        # ---------------------------------------------------------

        elif criterion == "Missing Year":

            match = not photo.get(
                "year",
                "",
            )

        # ---------------------------------------------------------
        # Missing Location
        # ---------------------------------------------------------

        elif criterion == "Missing Location":

            match = not photo.get(
                "location",
                "",
            )

        # ---------------------------------------------------------
        # Missing Info
        # ---------------------------------------------------------

        elif criterion == "Missing Info":

            match = not photo.get(
                "info",
                "",
            )

        # ---------------------------------------------------------
        # Containing Text
        # ---------------------------------------------------------

        elif criterion == "Containing Text...":

            fields = (
                photo.get("event", ""),
                photo.get("year", ""),
                photo.get("location", ""),
                photo.get("info", ""),
            )

            match = any(
                search_text
                in str(field).casefold()
                for field in fields
            )

        else:
            raise ValueError(
                f"Unknown find criterion: {criterion}"
            )

        if match:

            logger.debug(
                "Find matched photo: %d",
                index,
            )

            return index

        index = (
            index + direction
        ) % len(photos)

    logger.debug(
        "Find produced no match."
    )

    return None

# ---------------------------------------------------------------------
# Write Photo EXIF
# ---------------------------------------------------------------------

def write_photo_exif(
    project_json_path: Path,
    photo_index: int,
    metadata: dict,
) -> None:
    """
    Write Photo Manager metadata to the photo's EXIF UserComment.

    UserComment format is defined by ADR-009:

        <Event> | <Year> | <Location> | <Info>

    Empty fields are omitted.
    """

    logger.debug(
        "Writing photo EXIF: %s [%d]",
        project_json_path,
        photo_index,
    )

    # -------------------------------------------------------------
    # Load project information
    # -------------------------------------------------------------

    data = json.loads(
        project_json_path.read_text(
            encoding="utf-8"
        )
    )

    photos = data["photos"]

    if (
        photo_index < 0
        or photo_index >= len(photos)
    ):
        raise IndexError(
            f"Photo index out of range: {photo_index}"
        )

    photo = photos[photo_index]

    # -------------------------------------------------------------
    # Locate image
    # -------------------------------------------------------------

    image_path = (
        project_json_path.parent
        / data["workspace"]["image_folder"]
        / photo["file"]
    )

    logger.debug(
        "EXIF image: %s",
        image_path,
    )

    # -------------------------------------------------------------
    # Construct UserComment
    # -------------------------------------------------------------

    fields = (
        metadata.get("event", ""),
        metadata.get("year", ""),
        metadata.get("location", ""),
        metadata.get("info", ""),
    )

    user_comment = " | ".join(
        str(field).strip()
        for field in fields
        if str(field).strip()
    )

    logger.debug(
        "UserComment: %s",
        user_comment,
    )

    # -------------------------------------------------------------
    # Load existing EXIF
    # -------------------------------------------------------------

    exif_dict = piexif.load(
        str(image_path)
    )

    # -------------------------------------------------------------
    # Replace UserComment
    # -------------------------------------------------------------

    exif_dict["Exif"][
        piexif.ExifIFD.UserComment
    ] = piexif.helper.UserComment.dump(
        user_comment,
        encoding="ascii",
    )

    # -------------------------------------------------------------
    # Write EXIF
    # -------------------------------------------------------------

    exif_bytes = piexif.dump(
        exif_dict
    )

    piexif.insert(
        exif_bytes,
        str(image_path),
    )

    logger.debug(
        "Photo EXIF written successfully: %s",
        image_path,
    )

# -------------------------------------------------------------
# Set exif_written
# -------------------------------------------------------------

def set_photo_exif_written(
    project_json_path: Path,
    photo_index: int,
    value: bool,
) -> None:
    """
    Set the exif_written flag for one photo.
    """

    logger.debug(
        "Setting exif_written=%s: %s [%d]",
        value,
        project_json_path,
        photo_index,
    )

    data = json.loads(
        project_json_path.read_text(
            encoding="utf-8"
        )
    )

    photos = data["photos"]

    if (
        photo_index < 0
        or photo_index >= len(photos)
    ):
        raise IndexError(
            f"Photo index out of range: {photo_index}"
        )

    photos[photo_index]["exif_written"] = value
    
    if value:

        photos[photo_index]["last_updated"] = (
            datetime.now().isoformat()
        )

    project_json_path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    logger.debug(
        "exif_written updated successfully: %s [%d]",
        project_json_path,
        photo_index,
    )

# ---------------------------------------------------------------------
# Get Photo Coordinates
# ---------------------------------------------------------------------

def get_photo_coordinates(
    project_json_path: Path,
    photo_index: int,
) -> tuple[float, float] | None:
    """
    Return the GPS coordinates for a photo.

    Returns None when the photo has no complete GPS coordinates.
    """

    data = json.loads(
        project_json_path.read_text(
            encoding="utf-8"
        )
    )

    photo = data["photos"][photo_index]

    latitude = photo.get("lat")
    longitude = photo.get("lng")

    if latitude is None or longitude is None:
        return None

    return (
        float(latitude),
        float(longitude),
    )

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
# Get Metadata Policies
# ---------------------------------------------------------------------

def get_metadata_policies(
    project_json_path: Path,
) -> MetadataPolicies:
    """
    Return the metadata policies for a project.

    Metadata policies are stored in project.json and are independent
    of ProjectGlobal data.
    """

    logger.debug(
        "Loading metadata policies: %s",
        project_json_path,
    )

    data = json.loads(
        project_json_path.read_text(
            encoding="utf-8"
        )
    )

    metadata_data = data["metadata_policies"]

    metadata_policies = MetadataPolicies(
        event=MetadataPolicy(
            propagate=metadata_data["event"]["propagate"],
            priority=metadata_data["event"]["priority"],
            default=metadata_data["event"]["default"],
        ),
        year=MetadataPolicy(
            propagate=metadata_data["year"]["propagate"],
            priority=metadata_data["year"]["priority"],
            default=metadata_data["year"]["default"],
        ),
        location=MetadataPolicy(
            propagate=metadata_data["location"]["propagate"],
            priority=metadata_data["location"]["priority"],
            default=metadata_data["location"]["default"],
        ),
        info=MetadataPolicy(
            propagate=metadata_data["info"]["propagate"],
            priority=metadata_data["info"]["priority"],
            default=metadata_data["info"]["default"],
        ),
    )

    logger.debug(
        "Metadata policies loaded: %s",
        metadata_policies,
    )

    return metadata_policies

# ---------------------------------------------------------------------
# Save Metadata Policies
# ---------------------------------------------------------------------

def save_metadata_policies(
    project_json_path: Path,
    metadata_policies: MetadataPolicies,
) -> None:
    """
    Save metadata policies to project.json.

    Only the metadata_policies section is changed.
    All other project data is preserved.

    Raises
    ------
    OSError
        If project.json cannot be read or written.

    json.JSONDecodeError
        If project.json does not contain valid JSON.
    """

    logger.debug(
        "Saving metadata policies: %s",
        project_json_path,
    )

    try:

        data = json.loads(
            project_json_path.read_text(
                encoding="utf-8"
            )
        )

        data["metadata_policies"] = {
            "event": {
                "propagate": metadata_policies.event.propagate,
                "priority": metadata_policies.event.priority,
                "default": metadata_policies.event.default,
            },
            "year": {
                "propagate": metadata_policies.year.propagate,
                "priority": metadata_policies.year.priority,
                "default": metadata_policies.year.default,
            },
            "location": {
                "propagate": metadata_policies.location.propagate,
                "priority": metadata_policies.location.priority,
                "default": metadata_policies.location.default,
            },
            "info": {
                "propagate": metadata_policies.info.propagate,
                "priority": metadata_policies.info.priority,
                "default": metadata_policies.info.default,
            },
        }

        project_json_path.write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            ) + "\n",
            encoding="utf-8",
        )

    except (
        OSError,
        json.JSONDecodeError,
    ) as error:

        logger.error(
            "Unable to save metadata policies: %s",
            error,
        )

        raise

    logger.debug(
        "Metadata policies saved: %s",
        project_json_path,
    )

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
# Validate Project JSON
# ---------------------------------------------------------------------

def validate_project_data(
    project_json_path: Path,
) -> bool:
    """
    Validate project.json syntax and schema compatibility.

    Returns True if the project JSON is syntactically valid and
    contains a supported schema version.
    """

    try:
        data = json.loads(
            project_json_path.read_text(
                encoding="utf-8"
            )
        )

    except json.JSONDecodeError:
        logger.warning(
            "Invalid JSON in project file: %s",
            project_json_path,
        )
        return False

    except OSError as error:
        logger.warning(
            "Unable to read project file %s: %s",
            project_json_path,
            error,
        )
        return False

    try:
        schema_version = data["workspace"]["schema"]

    except (KeyError, TypeError):
        logger.warning(
            "Project is missing mandatory field: "
            "workspace.schema: %s",
            project_json_path,
        )
        return False

    if (
        not isinstance(schema_version, int)
        or isinstance(schema_version, bool)
        or schema_version != SCHEMA_VERSION
    ):
        logger.warning(
            "Unsupported project schema version %r in %s",
            schema_version,
            project_json_path,
        )
        return False
        
    try:
        registration_status = (
            data["workspace"]["registration_status"]
        )

    except (KeyError, TypeError):
        logger.warning(
            "Project is missing mandatory field: "
            "workspace.registration_status: %s",
            project_json_path,
        )
        return False

    valid_registration_statuses = {
        "NOT_STARTED",
        "IN_PROGRESS",
        "COMPLETE",
    }

    if registration_status not in valid_registration_statuses:
        logger.warning(
            "Invalid registration_status %r in %s",
            registration_status,
            project_json_path,
        )
        return False
        
    try:
        download_status = (
            data["workspace"]["download_status"]
        )

    except (KeyError, TypeError):
        logger.warning(
            "Project is missing mandatory field: "
            "workspace.download_status: %s",
            project_json_path,
        )
        return False

    valid_download_statuses = {
        "NOT_STARTED",
        "IN_PROGRESS",
        "COMPLETE",
    }

    if download_status not in valid_download_statuses:
        logger.warning(
            "Invalid download_status %r in %s",
            download_status,
            project_json_path,
        )
        return False
        
    try:
        project_name = data["workspace"]["event"]

    except (KeyError, TypeError):
        logger.warning(
            "Project is missing mandatory field: "
            "workspace.event: %s",
            project_json_path,
        )
        return False

    if (
        not isinstance(project_name, str)
        or not project_name.strip()
    ):
        logger.warning(
            "Invalid workspace.event %r in %s",
            project_name,
            project_json_path,
        )
        return False

    try:
        image_folder = data["workspace"]["image_folder"]

    except (KeyError, TypeError):
        logger.warning(
            "Project is missing mandatory field: "
            "workspace.image_folder: %s",
            project_json_path,
        )
        return False

    if (
        not isinstance(image_folder, str)
        or not image_folder.strip()
    ):
        logger.warning(
            "Invalid workspace.image_folder %r in %s",
            image_folder,
            project_json_path,
        )
        return False

    image_directory = (
        project_json_path.parent
        / image_folder
    )

    if not image_directory.is_dir():
        logger.warning(
            "Project image folder not found: %s",
            image_directory,
        )
        return False
        
    source_fields = (
        "importer",
        "source",
        "source_id",
        "source_title",
    )

    for field_name in source_fields:

        try:
            value = data["workspace"][field_name]

        except (KeyError, TypeError):
            logger.warning(
                "Project is missing mandatory field: "
                "workspace.%s: %s",
                field_name,
                project_json_path,
            )
            return False

        if (
            not isinstance(value, str)
            or not value.strip()
        ):
            logger.warning(
                "Invalid workspace.%s %r in %s",
                field_name,
                value,
                project_json_path,
            )
            return False

    return True
    
# ---------------------------------------------------------------------
# Get Project Global Data
# ---------------------------------------------------------------------

def get_project_global(
    project_json_path: Path,
) -> tuple[int, str, str]:
    """
    Return the project-level information required by the
    Orchestrator.

    The photo records are deliberately not returned. They remain
    authoritative in project.json and are retrieved separately when
    required.
    """

    logger.debug(
        "Loading project global data: %s",
        project_json_path,
    )

    data = json.loads(
        project_json_path.read_text(
            encoding="utf-8"
        )
    )

    workspace = data["workspace"]

    photo_count = len(
        data["photos"]
    )
    source = workspace["source"]
    source_title = workspace["source_title"]

    logger.debug(
        "Project global data: photos=%d, source=%s, source_title=%s",
        photo_count,
        source,
        source_title,
    )

    return (
        photo_count,
        source,
        source_title,
    )
# ---------------------------------------------------------------------
# Get Registration Status
# ---------------------------------------------------------------------

def get_registration_status(
    project_json_path: Path,
) -> str:
    """
    Return the current project registration status.

    The project.json file is read each time so that the returned
    information reflects the current authoritative project state.
    """

    logger.debug(
        "Loading registration status: %s",
        project_json_path,
    )

    data = json.loads(
        project_json_path.read_text(
            encoding="utf-8"
        )
    )

    return data["workspace"]["registration_status"]


# ---------------------------------------------------------------------
# Get Download Status
# ---------------------------------------------------------------------

def get_download_status(
    project_json_path: Path,
) -> str:
    """
    Return the current project download status.

    The project.json file is read each time so that the returned
    information reflects the current authoritative project state.
    """

    logger.debug(
        "Loading download status: %s",
        project_json_path,
    )

    data = json.loads(
        project_json_path.read_text(
            encoding="utf-8"
        )
    )

    return data["workspace"]["download_status"]    

# ---------------------------------------------------------------------
# Get Photo Availability
# ---------------------------------------------------------------------

def get_photo_availability(
    project_json_path: Path,
) -> tuple[int, int]:
    """
    Return the number of registered photo records and the number
    currently available locally.

    Registered is the total number of photo records in project.json.
    Present is the number of records with downloaded=True.

    The values are derived from the current photo records so they
    remain valid even if registration or downloading was interrupted.
    """

    logger.debug(
        "Loading photo availability: %s",
        project_json_path,
    )

    data = json.loads(
        project_json_path.read_text(
            encoding="utf-8"
        )
    )

    photos = data["photos"]

    registered = len(photos)

    present = sum(
        1
        for photo in photos
        if photo["downloaded"] is True
    )

    logger.debug(
        "Photo availability: registered=%d, present=%d",
        registered,
        present,
    )

    return registered, present

# ---------------------------------------------------------------------
# Discover Available Projects
# ---------------------------------------------------------------------

def discover_available_projects(
    workspace_directory: Path,
) -> list[ProjectSelectionRecord]:
    """
    Discover all valid Photo Manager projects in a workspace.

    Projects are identified by recursively locating project.json files.

    The project name is obtained from workspace.event.

    The image folder is resolved relative to the directory containing
    project.json, using workspace.image_folder.

    The thumbnail path is resolved to the complete filesystem path
    using the first photo listed in project.json.

    Projects without photos have no thumbnail.
    """

    project_records = []

    project_files = sorted(
        workspace_directory.rglob(
            PROJECT_FILENAME
        )
    )

    for project_json_path in project_files:

        if not validate_project_data(
            project_json_path
        ):
            continue

        try:
            data = json.loads(
                project_json_path.read_text(
                    encoding="utf-8"
                )
            )

            workspace = data["workspace"]

            project_name = workspace["event"]

            image_folder = workspace["image_folder"]

            project_directory = (
                project_json_path.parent
            )

            image_directory = (
                project_directory
                / image_folder
            )

            photos = data.get(
                "photos",
                []
            )

            thumbnail_path = None

            if photos:
                first_photo = photos[0]

                thumbnail_path = (
                    image_directory
                    / first_photo["file"]
                )

            valid = True

            if thumbnail_path is not None:
                if not thumbnail_path.is_file():
                    logger.warning(
                        "Thumbnail image not found: %s",
                        thumbnail_path,
                    )
                    thumbnail_path = None

            project_records.append(
                ProjectSelectionRecord(
                    project_name=project_name,
                    project_json_path=project_json_path,
                    image_folder=image_folder,
                    thumbnail_path=thumbnail_path,
                    is_new_project=False,
                    valid=valid,
                )
            )

        except (
            KeyError,
            json.JSONDecodeError,
            OSError,
            TypeError,
        ):
            continue

    return project_records
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
