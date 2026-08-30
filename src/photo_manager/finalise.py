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
Photo Manager Finalise Service

Purpose
-------
Provides the project finalisation service used by the
Photo Manager Orchestrator.

Responsibilities
----------------
- Coordinate the filesystem operations required to finalise a project.
- Report Finalise progress to the Orchestrator.
- Select and validate the finalisation destination.
- Resolve filename collisions.
- Copy and verify project photos.
- Remove the completed project from the workspace.

Notes
-----
The Orchestrator coordinates the Finalise workflow and user
interaction.

This service performs the filesystem operations required to
finalise a project but does not directly manipulate the GUI.

Progress is reported through a callback supplied by the
Orchestrator.

The original project remains intact until all destination
photo copies have been successfully completed and verified.

Only after successful verification is project.json deleted.
This prevents Photo Manager from presenting a partially
finalised project as available for editing.

If finalisation is interrupted after project.json has been
deleted, the project may leave files requiring manual
filesystem cleanup. The project will not, however, be
available to Photo Manager.
"""

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from collections.abc import Callable
from photo_manager.constants import APPLICATION_NAME
from photo_manager.logging import get_logger
import hashlib


logger = get_logger("Finalise")


# ---------------------------------------------------------------------
# Finalise Stage
# ---------------------------------------------------------------------

class FinaliseStage(Enum):
    """
    Identifies a stage of the Finalise workflow.
    """

    CHECKING_PROJECT = auto()

    CHECKING_PHOTOS = auto()

    SELECTING_DESTINATION = auto()

    VALIDATING_DESTINATION = auto()

    ANALYSING_FILENAMES = auto()

    RESOLVING_CONFLICTS = auto()

    COPYING_PHOTOS = auto()

    VERIFYING_COPIES = auto()

    REMOVING_PROJECT_FILES = auto()

    REMOVING_SOURCE_PHOTOS = auto()

    COMPLETING = auto()


# ---------------------------------------------------------------------
# Finalise Progress
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class FinaliseProgress:
    """
    Describes the current progress of Finalise.
    """

    stage: FinaliseStage

    message: str

    current: int | None = None

    total: int | None = None

    current_file: str | None = None


# ---------------------------------------------------------------------
# Finalise Progress Callback
# ---------------------------------------------------------------------

FinaliseProgressCallback = Callable[
    [FinaliseProgress],
    None,
]

# ---------------------------------------------------------------------
# Project File Integrity
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class ProjectFileIntegrity:
    """
    Describes the relationship between project-registered photos
    and the actual contents of the project image directory.
    """

    registered_files: list[str]

    present_files: list[str]

    missing_files: list[str]

    unexpected_files: list[str]

    @property
    def is_complete(self) -> bool:
        """
        Return True when all registered photos are present and
        there are no unexpected files.
        """

        return (
            not self.missing_files
            and not self.unexpected_files
        )

# ---------------------------------------------------------------------
# Destination Validation
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class DestinationValidation:
    """
    Describes whether a Finalise destination is suitable for use.
    """

    valid: bool

    reason: str | None = None

# ---------------------------------------------------------------------
# Filename Collision
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class FilenameCollision:
    """
    Describes a filename collision detected during Finalise.
    """

    filename_a: str

    filename_b: str


# ---------------------------------------------------------------------
# Filename Analysis
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class FilenameAnalysis:
    """
    Describes filename collisions between project photos and the
    selected destination.
    """

    destination_collisions: list[FilenameCollision]

    project_collisions: list[FilenameCollision]

    @property
    def has_collisions(self) -> bool:
        """
        Return True when any filename collisions were found.
        """

        return (
            bool(self.destination_collisions)
            or bool(self.project_collisions)
        )

# ---------------------------------------------------------------------
# Analyse Filenames
# ---------------------------------------------------------------------

def analyse_filenames(
    registered_filenames: list[str],
    destination_directory: Path,
    progress_callback: FinaliseProgressCallback | None = None,
) -> FilenameAnalysis:
    """
    Analyse project and destination filenames for collisions.

    Filename comparisons are case-insensitive so that Finalise
    behaves consistently across operating systems.

    No filesystem modifications are performed.
    """

    _report_progress(
        progress_callback,
        FinaliseStage.ANALYSING_FILENAMES,
        "Checking destination filenames...",
    )

    logger.info(
        "Analysing filenames in destination: %s",
        destination_directory,
    )

    # -------------------------------------------------------------
    # Build case-insensitive destination lookup.
    # -------------------------------------------------------------

    destination_files = [
        path.name
        for path in destination_directory.iterdir()
        if path.is_file()
    ]

    destination_lookup = {
        filename.casefold(): filename
        for filename in destination_files
    }

    # -------------------------------------------------------------
    # Check project filenames against destination.
    # -------------------------------------------------------------

    destination_collisions: list[FilenameCollision] = []

    for filename in registered_filenames:

        existing_filename = destination_lookup.get(
            filename.casefold()
        )

        if existing_filename is not None:

            destination_collisions.append(
                FilenameCollision(
                    filename_a=filename,
                    filename_b=existing_filename,
                )
            )

    # -------------------------------------------------------------
    # Check for collisions within the project itself.
    # -------------------------------------------------------------

    project_lookup: dict[str, str] = {}

    project_collisions: list[FilenameCollision] = []

    for filename in registered_filenames:

        key = filename.casefold()

        existing_filename = project_lookup.get(
            key
        )

        if existing_filename is not None:

            project_collisions.append(
                FilenameCollision(
                    filename_a=filename,
                    filename_b=existing_filename,
                )
            )

        else:

            project_lookup[key] = filename

    # -------------------------------------------------------------
    # Log results.
    # -------------------------------------------------------------

    logger.info(
        "Filename analysis: destination_collisions=%d, "
        "project_collisions=%d",
        len(destination_collisions),
        len(project_collisions),
    )

    return FilenameAnalysis(
        destination_collisions=destination_collisions,
        project_collisions=project_collisions,
    )

# ---------------------------------------------------------------------
# Resolve Filename Collisions
# ---------------------------------------------------------------------

def resolve_filename_collisions(
    registered_filenames: list[str],
    destination_directory: Path,
    progress_callback: FinaliseProgressCallback | None = None,
) -> dict[str, str]:
    """
    Determine destination filenames for project photos.

    Filename comparisons are case-insensitive.

    Files that would collide with an existing destination file are
    assigned a new filename using a numeric suffix.

    Example:

        photo.jpg
        photo_1.jpg
        photo_2.jpg

    becomes:

        photo_3.jpg

    when those names are already in use.

    Returns
    -------
    dict[str, str]
        Mapping of original project filename to destination filename.

        Files that do not require renaming map to themselves.

    No filesystem modifications are performed.
    """

    _report_progress(
        progress_callback,
        FinaliseStage.RESOLVING_CONFLICTS,
        "Resolving filename collisions...",
    )

    logger.info(
        "Resolving filename collisions in destination: %s",
        destination_directory,
    )

    # -------------------------------------------------------------
    # Build case-insensitive set of names already in destination.
    # -------------------------------------------------------------

    used_names = {
        path.name.casefold()
        for path in destination_directory.iterdir()
        if path.is_file()
    }

    resolved_names: dict[str, str] = {}

    # -------------------------------------------------------------
    # Resolve each project filename.
    # -------------------------------------------------------------

    for filename in registered_filenames:

        candidate = filename

        if candidate.casefold() not in used_names:

            resolved_names[filename] = candidate

            used_names.add(
                candidate.casefold()
            )

            continue

        original_path = Path(
            filename
        )

        stem = original_path.stem
        suffix = original_path.suffix

        counter = 1

        while True:

            candidate = (
                f"{stem}_{counter}{suffix}"
            )

            if candidate.casefold() not in used_names:
                break

            counter += 1

        resolved_names[filename] = candidate

        used_names.add(
            candidate.casefold()
        )

        logger.info(
            "Filename collision resolved: %s -> %s",
            filename,
            candidate,
        )

    logger.info(
        "Filename collision resolution complete."
    )

    return resolved_names

# ---------------------------------------------------------------------
# Calculate File Hash
# ---------------------------------------------------------------------

def _calculate_file_hash(
    file_path: Path,
) -> str:
    """
    Calculate the SHA-256 hash of a file.

    The file is read incrementally to avoid loading the entire
    file into memory.
    """

    digest = hashlib.sha256()

    with file_path.open("rb") as file:

        while chunk := file.read(1024 * 1024):

            digest.update(
                chunk
            )

    return digest.hexdigest()

# ---------------------------------------------------------------------
# Copy Result
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class CopyResult:
    """
    Describes the result of copying project photos.
    """

    successful: bool

    copied_files: list[Path]

    failed_file: str | None = None

    error: str | None = None

# ---------------------------------------------------------------------
# Copy Project Photos
# ---------------------------------------------------------------------

def copy_project_photos(
    image_directory: Path,
    destination_directory: Path,
    resolved_filenames: dict[str, str],
    progress_callback: FinaliseProgressCallback | None = None,
) -> CopyResult:
    """
    Copy and immediately verify project photos.

    Each photo is copied and then verified using SHA-256 before
    the next photo is copied.

    If either the copy or verification fails, processing stops
    immediately. Files successfully copied before the failure
    are left in the destination.

    No source files are modified or deleted.
    """

    total = len(
        resolved_filenames
    )

    _report_progress(
        progress_callback,
        FinaliseStage.COPYING_PHOTOS,
        "Copying project photos...",
        0,
        total,
    )

    logger.info(
        "Copying and verifying %d project photo(s) to: %s",
        total,
        destination_directory,
    )

    copied_files: list[Path] = []

    for current, (
        source_filename,
        destination_filename,
    ) in enumerate(
        resolved_filenames.items(),
        start=1,
    ):

        source_path = (
            image_directory
            / source_filename
        )

        destination_path = (
            destination_directory
            / destination_filename
        )

        # -------------------------------------------------------------
        # Copy
        # -------------------------------------------------------------

        _report_progress(
            progress_callback,
            FinaliseStage.COPYING_PHOTOS,
            f"Copying photo #{current} of {total}...",
            current,
            total,
            source_filename,
        )

        logger.info(
            "Copying photo #%d of %d: %s -> %s",
            current,
            total,
            source_path,
            destination_path,
        )

        try:

            destination_path.write_bytes(
                source_path.read_bytes()
            )

        except OSError as error:

            logger.error(
                "Unable to copy photo #%d: %s -> %s: %s",
                current,
                source_path,
                destination_path,
                error,
            )

            return CopyResult(
                successful=False,
                copied_files=copied_files,
                failed_file=source_filename,
                error=str(error),
            )

        logger.info(
            "Photo #%d copied successfully.",
            current,
        )

        # -------------------------------------------------------------
        # Verify
        # -------------------------------------------------------------

        _report_progress(
            progress_callback,
            FinaliseStage.VERIFYING_COPIES,
            f"Verifying photo #{current} of {total}...",
            current,
            total,
            destination_filename,
        )

        logger.info(
            "Verifying photo #%d of %d: %s",
            current,
            total,
            destination_filename,
        )

        try:

            source_hash = _calculate_file_hash(
                source_path
            )

            destination_hash = _calculate_file_hash(
                destination_path
            )

        except OSError as error:

            logger.error(
                "Unable to verify photo #%d: %s: %s",
                current,
                destination_filename,
                error,
            )

            return CopyResult(
                successful=False,
                copied_files=copied_files,
                failed_file=source_filename,
                error=str(error),
            )

        if source_hash != destination_hash:

            logger.error(
                "SHA-256 verification failed for photo #%d: "
                "%s",
                current,
                destination_filename,
            )

            return CopyResult(
                successful=False,
                copied_files=copied_files,
                failed_file=source_filename,
                error=(
                    "The copied file does not match "
                    "the original file."
                ),
            )

        logger.info(
            "Photo #%d verification successful.",
            current,
        )

        copied_files.append(
            destination_path
        )

    logger.info(
        "Project photo copying and verification complete: "
        "%d photo(s).",
        len(copied_files),
    )

    return CopyResult(
        successful=True,
        copied_files=copied_files,
    )

# ---------------------------------------------------------------------
# Remove Project File
# ---------------------------------------------------------------------

def remove_project_file(
    project_file: Path,
) -> None:
    """
    Remove the project JSON file after all project photos have been
    successfully copied and verified.

    The project file is removed before the source photos so that an
    interrupted Finalise cannot leave an apparently selectable but
    incomplete project.
    """

    logger.info(
        "Removing project file: %s",
        project_file,
    )

    try:

        project_file.unlink()

    except OSError as error:

        logger.error(
            "Unable to remove project file: %s: %s",
            project_file,
            error,
        )

        raise

    logger.info(
        "Project file removed successfully: %s",
        project_file,
    )

# ---------------------------------------------------------------------
# Remove Source Photos
# ---------------------------------------------------------------------

def remove_source_photos(
    image_directory: Path,
    registered_filenames: list[str],
    progress_callback: FinaliseProgressCallback | None = None,
) -> list[str]:
    """
    Remove the project source photos after successful finalisation.

    Parameters
    ----------
    image_directory
        Source directory containing the project photos.

    registered_filenames
        Authoritative list of project photo filenames.

    progress_callback
        Callback used to report removal progress.

    Returns
    -------
    list[str]
        Filenames successfully removed.

    Notes
    -----
    Files are removed in the order supplied.

    If removal of a file fails, the function stops immediately.
    Files successfully removed before the failure remain removed.
    """

    total = len(
        registered_filenames
    )

    _report_progress(
        progress_callback,
        FinaliseStage.REMOVING_SOURCE_PHOTOS,
        "Removing project photos...",
        0,
        total,
    )

    logger.info(
        "Removing %d source photo(s) from: %s",
        total,
        image_directory,
    )

    removed_files: list[str] = []

    for current, filename in enumerate(
        registered_filenames,
        start=1,
    ):

        file_path = (
            image_directory
            / filename
        )

        _report_progress(
            progress_callback,
            FinaliseStage.REMOVING_SOURCE_PHOTOS,
            f"Removing photo #{current} of {total}...",
            current,
            total,
            filename,
        )

        logger.info(
            "Removing source photo #%d of %d: %s",
            current,
            total,
            file_path,
        )

        try:

            file_path.unlink()

        except OSError as error:

            logger.error(
                "Unable to remove source photo: %s: %s",
                file_path,
                error,
            )

            raise

        removed_files.append(
            filename
        )

        logger.info(
            "Source photo removed: %s",
            filename,
        )

    logger.info(
        "Source photo removal complete: %d photo(s).",
        len(removed_files),
    )

    return removed_files

# ---------------------------------------------------------------------
# Remove Empty Project Directories
# ---------------------------------------------------------------------

def remove_empty_project_directories(
    image_directory: Path,
    project_directory: Path,
) -> None:
    """
    Remove the empty project image directory and project directory.

    Both directories must be empty. No recursive deletion is
    performed.
    """

    logger.info(
        "Removing empty project directories."
    )

    try:

        image_directory.rmdir()

        logger.info(
            "Removed project image directory: %s",
            image_directory,
        )

        project_directory.rmdir()

        logger.info(
            "Removed project directory: %s",
            project_directory,
        )

    except OSError as error:

        logger.error(
            "Unable to remove project directory structure: %s",
            error,
        )

        raise

# ---------------------------------------------------------------------
# Check Project File Integrity
# ---------------------------------------------------------------------

def check_project_file_integrity(
    registered_filenames: list[str],
    image_directory: Path,
    progress_callback: FinaliseProgressCallback | None = None,
) -> ProjectFileIntegrity:
    """
    Compare the registered project photos with the actual contents
    of the project image directory.

    The filenames supplied by the Project service are authoritative.

    No filesystem modifications are performed.
    """

    logger.info(
        "Checking project file integrity: %s",
        image_directory,
    )

    # -------------------------------------------------------------
    # Check project directory.
    # -------------------------------------------------------------

    _report_progress(
        progress_callback,
        FinaliseStage.CHECKING_PROJECT,
        "Checking project...",
    )

    if not image_directory.is_dir():

        raise FileNotFoundError(
            f"Project image directory does not exist: "
            f"{image_directory}"
        )

    # -------------------------------------------------------------
    # Check registered photos.
    # -------------------------------------------------------------

    total = len(
        registered_filenames
    )

    _report_progress(
        progress_callback,
        FinaliseStage.CHECKING_PHOTOS,
        "Checking project photo files...",
        0,
        total,
    )

    present_files: list[str] = []

    for index, filename in enumerate(
        registered_filenames,
        start=1,
    ):

        file_path = (
            image_directory
            / filename
        )

        if file_path.is_file():

            present_files.append(
                filename
            )

        _report_progress(
            progress_callback,
            FinaliseStage.CHECKING_PHOTOS,
            "Checking project photo files...",
            index,
            total,
            filename,
        )

    # -------------------------------------------------------------
    # Determine missing photos.
    # -------------------------------------------------------------

    registered_set = set(
        registered_filenames
    )

    present_set = set(
        present_files
    )

    missing_files = sorted(
        registered_set - present_set
    )

    # -------------------------------------------------------------
    # Determine unexpected files.
    # -------------------------------------------------------------

    actual_files = {
        path.name
        for path in image_directory.iterdir()
        if path.is_file()
    }

    unexpected_files = sorted(
        actual_files - registered_set
    )

    # -------------------------------------------------------------
    # Log results.
    # -------------------------------------------------------------

    logger.info(
        "Project file integrity: "
        "registered=%d, present=%d, missing=%d, unexpected=%d",
        len(registered_filenames),
        len(present_files),
        len(missing_files),
        len(unexpected_files),
    )

    if missing_files:

        logger.warning(
            "Missing project photos: %s",
            ", ".join(missing_files),
        )

    if unexpected_files:

        logger.warning(
            "Unexpected files in project image directory: %s",
            ", ".join(unexpected_files),
        )

    return ProjectFileIntegrity(
        registered_files=sorted(
            registered_filenames
        ),
        present_files=sorted(
            present_files
        ),
        missing_files=missing_files,
        unexpected_files=unexpected_files,
    )

# ---------------------------------------------------------------------
# Validate Destination
# ---------------------------------------------------------------------

def validate_destination(
    destination_directory: Path,
    progress_callback: FinaliseProgressCallback | None = None,
) -> DestinationValidation:
    """
    Validate a destination directory for Finalise.

    The destination must:

    - exist;
    - be a directory;
    - allow Photo Manager to create a temporary file;
    - allow Photo Manager to remove that temporary file.

    No permanent filesystem changes are made.
    """

    _report_progress(
        progress_callback,
        FinaliseStage.VALIDATING_DESTINATION,
        "Validating destination directory...",
    )

    logger.info(
        "Validating Finalise destination: %s",
        destination_directory,
    )

    # -------------------------------------------------------------
    # Exists?
    # -------------------------------------------------------------

    if not destination_directory.exists():

        reason = (
            "The selected destination directory does not exist."
        )

        logger.warning(
            "Destination validation failed: %s",
            reason,
        )

        return DestinationValidation(
            valid=False,
            reason=reason,
        )

    # -------------------------------------------------------------
    # Directory?
    # -------------------------------------------------------------

    if not destination_directory.is_dir():

        reason = (
            "The selected destination is not a directory."
        )

        logger.warning(
            "Destination validation failed: %s",
            reason,
        )

        return DestinationValidation(
            valid=False,
            reason=reason,
        )

    # -------------------------------------------------------------
    # Test write access.
    # -------------------------------------------------------------

    test_file = (
        destination_directory
        / ".photo_manager_finalise_test"
    )

    try:

        test_file.write_bytes(
            b"Photo Manager Finalise write test."
        )

        test_file.unlink()

    except OSError as error:

        try:
            if test_file.exists():
                test_file.unlink()
        except OSError:
            pass

        reason = (
            f"{APPLICATION_NAME} cannot write to the selected "
            "destination directory."
        )

        logger.warning(
            "Destination validation failed: %s (%s)",
            reason,
            error,
        )

        return DestinationValidation(
            valid=False,
            reason=reason,
        )

    logger.info(
        "Destination validation successful: %s",
        destination_directory,
    )

    return DestinationValidation(
        valid=True,
    )

# ---------------------------------------------------------------------
# Report Progress
# ---------------------------------------------------------------------

def _report_progress(
    callback: FinaliseProgressCallback | None,
    stage: FinaliseStage,
    message: str,
    current: int | None = None,
    total: int | None = None,
    current_file: str | None = None,
) -> None:
    """
    Report Finalise progress to the Orchestrator.
    """

    progress = FinaliseProgress(
        stage=stage,
        message=message,
        current=current,
        total=total,
        current_file=current_file,
    )

    logger.debug(
        "Finalise progress: stage=%s, message=%s, "
        "current=%s, total=%s, current_file=%s",
        stage.name,
        message,
        current,
        total,
        current_file,
    )

    if callback is not None:
        callback(
            progress
        )




    # -------------------------------------------------------------
    # Selecting Destination
    # -------------------------------------------------------------


