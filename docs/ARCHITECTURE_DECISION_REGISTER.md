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

## ADR-009 — Photo Manager UserComment Format

**Status:** Accepted

**Date:** 2026-08-24

### Context

Photo Manager writes the approved photo metadata to the image file's EXIF `UserComment` field.

A consistent format is required so that:

- the information is readable in external photo applications;
- the format remains compatible with software that may have limited character support;
- the format can potentially be recognised by future Photo Manager importers;
- empty metadata fields can be represented without unnecessary separators.

The `project.json` file remains the authoritative Photo Manager record. The EXIF `UserComment` is a representation of the approved metadata written into the image.

### Decision

Photo Manager will write the following metadata fields to EXIF `UserComment` in this order:

1. Event
2. Year
3. Location
4. Info

The format is:

    <Event> | <Year> | <Location> | <Info>

The separator is a vertical bar with one space on each side:

    " | "

The string is constructed by concatenating the non-empty fields in order.

The separator is inserted before each non-empty field except the first non-empty field.

For example:

    RACAL Course | 1984 | North Ryde | Medport manufacturers course

If a field is empty, it is omitted rather than producing an empty field between separators.

For example:

    RACAL Course | 1984 | Medport manufacturers course

If only Event and Info are populated:

    RACAL Course | Medport manufacturers course

If all fields are empty, the UserComment is an empty string.

### Rationale

The `|` character is visually unambiguous and is unlikely to occur in normal user-entered metadata.

Spaces around the separator improve readability when the UserComment is displayed by external applications such as Kodi.

The format uses ordinary text characters rather than unusual Unicode punctuation, reducing the possibility of compatibility problems with external applications.

The format is primarily intended as a human-readable representation of Photo Manager metadata within the image. Photo Manager does not depend on reconstructing its metadata from the UserComment.

### Consequences

The `|` character is effectively reserved as the UserComment field separator.

Because empty fields are omitted, the UserComment does not necessarily contain enough information to determine which of the four metadata fields were originally empty. This is acceptable because `project.json` remains the authoritative Photo Manager record.

Future importers may recognise and use the Photo Manager UserComment format, but this is not a requirement of the current EXIF implementation.

Future decisions concerning other EXIF metadata, such as creation dates, GPS data, or preservation of camera-specific metadata, will be recorded separately.

### Character set

Some display systems support a limited character set, so to allow comments to be correctly displayed, the input fields are limited to the following characters:
A-Z
a-z
0-9
space
. , ' " - ( ) [ ] / & + = ? ! % @ _ * : #

# ADR-010 — External Browser Integration for Google Maps

**Status:** Accepted  
**Date:** 2026-08-26

## Context

Photo Manager provides a Google Maps button in the Photo Editor for photographs that contain GPS coordinates.

The application should open the photo's location in a web browser. The browser is an optional external capability and must not be a prerequisite for running Photo Manager.

The application should be portable across systems where different supported browsers may be installed.

When Photo Manager opens Google Maps, the browser window is associated with the currently displayed photo. The browser remains available while the user examines the location.

When a different photo or Activity is presented, the Google Maps browser window opened by Photo Manager is closed. A subsequent Maps request opens a new browser window for the newly displayed photo.

The user may also close the Maps browser window independently of Photo Manager. This is not an error condition.

## Decision

Photo Manager will support Google Maps through an externally installed web browser.

The application will:

1. Discover supported browsers using the system environment rather than assuming a fixed executable path.
2. Initially support:
   - Google Chrome
   - Firefox
3. Select an available supported browser according to the application's defined preference order.
4. Allow Photo Manager to operate normally when no supported browser is installed.
5. Report an error only when the user attempts to use the Maps function and no supported browser is available.
6. Open a dedicated browser window for Google Maps when the Maps function is used.
7. Maintain a reference to the browser process/window opened by Photo Manager.
8. Associate the browser window with the currently displayed photo.
9. Allow the user to use the Maps browser independently while the current photo remains displayed.
10. Close the Maps browser window before Window Manager presents a different photo or Activity.
11. Treat a Maps browser that has already been closed by the user as a normal condition.
12. Open a new Maps browser window when the Maps function is subsequently requested.

The responsibility for the feature is divided as follows:

### Editor

The Editor provides the Maps button and emits the `Maps` action when the user clicks it.

The Maps button is disabled when the current photo has no GPS coordinates.

### Orchestrator

The Orchestrator handles the `Maps` action.

It obtains the current photo's latitude and longitude from the Project Service and requests that the Window Manager display the location.

