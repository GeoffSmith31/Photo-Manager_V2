# Photo Manager V2
# Core Design Specification

Document Status: Draft
Document Version: 1.0

Defines:
    Core Design Version 1.0

Normative References:

CORE_IMPORTER_API_SPECIFICATION.md    Version 1.0
IMPORTER_SDK_SPECIFICATION.md         Version 1.0
PROJECT_JSON.md                       Version 2
SPECIFICATION_STYLE_GUIDE.md          Version 1.0

---

# 1. Purpose

This document defines the internal design and architecture of the Photo
Manager Core.

The Core is responsible for implementing the services defined by the
Core–Importer API Specification and managing all project state.

This specification describes the internal organisation of the Core,
including its components, responsibilities and interactions.

This document is intended for developers implementing or maintaining the
Photo Manager Core.

The internal implementation of the Core is independent of any
individual Importer.

---

# 2. Scope

This specification defines:

- Core architecture.
- Core components.
- Project lifecycle.
- Import workflow.
- State management.
- Window management.
- Metadata management.
- Importer management.
- Settings management.
- Error recovery.

This specification does not define:

- The Core–Importer API.
- The Importer SDK.
- Individual Importer implementations.
- The persistent Project Schema.
- User interface appearance.

These topics are defined by their respective specifications.

---

# 3. Architecture Overview

(Intentionally left blank.)

---

# 4. Design Goals

The Core has been designed according to the following principles.

- The Core owns all project state.
- The Core validates all persistent data.
- The Core implements the Core–Importer API.
- The Core coordinates Importers.
- The Core applies Metadata Policies.
- Components communicate through well-defined interfaces.
- Each Core component has a single well-defined responsibility.
- Core components SHALL NOT communicate directly with one another.
- All inter-component communication SHALL be coordinated by the
  Orchestrator.
- Internal implementation details remain hidden behind component
  boundaries.
- The architecture has been designed to support future extension without requiring modification of the Core–Importer API.

The Core is intended to provide a stable foundation for future versions
of Photo Manager.

---

# 5. Core Architecture

The Photo Manager Core is organised as a collection of cooperating
components.

Each component has clearly defined responsibilities and communicates
with other components through well-defined interfaces.

The Core is responsible for implementing the services defined by the
Core–Importer API Specification while maintaining all project state.

The architecture has been designed to separate user interface,
application logic and persistent project management.

The major Core components are:

- Application Controller
- Project Manager
- Importer Manager
- Metadata Manager
- State Manager
- Window Manager
- Settings Manager

The responsibilities of each component are described in the following
sections.

---

## 5.1 Component Relationships

The Photo Manager application is organised as a layered architecture.

The User Interface communicates with the Core through the
Orchestrator.

The Orchestrator coordinates all Core activity in response to user
actions and system events.

Core components do not communicate directly with one another.
All coordination between components is performed by the Orchestrator.

The following diagram illustrates the high-level relationships between
the principal application and Core components.

+--------------------------------------------------------------------------+
|                          13. User Interface                              |
|                                                                          |
|  +-------------------------+     +------------------------------------+  |
|  | 13.1 Control Tower      |     | 13.2 Editor                       |  |
|  +-------------------------+     +------------------------------------+  |
+--------------------------------------------------------------------------+
                                 |
                                 v
+--------------------------------------------------------------------------+
|                         6. Orchestrator                                 |
+--------------------------------------------------------------------------+
      |             |               |             |              |
      |             |               |             |              |
      v             v               v             v              v
+-------------+ +-------------+ +-------------+ +-------------+ +-------------+
| 7. Project  | | 8. Importer | | 9. Metadata | |10. State    | |11. Window   |
|   Manager   | |   Manager   | |   Manager   | |   Manager   | |   Manager   |
+-------------+ +-------------+ +-------------+ +-------------+ +-------------+
      |               |                                        |
      |               |                                        |
      |               |                                +----------------------+
      |               |                                | 12. Settings         |
      |               |                                |     Manager          |
      |               |                                +----------------------+
      |               |
      |               v
      |      +----------------------+
      |      | Core–Importer API    |
      |      +----------------------+
      |               |
      |               v
      |      +----------------------+
      |      |      Importer        |
      |      +----------------------+
      |
      v
+----------------------+
|     project.json     |
+----------------------+

The responsibilities of each component are described in the following
sections.

# 6. Orchestrator

## Purpose

The Orchestrator coordinates all activity within the Photo Manager Core.

The Orchestrator is responsible for managing application workflow,
coordinating Core components and responding to user actions and system
events.

The Orchestrator is the only component that coordinates communication
between Core components.

---

## Responsibilities

The Orchestrator is responsible for:

