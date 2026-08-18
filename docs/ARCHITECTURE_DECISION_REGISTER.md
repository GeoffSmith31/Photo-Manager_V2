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

# ADR-008 — Retrieve Data Only When Required

**Status:** Accepted  
**Date:** 2026-08-17

## Context

Photo Manager V2 uses `project.json` as the authoritative record of project configuration and photo metadata.

The Orchestrator coordinates access to project data and maintains application state. It is tempting to retrieve additional photo data when a photo is first loaded, particularly data that might be useful for a later operation.

For example, a photo may contain latitude and longitude. The Editor needs to know whether a Maps action is available, but it does not initially need the actual latitude and longitude values.

If Orchestrator retrieves and retains those values when the photo is first loaded, they become a cached representation of authoritative project data. If the underlying project data subsequently changes, there is a risk that a later operation could inadvertently use the previously retrieved values rather than the current authoritative values.

This is particularly undesirable given the V1.0 experience, where cached data could result in the Editor displaying information that did not actually reflect the current contents of `project.json`.

## Decision

Orchestrator will retrieve **only the project and photo data required for the current operation**.

Data that is not required to perform the current operation will not be retrieved merely for possible future use.

### Project-level data

When a project is opened, Orchestrator will retrieve and retain the project-level information required for ongoing operation, including:

- Number of photos in the project.
- Metadata propagation policies.

This information remains valid for the duration of the open project and is required by Orchestrator for normal Editor operation.

### Photo-level data

When a photo is requested, Orchestrator will retrieve the photo data required to populate the Editor:

- Image filepath.
- Event.
- Year.
- Location.
- Info.
- Whether latitude/longitude data exists.

The actual latitude and longitude values will **not** be retrieved at this stage.

### Data required for later operations

If a later operation requires data that was not previously retrieved, Orchestrator will obtain that data from the Project Service at the time the operation is requested.

For example, when the user requests **Launch Google Maps**:

1. Editor reports the Maps request.
2. Orchestrator requests the current photo's latitude and longitude from the Project Service.
3. Orchestrator passes those current coordinates to Window Manager.
4. Window Manager opens the browser at the requested location.

This ensures that coordinates used to launch Maps are the current authoritative values rather than values previously retrieved and retained by Orchestrator.

## Consequences

### Positive

- `project.json` remains the authoritative source of project and photo data.
- Orchestrator cannot inadvertently use data it never retrieved.
- The risk of stale photo metadata being used by later operations is reduced.
- The Editor receives only the information it needs.
- Data retrieval remains closely associated with the operation that requires it.
- The architecture reinforces the V2 principle established after the V1.0 caching problems.

### Negative

- Some operations require an additional request to the Project Service.
- Orchestrator must explicitly identify what data each operation requires.
- An operation such as opening Google Maps requires a fresh project-data lookup rather than using data already available from the initial photo display.

## Architectural Principle

> **If Orchestrator does not need a value for the current operation, it does not retrieve it.**

When a value is required later, it is retrieved from the authoritative Project Service at the point where it is required.

This is intentional. It is preferable to perform an additional authoritative lookup than to risk treating previously retrieved data as current.