The Orchestrator does not manage the browser process or window.

### Project Service

The Project Service provides the latitude and longitude for the requested photo.

It does not construct browser URLs or interact with the browser.

### Window Manager

The Window Manager owns browser discovery, browser launching, and the lifecycle of the Google Maps browser window.

It:

- determines which supported browser is available;
- launches the selected browser when required;
- retains the browser process/window reference;
- closes the Maps browser before presenting a different photo or Activity;
- safely handles a browser that has already been closed by the user;
- presents the requested application Activity after Maps cleanup has been completed.

Window Manager is also responsible for using the appropriate browser-launch mechanism for the current operating system.

### Multi-OS Support

Operating-system-specific browser discovery and launching behaviour will be contained within `multi_os.py` where practical.

The remainder of the application should use OS-independent interfaces provided by the multi-OS layer.

### Constants

The supported browser definitions will be maintained in `constants.py`.

The browser list will contain the supported browser names and the platform-specific executable names or identifiers required for discovery.

The order of the list defines the browser preference order.

## Error Handling

The absence of a supported browser is not an application startup error.

If the user selects the Maps function when no supported browser is available, Photo Manager will display a user-facing error explaining that Google Maps cannot be opened.

Browser discovery, launch, or process-management failures will be logged and reported to the user through the normal Window Manager user-interaction mechanism where appropriate.

A browser that has already been closed by the user is not an error condition.

A photo without GPS coordinates is not an error condition; the Maps button is disabled for such photos.

When Window Manager is asked to present a new photo or Activity, failure to close an already-terminated Maps browser is not an error.

## Rationale

Treating the browser as an optional capability allows Photo Manager to operate normally on systems without a supported browser while still providing useful feedback when the Maps function is requested.

Browser discovery avoids platform-specific assumptions about executable locations and allows the application to operate in different environments.

Associating the Maps browser with the currently displayed photo avoids the complexity of communicating with and navigating an existing browser window when the user moves to another photo.

Closing the Maps browser before presenting a different photo or Activity provides deterministic behaviour: the browser always represents the location of the photo for which it was opened.

Keeping browser interaction within the Window Manager preserves the application's architectural separation:

- the Project Service manages project data;
- the Orchestrator coordinates operations;
- the Window Manager manages application windows and external browser windows;
- the multi-OS layer contains operating-system-specific implementation details;
- constants define the supported browser configuration.

# ADR-011 — Finalise Workflow and Safety Model

**Status:** Accepted  
**Date:** 2026-08-30

## Context

Finalise is the process used to complete a Photo Manager project and transfer its project photos to a user-selected destination.

Finalise may involve a substantial number of filesystem operations and may take significant time on large projects. It also performs destructive operations during project cleanup.

The workflow therefore needs:

- clear and continuous user-visible activity;
- safe handling of missing or unexpected files;
- explicit user approval at appropriate decision points;
- validation of the destination before copying;
- deterministic filename collision handling;
- a clearly defined point at which Finalise becomes non-interruptible; and
- a fail-safe cleanup sequence that prevents an incomplete project from subsequently being opened for editing.

## Decision

Finalise will be implemented as a dedicated workflow coordinated by the Orchestrator and presented as a Control Tower Activity.

The responsibilities are divided as follows:

- **Orchestrator** — coordinates the workflow, manages application state and user decisions, and controls transitions.
- **Finalise Service** — performs project analysis, filename processing, copying, verification and filesystem cleanup.
- **Window Manager** — provides user interaction and Activity presentation.
- **Activity Panel** — provides continuous observable progress during Finalise.

The Finalise Service will not directly control application workflow or GUI state.

---

## Finalise Workflow

```text
EDITING
   │
   │ Finalise requested
   ▼
FINALISE — PREPARATION
   │
   ▼
PROJECT INTEGRITY CHECK
   │
   ├── Unexpected files
   │       │
   │       └── STOP
   │
   ├── Missing project files
   │       │
   │       └── Warn user
   │             ├── Cancel
   │             └── Continue
   │
   ▼
CHECK EDIT STATUS
   │
   ├── Unedited photos
   │       │
   │       └── Warn user
   │             ├── Cancel
   │             └── Continue
   │
   ▼
SELECT DESTINATION
   │
   ├── Cancel → EDITOR
   │
   ▼
VALIDATE DESTINATION
   │
   ├── Invalid → inform user → EDITOR
   │
   ▼
ANALYSE FILENAMES
   │
   ├── No collisions
   │
   └── Collisions
          │
          ▼
     PRESENT PROPOSED
     FILENAMES
          │
          ├── Cancel → EDITOR
          │
          └── Accept
                 │
                 ▼
════════════════════════════════════
        NON-INTERRUPTIBLE PHASE
════════════════════════════════════
                 │
                 ▼
            COPY PHOTOS
                 │
                 ▼
          VERIFY COPIES
                 │
                 ▼
          DELETE project.json
                 │
                 ▼
          DELETE SOURCE PHOTOS
                 │
                 ▼
        REMOVE PROJECT DIRECTORY
                 │
                 ▼
          FINALISE COMPLETE
                 │
                 ▼
        PROJECT SELECTION
```

