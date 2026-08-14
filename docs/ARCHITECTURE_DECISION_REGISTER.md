# ADR-001 – Project Workspace Model
Status

Accepted

Decision

Photo Manager SHALL support multiple project workspaces.

Only one project workspace MAY be active at any time.

Each project SHALL be stored in its own workspace directory.

Each workspace SHALL contain a standard project.json file that defines the persistent state of that project.

The Project Manager SHALL be responsible for creating, opening, closing and managing the active project workspace.

Rationale

Supporting multiple workspaces provides greater flexibility while preserving the simplicity of a single active project.

Typical use cases include:

Maintaining multiple independent photo collections.
Importing several Journi trips over time.
Archiving completed projects.
Backing up or moving individual projects.

Using a standard project.json filename within each workspace eliminates the need to rename project files while keeping each workspace self-contained.

Consequences
Startup no longer automatically resumes the previous project.
The user selects or creates a project before import or editing operations commence.
Resume processing occurs only after a project has been opened.
The Core–Importer API and Importer SDK require no modification.

# ADR-002 – Application Logging

The application maintains a single persistent diagnostic log.

Logging is controlled by configurable log levels.

In normal operation, only WARNING and ERROR messages are recorded.

During development or troubleshooting, INFO and DEBUG logging may be enabled.

Log entries identify the originating component and, where applicable, the active project.

# ADR-003 – Orchestrator-Centred Workflow

The Orchestrator coordinates all business operations between Core components.

Components SHALL NOT invoke business operations on other components directly.

Infrastructure services (such as logging) are configured during application startup and may be used directly by application components.

This separation prevents the Orchestrator from becoming an infrastructure bottleneck while ensuring it remains the single authority for application workflow and state transitions.

# ADR-004 – Logging Architecture

Decision

Logging is provided by a dedicated Logging Service.
The Orchestrator configures the Logging Service during application startup.
The Settings Service provides the logging directory and logging level.
The Logging Service determines log filenames and manages log rotation.
All components obtain loggers via get_logger().
Components use human-readable names (e.g. "Project Manager") rather than Python module names.
The Logging Service supports standalone operation for development and testing.

# ADR-005 – Separation of Application and Workspace Configuration

The Settings Service stores only application-wide configuration.
Application settings are in a .json file.
Each workspace stores its own configuration in project.json.
Runtime state is maintained separately and is not persisted unless explicitly required.

# ADR-006 – Platform Directory Resolution

Decision

Photo Manager shall use the platformdirs library to determine platform-specific locations for configuration, application state, cache and log files.

Rationale

avoids maintaining operating-system-specific code
follows native platform conventions
mature, widely-used library
small, focused dependency

# ADR-007 — Project Directory Structure and Path Convention

**Status:** Accepted  
**Date:** 2026-08-13

## Context

Photo Manager projects are stored beneath the configured workspace.

The project directory name is not required to match the Project Name stored in the project data. The application therefore needs a consistent and unambiguous method of locating project image files without relying on directory naming conventions or filesystem searches.

The `project.json` file is the authoritative record for the project and contains the `image_folder` value and the filenames of the project's photos.

## Decision

Each Photo Manager project will be stored in its own directory beneath the configured workspace.

The standard project directory structure is:

    <workspace>/
    └── <project directory>/
        ├── project.json
        └── <image_folder>/
            ├── image1.jpg
            ├── image2.jpg
            └── ...

The following path conventions apply:

- `project.json` is located in the project directory.
- `workspace.image_folder` contains a path relative to the project directory.
- Each `photo.file` value contains a filename relative to `workspace.image_folder`.
- The Project Name is obtained from `workspace.event`.
- The project directory is determined from the location of `project.json`.
- No absolute filesystem paths will be stored in `project.json`.

Paths are therefore resolved as follows:

    project_directory = project.json.parent

    image_directory =
        project_directory / workspace.image_folder

    photo_path =
        image_directory / photo.file

For example:

    Demo-PhotoManager-Workspace/
    └── Alice's Wedding/
        ├── project.json
        └── photos/
            ├── Cambodia139.jpg
            └── MTW-Hut.png

With:

    "image_folder": "photos"

and:

    "file": "Cambodia139.jpg"

the resulting image path is:

    Alice\'s\ Wedding/photos/Cambodia139.jpg

## Rationale

This convention provides a consistent method of locating project files and images while keeping projects portable.

It also means:

- Project directory names do not need to match the Project Name.
- The Project Name remains user-controlled through `workspace.event`.
- `project.json` does not contain machine-specific absolute paths.
- The application does not need to search the filesystem to determine where project images are located.
- The same convention can be used by project discovery, importing, editing, thumbnail handling and finalisation.
- A project remains valid even when it contains no downloaded photos.
- The first photo listed in `project.json` can be used as a representative thumbnail when one exists.

## Consequences

The Project Service can resolve project and image paths consistently from the location of `project.json` and the relative paths recorded in the project data.

Project discovery can locate projects by recursively searching for `project.json` files without making assumptions about project directory names.

The GUI does not need to understand the filesystem structure. It receives resolved paths through the appropriate application interfaces.

Any future changes to the project directory or image storage convention should be treated as an architectural decision and recorded accordingly.