- Coordinating all Core workflow.
- Managing the application lifecycle.
- Receiving user requests from the User Interface.
- Coordinating project operations.
- Coordinating Importer operations.
- Coordinating Metadata operations.
- Coordinating Window operations.
- Coordinating application state changes.
- Coordinating application startup and shutdown.
- Handling unrecoverable errors.
- Determining the sequence in which Core components are invoked.

The Orchestrator SHALL NOT directly manipulate project data.

The Orchestrator SHALL delegate all specialised operations to the
appropriate Core component.

---

## Interactions

The Orchestrator communicates with all Core components.

Core components SHALL communicate only with the Orchestrator.

Core components SHALL NOT communicate directly with one another.

The Orchestrator is responsible for transferring information between
components where required.

---

## Managed Data

The Orchestrator maintains the current workflow context.

Persistent project data is managed by the Project Manager.

Application settings are managed by the Settings Manager.

The Orchestrator SHALL NOT directly manage persistent project data.

---

## Notes

The Orchestrator is the central coordinating component of the Photo
Manager Core.

The Orchestrator implements the workflow described by this
specification while ensuring that each Core component remains
independent and focused upon its individual responsibility.

# 7. Project Manager

## Purpose

The Project Manager is responsible for managing Photo Manager projects.

The Project Manager owns the project workspace and all persistent
project data.

The Project Manager is the only Core component permitted to create,
load, modify or save `project.json`.

---

## Responsibilities

The Project Manager is responsible for:

- Creating new projects.
- Opening existing projects.
- Validating project structure.
- Managing the project workspace.
- Loading `project.json`.
- Saving `project.json`.
- Maintaining project consistency.
- Managing project assets.
- Maintaining project status information.

The Project Manager SHALL be the sole owner of all persistent project
state.

---

## Interactions

The Project Manager communicates only with the Orchestrator.

The Project Manager SHALL NOT communicate directly with any other Core
component.

The Project Manager SHALL perform project operations only when
requested by the Orchestrator.

---

## Managed Data

The Project Manager owns:

- Project workspace.
- `project.json`
- Project asset directories.
- Project status.

The Project Manager SHALL be responsible for ensuring that persistent
project data remains valid and internally consistent.

---

## Notes

The Project Manager is responsible only for project management.

The Project Manager does not communicate with Importers, apply Metadata
Policies or manage application state.

Those responsibilities belong to other Core components and are
coordinated by the Orchestrator.

# 8. Importer Manager

## Purpose

The Importer Manager is responsible for discovering, loading and
managing Photo Manager Importers.

The Importer Manager provides the Core implementation of the
Core–Importer API and maintains the lifecycle of all Importers.

The Importer Manager is the only Core component permitted to communicate
directly with an Importer.

---

## Responsibilities

The Importer Manager is responsible for:

- Discovering available Importers.
- Loading Importers.
- Initialising Importers.
- Invoking Core–Importer API services.
- Managing Importer lifecycle.
- Receiving communications from Importers.
- Issuing commands to Importers.
- Validating Importer compatibility.
- Releasing Importer resources.

The Importer Manager SHALL NOT directly manage project data.

The Importer Manager SHALL implement the Core–Importer API on behalf of
the Core.

---

## Interactions

The Importer Manager communicates only with the Orchestrator and the
active Importer.

The Importer Manager SHALL NOT communicate directly with any other Core
component.

The Importer Manager SHALL perform Importer operations only when
requested by the Orchestrator.

---

## Managed Data

The Importer Manager owns:

- Importer instances.
- Importer lifecycle.
- Importer capability information.
- Importer compatibility information.

The Importer Manager SHALL NOT maintain project-specific state.

Project state is owned exclusively by the Project Manager.

---

## Notes

The Importer Manager is responsible only for management of Importers.

The Importer Manager does not determine application workflow.

The sequencing of Registration, Asset Transfer and recovery operations
is coordinated by the Orchestrator.

# 9. Metadata Manager

## Purpose

The Metadata Manager is responsible for processing metadata associated
with Photo Manager projects.

The Metadata Manager applies Metadata Policies, validates metadata and
coordinates metadata processing throughout the import workflow.

The Metadata Manager does not own project metadata.

Persistent metadata is owned by the Project Manager.

---

## Responsibilities

The Metadata Manager is responsible for:

- Applying Metadata Policies.
- Validating metadata.
- Initialising user-editable metadata.
- Updating metadata in accordance with Metadata Policies.
- Maintaining metadata consistency.
- Providing metadata processing services to the Core.

The Metadata Manager SHALL NOT directly modify `project.json`.

The Metadata Manager SHALL return processed metadata to the
Orchestrator.

---

## Interactions

The Metadata Manager communicates only with the Orchestrator.

The Metadata Manager SHALL NOT communicate directly with any other Core
component.

The Metadata Manager SHALL perform metadata processing only when
requested by the Orchestrator.

---

## Managed Data