---

## Project File Integrity

The filenames recorded in `project.json` are the authoritative list of project photos.

The actual contents of the project's image directory are compared against this list.

### Missing Project Photos

A registered project photo that is missing from the image directory does **not** prevent Finalise from completing.

The user is shown the filenames of the missing photos and may either:

- cancel Finalise and attempt to recover the files; or
- continue Finalise without the missing photos.

If the user continues, the missing photos are not copied.

### Unexpected Files

Files found in the project image directory that are not registered in `project.json` are considered unexpected files.

Unexpected files are a **hard stop**.

The filenames of all unexpected files are displayed to the user. The user must manually remove or relocate them before attempting Finalise again.

Photo Manager must never silently:

- delete unexpected files;
- move unexpected files; or
- copy unexpected files as part of Finalise.

---

## Unedited Photos

Before Finalise proceeds to the destination-selection stage, the Orchestrator requests the list of unedited photos from the Project Service.

If unedited photos exist, the user is warned and shown the number of affected photos.

The user may:

- cancel Finalise; or
- continue despite the unedited photos.

If no unedited photos exist, Finalise continues without user intervention.

---

## Destination Selection and Validation

The user selects the destination directory through the Window Manager.

If the user cancels the directory selection, Finalise is cancelled and the existing Editor Activity is restored, preferably showing the photo that was being edited when Finalise was requested.

After selection, the destination is independently validated.

The destination must:

- exist;
- be a directory; and
- be writable by the application.

Actual write capability should be tested rather than relying solely on filesystem permission bits.

An invalid destination prevents Finalise from proceeding and returns the user to the Editor Activity.

---

## Filename Collision Handling

Filename analysis occurs before any files are modified.

Only filenames registered in `project.json` are considered for copying.

If a proposed destination filename already exists, a new filename is generated by appending an incrementing integer.

For example:

```text
IMG001.jpg
IMG001_1.jpg
IMG001_2.jpg
IMG001_3.jpg
```

The process continues until a non-conflicting filename is found.

All proposed filename changes are presented to the user before copying begins.

No source files are renamed until the user has accepted the proposed changes.

If the user cancels the collision approval, Finalise is cancelled and the existing Editor Activity is restored, preferably showing the current photo.

Filename collision detection will be case-insensitive. Photo Manager will treat filenames that differ only in character case as conflicting, regardless of the case-sensitivity characteristics of the underlying filesystem.

Case normalisation is used only for collision comparison. Original filename spelling and case are preserved in source and proposed destination filenames.

---

## Activity Panel and Progress Reporting

Finalise will be presented as a Control Tower Activity.

The Activity Panel will provide continuous observable progress during potentially lengthy operations.

There should be no intentional period of more than approximately 0.5 seconds without an observable activity or progress update during a long-running operation.

Finalise activities include:

1. Checking project
2. Checking project photos
3. Checking edit status
4. Selecting destination
5. Validating destination
6. Analysing filenames
7. Resolving filename conflicts
8. Copying photos
9. Verifying copied photos
10. Removing project files
11. Removing source photos
12. Completing Finalise

Long-running operations must provide meaningful progress information and must not block the Qt event loop.

For example:

```text
FINALISE

Copying photos

83 / 184

Current file:
IMG0083.jpg

████████████████░░░░
```

Where practical, individual large-file copies should report byte-level progress.

Finalise progress should be communicated through a structured progress interface rather than arbitrary GUI updates.

---

## User Cancellation

During the preparation and user-decision phase, cancellation returns the user to the existing project's Editor Activity.

Where possible, the Editor should reopen on the photo that was current when Finalise was requested.

Cancellation applies to:

- missing-photo warnings;
- unedited-photo warnings;
- destination selection;
- filename collision approval; and
- other user-decision points before copying begins.

The project remains loaded and unchanged.

---

## Non-Interruptible Execution Phase

Once actual copying begins, Finalise enters the non-interruptible execution phase.

The normal **Close** action is removed or disabled.

**Settings** is also removed or disabled.

**Help** remains available.

The user cannot cancel Finalise through the normal Action Bar during:

- copying;
- verification;
- deletion of `project.json`;
- deletion of source photos; or
- project-directory cleanup.

This prevents the application from being deliberately interrupted during operations that may leave the project in an intermediate state.

---

## Destructive Safety Boundary

The original project remains intact until all destination files have been successfully copied and verified.

The destructive sequence is strictly:

```text
COPY
  ↓
VERIFY
  ↓
DELETE project.json
  ↓
DELETE SOURCE PHOTOS
  ↓
REMOVE PROJECT DIRECTORY
```

`project.json` is deliberately deleted **before** the source photos.

If the application crashes after `project.json` has been deleted but before cleanup is complete:

- the project cannot subsequently be selected for editing;
- some source files may remain and require manual filesystem cleanup; and
- Photo Manager cannot open an incomplete or potentially inconsistent project.

This behaviour is considered safer than allowing a partially cleaned project to remain selectable.

---

## Completion

After successful cleanup:

1. Finalise reports completion.
2. The Orchestrator clears the active project.
3. Available projects are rediscovered.
4. The application returns to Project Selection.

The Finalise Service does not directly initiate Project Selection.

The transition is coordinated by the Orchestrator.

---

## Architectural Responsibility

```text
                    ORCHESTRATOR
                         │
             coordinates workflow
                         │
                         ▼
                  FINALISE SERVICE
                         │
          ┌──────────────┴──────────────┐
          │                             │
    filesystem work              progress events
          │                             │
          │                             ▼
          │                       ORCHESTRATOR
          │                             │
          │                             ▼
          │                      WINDOW MANAGER
          │                             │
          │                             ▼
          │                      ACTIVITY PANEL
          │
          ▼
    Source / Destination
```

The governing responsibility boundary is:

> **The Finalise Service performs the work; the Orchestrator coordinates it; the Window Manager presents it.**

# ADR-012 — Standalone Importers and Project JSON Contract

**Status:** Accepted
**Date:** 2026-10-18

## Context

The original Photo Manager V2 architecture defined a direct interface between the Photo Manager Core and Importers. This relationship was documented in the Core–Importer API Specification and supported by the Importer SDK Specification.

The architecture has since been redesigned. Importers now operate as standalone applications that communicate with their respective source systems, acquire photo assets, and produce Photo Manager projects.

Photo Manager consumes these projects for project management, photo editing and metadata processing. It does not require a direct API connection to the Importer that created a project.

The `project.json` file provides the persistent representation of a project and defines the data exchanged between an Importer and Photo Manager.

## Decision

The `project.json` format is the sole contract between an Importer and Photo Manager.

Importers SHALL produce projects that conform to the applicable Project JSON schema. Photo Manager SHALL interpret those projects according to the same contract.

No shared Core–Importer API or Importer SDK is required.

The Project JSON Reference is the authoritative developer reference for the structure, field definitions and constraints of `project.json`. The schema version identifies the version of the project format to which the file conforms.

The following specifications are superseded by this decision:

- `CORE-IMPORTER_API_SPECIFICATION` — the direct Core–Importer API it defines is no longer part of the adopted architecture.
- `IMPORTER_SDK_SPECIFICATION` — the SDK and plugin integration model it defines is no longer required.

These specifications are retained as historical records of the previous architecture. They are not authoritative for new development.

## Rationale

Using `project.json` as the integration contract separates Importer implementation from Photo Manager's internal architecture.

This allows Importers to be developed, tested and operated independently, provided their output conforms to the agreed project format.

It also establishes a single authoritative contract for the data required by Photo Manager, avoiding the need to maintain separate API, SDK and project-format specifications for the Importer–Photo Manager relationship.

## Consequences

- Importers do not need to implement the former Core–Importer API or SDK.
- Photo Manager does not need a direct runtime connection to an Importer.
- Importer compatibility is determined by conformance to the applicable Project JSON schema.
- Changes to the shared data contract must be reflected in the Project JSON specification and reference documentation.
- The Core–Importer API Specification and Importer SDK Specification remain available for historical reference but must not be used as requirements for new development.
- Importer-specific implementation details and source-system interactions remain the responsibility of each Importer and are outside the shared project-format contract.