The Metadata Manager owns:

- Metadata Policies.
- Metadata processing rules.
- Metadata validation rules.

Persistent metadata remains the responsibility of the Project Manager.

---

## Notes

The Metadata Manager is responsible only for metadata processing.

The Metadata Manager does not manage projects, communicate with
Importers or determine application workflow.

Those responsibilities belong to other Core components and are
coordinated by the Orchestrator.

# 10. State Manager

## Purpose

The State Manager is responsible for maintaining the current operational
state of the Photo Manager application.

The State Manager provides a single authoritative representation of the
application workflow state.

The State Manager does not manage persistent project state.

Persistent project state is owned by the Project Manager.

---

## Responsibilities

The State Manager is responsible for:

- Maintaining the current application state.
- Validating state transitions.
- Providing the current application state to the Orchestrator.
- Recording workflow progress.
- Providing state information to other Core components via the
  Orchestrator.

The State Manager SHALL NOT directly modify `project.json`.

The State Manager SHALL NOT determine application workflow.

---

## Interactions

The State Manager communicates only with the Orchestrator.

The State Manager SHALL NOT communicate directly with any other Core
component.

The State Manager SHALL update application state only when requested by
the Orchestrator.

---

## Managed Data

The State Manager owns:

- Current application state.
- Current workflow state.
- State transition rules.

The State Manager SHALL NOT maintain persistent project data.

---

## Notes

The State Manager provides a single source of truth for the operational
state of the application.

The State Manager does not coordinate workflow.

Workflow coordination is the responsibility of the Orchestrator.

# 11. Window Manager

## Purpose

The Window Manager is responsible for managing the behaviour of all
application windows.

The Window Manager provides a consistent interface for creating,
displaying, positioning and activating application windows.

The Window Manager does not determine application workflow.

---

## Responsibilities

The Window Manager is responsible for:

- Creating application windows.
- Displaying and hiding windows.
- Managing window placement, positioning and activation.
- Managing window focus.
- Managing modal dialogs.
- Managing window ownership.
- Coordinating interaction with external application windows.
- Providing window management services to the Core.

The Window Manager SHALL NOT determine when windows are displayed.

The Window Manager SHALL perform window operations only when requested
by the Orchestrator.

---

## Interactions

The Window Manager communicates only with the Orchestrator.

The Window Manager SHALL NOT communicate directly with any other Core
component.

The Window Manager SHALL perform window operations only when requested
by the Orchestrator.

---

## Managed Data

The Window Manager owns:

- Application window instances.
- Window state.
- Window ownership relationships.
- Window positioning information.

The Window Manager SHALL NOT maintain project-specific state.

---

## Notes

The Window Manager is responsible only for window management.

The Window Manager does not determine application workflow or user
interaction.

Those responsibilities belong to the Orchestrator.

The Window Manager MAY also coordinate the activation and focus of
external application windows where required to support an import
operation.

# 12. Settings Manager

## Purpose

The Settings Manager is responsible for managing the persistent
configuration of the Photo Manager application.

The Settings Manager owns all application settings and provides
configuration services to the Core.

The Settings Manager does not manage project-specific information.

---

## Responsibilities

The Settings Manager is responsible for:

- Loading application settings.
- Saving application settings.
- Validating application settings.
- Managing application configuration.
- Providing configuration information to the Orchestrator.
- Maintaining configuration consistency.

The Settings Manager SHALL be the sole owner of all persistent
application settings.

---

## Interactions

The Settings Manager communicates only with the Orchestrator.

The Settings Manager SHALL NOT communicate directly with any other Core
component.

The Settings Manager SHALL perform configuration operations only when
requested by the Orchestrator.

---

## Managed Data

The Settings Manager owns:

- Application configuration.
- User preferences.
- Importer configuration.
- Window preferences.
- Application defaults.

The Settings Manager SHALL NOT maintain project-specific state.

---

## Notes

The Settings Manager is responsible only for application configuration.

Project configuration is managed by the Project Manager.

The Settings Manager provides configuration information to the
Orchestrator, which coordinates its use by other Core components.

# 13. User Interface

## Purpose

The User Interface provides the primary means by which the user
interacts with the Photo Manager application.

The User Interface presents application information, accepts user
requests and displays the results of Core operations.

The User Interface does not directly communicate with Core components.

All interaction with the Core is coordinated by the Orchestrator.

---

## Responsibilities

The User Interface is responsible for:

- Presenting application information.
- Accepting user input.
- Displaying project information.
- Displaying application status.
- Displaying progress information.
- Presenting warnings and errors.
- Providing access to application functions.

The User Interface SHALL NOT implement application workflow.

Application workflow is coordinated by the Orchestrator.

---

## Components

The User Interface consists of the following principal components:

- Control Tower
- Editor

The responsibilities of each component are described in the following
sections.

## 13.1 Control Tower

### Purpose

The Control Tower provides the primary operational interface for the
Photo Manager application.

The Control Tower enables the user to create and manage projects,
initiate import operations, monitor application progress and access
application functions.

The Control Tower is intended to remain available throughout normal
application operation.

---

### Responsibilities

The Control Tower is responsible for:

- Creating and opening projects.
- Initiating import operations.
- Displaying application status.
- Displaying import progress.
- Displaying operational messages.
- Displaying warnings and errors.
- Providing access to application settings.
- Providing access to application Help.
- Launching the Editor.
- Displaying project summary information.

The Control Tower SHALL NOT implement application workflow.

Application workflow is coordinated by the Orchestrator.

---

### Interactions

The Control Tower communicates only with the Orchestrator.

The Control Tower SHALL NOT communicate directly with any Core
component.

The Control Tower SHALL request application operations by invoking the
appropriate services provided by the Orchestrator.

---

### Managed Data

The Control Tower does not own persistent application or project data.

The Control Tower maintains only the transient information required to
present the current operational state of the application.

---

### Notes

The Control Tower serves as the primary operational interface for Photo
Manager.

During an import operation, the Control Tower provides the principal
means by which the user monitors progress and responds to requests for
interaction.

## 13.2 Editor

### Purpose

The Editor provides the primary interface for viewing and modifying
project content.

The Editor enables the user to review imported assets, edit
user-maintained metadata and organise project information.

The Editor operates on the currently open project.

---

### Responsibilities

The Editor is responsible for:

- Displaying project assets.
- Displaying asset metadata.
- Supporting user modification of editable metadata.
- Displaying asset previews.
- Supporting asset search and filtering.
- Supporting asset selection.
- Displaying project statistics.
- Providing access to project editing functions.

The Editor SHALL NOT directly modify persistent project data.

Persistent project data is managed by the Project Manager.

---

### Interactions

The Editor communicates only with the Orchestrator.

The Editor SHALL NOT communicate directly with any Core component.

The Editor SHALL request project operations by invoking the appropriate
services provided by the Orchestrator.

---

### Managed Data

The Editor does not own persistent project data.

The Editor maintains only the transient information required to display
the current project and support user interaction.

---

### Notes

The Editor provides the primary working environment for managing a
Photo Manager project.

The Editor is responsible for presenting project information and
collecting user modifications.

Application workflow remains the responsibility of the Orchestrator.

# 14. Application Lifecycle

## Purpose

The Application Lifecycle defines the major operational phases of the
Photo Manager application.

The Orchestrator is responsible for coordinating transitions between
these phases.

The Application Lifecycle provides the overall framework within which
all Core operations are performed.

---

## Lifecycle Phases

The application operates through the following major phases:

1. Startup
2. Idle
3. Project Management
4. Import Operation
5. Project Editing
6. Project Finalisation
7. Shutdown

The detailed behaviour of each phase is described in the following
sections.

---

## 14.1 Startup

During startup the Orchestrator SHALL:

- Initialise Core components.
- Load application settings.
- Initialise the User Interface.
- Discover available Importers.
- Verify the application environment.
- Enter the Idle phase.

If startup cannot be completed successfully, the Orchestrator SHALL
present an appropriate error to the user and terminate the application.

---

## 14.2 Idle

During the Idle phase the application waits for user interaction.

The user MAY:

- Create a new project.
- Open an existing project.
- Modify application settings.
- Exit the application.

No import operation is active during the Idle phase.

---

## 14.3 Project Management

During the Project Management phase the user creates, opens or manages
Photo Manager projects.

The Orchestrator coordinates all project operations through the Project
Manager.

Successful completion of Project Management returns the application to
the Idle phase unless an Import Operation or Project Editing session is
initiated.

---

## 14.4 Import Operation

During an Import Operation the Orchestrator coordinates all interaction
between the User Interface, the Core and the active Importer.

The detailed Import Workflow is described in Section 15.

---

## 14.5 Project Editing

During Project Editing the user interacts with the Editor to review and
modify project information.

The Orchestrator coordinates all editing operations through the
appropriate Core components.

---

## 14.6 Project Finalisation

Project Finalisation marks the completion of work on the active
project.

During Project Finalisation, the Orchestrator coordinates the orderly
completion of the project through the Project Manager.

The Project Manager SHALL perform any actions required to complete the
project in accordance with the user's selected options.

Following successful finalisation, the application SHALL return to the
Idle phase.

The detailed behaviour of Project Finalisation is implementation
defined.

## 14.7 Shutdown

During shutdown the Orchestrator coordinates the orderly termination of
all application components.

Shutdown SHALL include:

- Completion or cancellation of any active operations.
- Saving application settings.
- Releasing application resources.
- Closing application windows.
- Terminating the application.
