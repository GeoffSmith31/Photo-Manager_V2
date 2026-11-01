# Photo Manager V2
# Core Design Specification

Document Status: Draft
Document Version: 1.2

Defines:
    Core Design Version 1.0

Normative References:

CORE_IMPORTER_API_SPECIFICATION.md    Version 1.2
IMPORTER_SDK_SPECIFICATION.md         Version 1.2
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

# 3. Core Architecture Overview

The Photo Manager Core is organised as a collection of cooperating
components, each with a defined responsibility.

The components work together to provide the complete Photo Manager
application while maintaining clear separation between workflow
coordination, project management, importer management, user
interaction, application state, configuration and diagnostic logging.

The Core is responsible for coordinating the application as a whole.
Individual components remain responsible for the functions assigned to
them and SHALL NOT assume ownership of responsibilities assigned to
other components.

The Core also provides the boundary between the Photo Manager
application and external Importers. Importers are treated as external
components and communicate with the Core through the interfaces defined
by the Core–Importer API Specification.


## 3.1 Architectural Model

The Core uses a layered and component-based architecture.

At the highest level, the application consists of:

- Application services that establish and manage the running
  application.
- Coordination services that control workflow and component
  interaction.
- Project services that create, load, validate and maintain projects.
- Importer services that discover, validate, select and activate
  Importers.
- User-interface components that present information and accept user
  actions.
- Supporting services that provide application state, configuration and
  logging.

The architecture is intended to ensure that workflow decisions are made
by the Orchestrator, persistent project state is managed by the Project
Manager and source-specific behaviour remains within the Importer.

The Core components communicate through defined interfaces rather than
by directly manipulating state owned by another component.


## 3.2 Core Components

The principal components of the Core are described below.

### 3.2.1 Application

The Application is responsible for establishing and terminating the
Photo Manager application.

It creates and connects the principal Core components and provides the
top-level application environment in which they operate.

The Application is responsible for application startup and shutdown but
does not own project workflow.

### 3.2.2 Orchestrator

The Orchestrator coordinates activity within the Photo Manager Core.

It is responsible for:

- Controlling the overall application workflow.
- Coordinating the activities of Core components.
- Responding to user actions that require workflow changes.
- Initiating project creation, loading and editing operations.
- Coordinating Importer selection and activation.
- Coordinating registration and acquisition operations.
- Managing transitions between application states and workflow stages.
- Determining the appropriate response to operational conditions and
  failures.

The Orchestrator coordinates these activities but does not replace the
services responsible for performing them.

For example, the Orchestrator may instruct the Project Manager to create
or load a project, but the Project Manager remains responsible for the
project operation itself.

The Orchestrator is also responsible for maintaining the distinction
between application state and project workflow stage.


### 3.2.3 Project Manager

The Project Manager is responsible for managing Photo Manager projects.

It is responsible for:

- Discovering available projects.
- Creating new project workspaces.
- Loading existing projects.
- Validating project data.
- Maintaining `project.json`.
- Persisting project changes.
- Managing project-level workflow information.
- Providing project information required by other Core components.

The Project Manager is the Core authority for persistent project state.

Other components SHALL NOT directly modify `project.json`.

The Project Manager does not determine the overall application workflow.
Workflow decisions remain the responsibility of the Orchestrator.


### 3.2.4 Importer Manager

The Importer Manager is responsible for managing Photo Manager
Importers.

It is responsible for:

- Discovering available Importers.
- Validating discovered Importers.
- Obtaining Importer capability information.
- Maintaining the collection of available Importers.
- Selecting an Importer for an import operation.
- Activating and initialising the selected Importer.
- Providing the Orchestrator with access to the selected Importer.

Importer discovery is separate from Importer activation.

Discovery SHALL NOT require connection to the Importer's source system,
authentication with the source system, source enumeration or asset
acquisition.

The Importer Manager does not own project state or import workflow.
Those responsibilities remain with the Project Manager and Orchestrator
respectively.


### 3.2.5 Project Selection

Project Selection provides the user interface and supporting logic
required to select an existing project or request creation of a new
project.

It presents the projects made available by the Project Manager and
communicates the user's selection to the Orchestrator.

Project Selection does not load or modify project data directly.


### 3.2.6 Control Tower

The Control Tower provides operational visibility and control for the
currently active Core operation.

It presents information such as:

- Current application state.
- Current workflow stage.
- Current activity.
- Operational status.
- Importer activity.
- Errors, warnings and actions requiring user attention.

The Control Tower communicates user control requests to the Orchestrator
and receives operational information from the Core.

The Control Tower does not own workflow state or project state.


### 3.2.7 Editor and User Interaction

The Editor and other user-interface components provide the user's
interaction with an active project.

They allow the user to view and modify information that the Core makes
available for editing.

User-interface components SHALL request project operations through the
appropriate Core services rather than directly modifying persistent
project data.

User interaction does not determine application workflow independently.
Workflow-changing actions are communicated to the Orchestrator.


### 3.2.8 Application State and Workflow Stage

The Core maintains two related but distinct concepts of state.

Application State represents the current operational state of the
running application.

Workflow Stage represents the current progress of the active project
through the Photo Manager workflow.

These concepts SHALL remain distinct.

A change in Application State does not necessarily imply a corresponding
change in Workflow Stage, and a change in Workflow Stage does not
necessarily imply an immediate change in Application State.

The Orchestrator controls both in accordance with the current
application operation.


### 3.2.9 Settings Manager

The Settings Manager provides access to application configuration required
by the Core.

The Settings Manager manages application-level settings and environment
information rather than project-specific persistent state.

Components SHALL obtain configuration through the Settings Manager
service rather than maintaining independent copies of application
settings.

### 3.2.10 Logging Manager

The Logging Manager provides application-wide diagnostic and operational
logging.

It records information required to understand application activity,
including:

- Normal operational events.
- Workflow activity.
- Warnings.
- Errors.
- Diagnostic information.

Components SHALL use the Logging Manager service for application
diagnostics rather than implementing independent logging mechanisms.

Logging does not determine workflow or application state.


### 3.2.11 Finalise Services

Finalise services provide the operations required to complete a project
and transfer its processed assets to the user-selected destination.

Finalise operations are initiated and coordinated by the Orchestrator.

Finalise services are responsible for performing the finalisation
operation but do not own overall application workflow.


## 3.3 Component Interaction

The Core components cooperate through the Orchestrator.

The general relationship between the principal components is:

```text
                         +----------------+
                         |      User      |
                         +-------+--------+
                                 |
                                 v
              +-------------------------------------+
              |         User Interface Layer        |
              |                                     |
              | Project Selection | Control Tower   |
              | Editor            | Other UI        |
              +-------------------+-----------------+
                                  |
                                  v
                         +----------------+
                         |  Orchestrator  |
                         +-------+--------+
                                 |
             +-------------------+-------------------+
             |                   |                   |
             v                   v                   v
     +---------------+   +---------------+   +---------------+
     | Project       |   | Importer      |   | Application   |
     | Manager       |   | Manager       |   | Services      |
     +-------+-------+   +-------+-------+   +---------------+
             |                   |
             v                   v
       `project.json`        Importer
                                 |
                                 v
                          +-------------+
                          | Source      |
                          | System      |
                          +-------------+

             +-------------------+-------------------+
             |                   |                   |
             v                   v                   v
     Settings Manager     Logging Manager      State / Workflow

```
The diagram is conceptual rather than a statement of implementation
mechanism.

The Orchestrator is the principal coordinator, but the architecture does
not require every interaction between components to pass directly
through the Orchestrator.

Where a component requires a service owned by another component, the
interaction SHALL use the appropriate service interface and SHALL
respect ownership boundaries.


## 3.4 Workflow Coordination

The Orchestrator coordinates the major application workflows.

A typical new-project import operation involves the following
coordination:

1. The user requests creation of a new project.
2. The Orchestrator coordinates Importer selection.
3. The Importer Manager discovers, validates and activates the selected
   Importer as required.
4. The Importer performs any required source interaction.
5. When sufficient project information is available, the Importer
   invokes CORE-001 Create Project.
6. The Project Manager creates and initialises the project.
7. The Importer registers assets through the Core–Importer API.
8. The Core records the registration results in the project.
9. Once registration is complete, the Core coordinates asset
   acquisition.
10. The Core records acquisition results and manages any required
    recovery or retry.
11. When the project reaches the appropriate workflow state, the
    Orchestrator makes it available for the next application operation.

The Orchestrator coordinates this sequence but does not perform
source-specific operations, direct project-file manipulation or asset
acquisition itself.

For an existing project, the Orchestrator instead coordinates loading
and validation of the project, determines whether incomplete workflow
remains, and resumes the appropriate operation where required.


## 3.5 Core–Importer Boundary

Importers are external components from the perspective of the Core.

The Core owns:

- Application workflow.
- Project state.
- Persistent project data.
- Project validation.
- Registration state.
- Acquisition state.
- Acquisition sequence.
- Retry policy.
- Overall operation completion.
- User-facing Core workflow.

The Importer owns:

- Communication with the source system.
- Source authentication and source-specific interaction.
- Source enumeration.
- Translation of source information into the canonical Photo Manager
  model.
- Asset registration requests.
- Asset acquisition.
- Source-specific resources and temporary source state.

The Core and Importer communicate exclusively through the interfaces
defined by the Core–Importer API Specification.

The Core SHALL NOT depend on source-specific implementation details.

The Importer SHALL NOT access or modify `project.json` directly.

During a new import, the Importer invokes CORE-001 Create Project and
subsequently invokes CORE-002 Register Asset as required by the import
operation.

During acquisition, the Core requests individual assets and the
Importer returns the corresponding Asset Data.

The Core remains responsible for recording the result of each operation
and determining what operation occurs next.

For each IMPORTER-001 operation that requires source communication, the
Core SHALL supply the source information required to establish or restore
source communication as part of that operation.

The source information consists of:

- `source`;
- `source_id`; and
- `source_title`.

If the Importer cannot establish the required source connection, the
Importer SHALL return a failed Result and SHALL report any relevant
runtime condition using CORE-004 Communications where appropriate.

This boundary allows source-specific implementation to remain within
Importers while the Core maintains a consistent project and workflow
model for all supported source systems.


## 3.6 Architectural Ownership

The following ownership rules apply throughout the Core architecture.

- The Orchestrator owns workflow coordination.
- The Project Manager owns persistent project state.
- The Importer Manager owns Importer discovery and activation.
- User-interface components own presentation and user interaction.
- Application State and Workflow Stage are maintained by the Core and
  coordinated by the Orchestrator.
- The Settings Manager owns application configuration.
- The Logging Manager owns application diagnostics and logging.
- Importers own source-specific communication and acquisition.
- No component SHALL directly modify state owned by another component
  except through the defined service interface.

These ownership boundaries are intended to keep the Core modular and to
allow individual components to evolve without transferring their
responsibilities to unrelated components.

Detailed behaviour and implementation requirements for each component are
defined in the subsequent sections of this specification.
---

# 4. Design Goals

The Photo Manager Core architecture has been designed to achieve the
following goals.

- Provide a clear separation of responsibilities between Core
  components.
- Keep application workflow coordination separate from the services that
  perform individual operations.
- Maintain clear ownership of persistent project state.
- Keep source-specific behaviour within Importers.
- Provide a stable and well-defined boundary between the Core and
  Importers.
- Keep user-interface components separate from project and workflow
  management.
- Maintain a clear distinction between Application State and Workflow
  Stage.
- Ensure that recovery and retry decisions remain under Core control.
- Allow Core components to evolve independently while maintaining their
  defined interfaces and responsibilities.
- Minimise direct dependencies between components.
- Prevent components from directly modifying state owned by another
  component.
- Provide sufficient diagnostic information to understand application
  activity and failures.
- Support the addition of future Importers without requiring changes to
  source-independent Core functionality.
- Maintain the integrity and consistency of persistent project data.
- Keep implementation details out of the public Core–Importer
  interface.

The architecture should favour simple, explicit component interactions
over implicit dependencies or duplicated responsibility.

Where a responsibility can be clearly assigned to one component, that
component SHALL remain the authoritative owner of that responsibility.

The architecture should also allow future functionality to be added
without unnecessarily changing the responsibilities or interfaces of
existing components.

---

# 5. Architectural Principles

The following principles govern the design and implementation of the
Photo Manager Core.

## 5.1 Clear Responsibility

Each Core component SHALL have a clearly defined responsibility.

A component SHALL NOT assume responsibility for functions that belong to
another component.

Where responsibilities overlap, the owning component SHALL remain the
authoritative source for the affected state or behaviour.

## 5.2 Explicit Ownership

Persistent data and application state SHALL have a clearly defined
owner.

Components SHALL NOT directly modify state owned by another component
except through the defined interface or service provided by that
component.

The Project Manager is the authoritative owner of persistent project
state.

The Orchestrator is the authoritative coordinator of application
workflow.

## 5.3 Coordination and Execution are Separate

The Orchestrator SHALL coordinate application activity but SHALL NOT
perform operations that belong to specialised components.

For example, the Orchestrator may coordinate project creation,
Importer activation or asset acquisition without itself implementing
the source-specific or project-storage operations required to perform
those activities.

This separation keeps workflow logic independent from implementation
details.

## 5.4 Separation of Source-Specific Behaviour

Source-specific behaviour SHALL remain within Importers.

The Core SHALL operate on the canonical Photo Manager model and SHALL
NOT contain assumptions about the implementation or behaviour of a
particular source system.

This principle allows additional Importers to be added without
introducing source-specific logic into the Core.

## 5.5 Separation of User Interaction

User-interface components SHALL be responsible for presenting
information and receiving user interaction.

They SHALL NOT become the authoritative owner of project state or
workflow state.

User interaction SHALL cause the appropriate Core service or workflow
operation to be invoked.

## 5.6 Application State and Workflow Stage

Application State and Workflow Stage SHALL remain distinct concepts.

Application State represents the current operational condition of the
application.

Workflow Stage represents the progress of the active project through
the application workflow.

A change in one SHALL NOT be assumed to imply an immediate change in
the other.

The Orchestrator coordinates both.

## 5.7 Persistent State and Recovery

The Core SHALL maintain sufficient persistent information to determine
the state of an incomplete operation after application restart.

Recovery decisions SHALL be made by the Core.

Importers MAY maintain temporary runtime state required to communicate
with their source system, but SHALL NOT become the authoritative owner
of persistent project recovery state.

## 5.8 Stable Interfaces

Interfaces between Core components SHALL be explicit and stable.

Internal implementation details SHALL NOT become implicit dependencies
between components.

The Core–Importer boundary SHALL be defined by the Core–Importer API
Specification rather than by assumptions about a particular Importer
implementation.

## 5.9 Validation at Ownership Boundaries

A component SHALL validate data for which it is responsible before that
data becomes authoritative within its domain.

The Core SHALL validate persistent project data before committing it to
the project.

Importers SHALL validate source-specific information sufficiently to
ensure that it can be translated into the canonical Photo Manager
model.

## 5.10 Controlled Extension

New functionality SHOULD be added by extending the appropriate
component or service rather than by transferring responsibility to an
unrelated component.

New components or interfaces SHOULD be introduced only where they
provide a clear architectural responsibility.

The architecture SHALL favour explicit and understandable interactions
over unnecessary abstraction or indirection.

---

# 6. Orchestrator

The Orchestrator is the principal workflow coordination component of the
Photo Manager Core.

It coordinates the activities of other Core components and controls the
progress of the application through its defined workflow.

The Orchestrator does not own the persistent project data, Importer
implementation, user-interface presentation or source-specific
operations performed by an Importer.

The Orchestrator SHALL coordinate these operations through the
appropriate Core services and component interfaces.


## 6.1 Responsibilities

The Orchestrator is responsible for:

- Coordinating the overall application workflow.
- Maintaining the current Application State.
- Maintaining the current Workflow Stage.
- Responding to workflow-changing user actions.
- Coordinating project creation.
- Coordinating project loading and validation.
- Coordinating Importer selection and activation.
- Coordinating registration and acquisition operations.
- Coordinating recovery of incomplete operations.
- Coordinating finalisation of completed projects.
- Determining the next workflow operation following completion,
  failure or recovery conditions.
- Communicating operational status to the user-interface components.
- Coordinating orderly application shutdown.


## 6.2 Workflow Coordination

The Orchestrator determines which operation should occur next based on
the current Application State, Workflow Stage, project state and
operational conditions.

The Orchestrator SHALL delegate individual operations to the component
responsible for performing them.

For example:

- Project creation and persistence SHALL be performed by the Project
  Manager.
- Importer discovery and activation SHALL be performed by the Importer
  Manager.
- Source communication SHALL be performed by the selected Importer.
- Asset registration and acquisition SHALL use the Core–Importer API.
- User interaction SHALL be provided by the appropriate user-interface
  component.
- Diagnostic logging SHALL be performed by the Logging Manager.


## 6.3 Application State

The Orchestrator controls the Application State.

Application State represents the current operational condition of the
running application.

The Application State SHALL describe what the application is currently
doing or waiting for, rather than the persistent progress of the
project.

The Orchestrator SHALL update Application State when the application
enters, progresses through or leaves an operational condition.

Application State SHALL NOT be used as a substitute for persistent
project workflow state.


## 6.4 Workflow Stage

The Orchestrator also controls the Workflow Stage.

Workflow Stage represents the progress of the active project through
the overall Photo Manager workflow.

Workflow Stage SHALL remain distinct from Application State.

The Orchestrator SHALL use Workflow Stage to determine the appropriate
project operation and SHALL use Application State to represent the
current operational condition while that operation is being performed.

A change in Workflow Stage SHALL NOT be assumed to require an immediate
change in Application State, and a change in Application State SHALL NOT
necessarily change Workflow Stage.


## 6.5 Project Creation

When the user requests a new project, the Orchestrator SHALL coordinate
the project-creation workflow.

The general sequence is:

1. Coordinate selection of the required Importer.
2. Coordinate Importer activation and initialisation.
3. Allow the Importer to perform any required source interaction.
4. Allow the Importer to obtain the information required to create the
   project.
5. Coordinate invocation of CORE-001 Create Project.
6. Receive the resulting Project Context.
7. Continue with the registration and acquisition workflow.

The Orchestrator SHALL NOT create or modify `project.json` directly.


## 6.6 Existing Project Operations

When an existing project is selected, the Orchestrator SHALL coordinate
its loading and validation through the Project Manager.

The Orchestrator SHALL determine the appropriate next operation from
the persistent project state.

Where an incomplete registration operation remains, the Orchestrator
SHALL coordinate registration recovery.

Where registered assets remain to be acquired, the Orchestrator SHALL
coordinate acquisition.

Where the project is complete, the Orchestrator SHALL make the project
available for the appropriate subsequent workflow operation.


## 6.7 Registration Coordination

During registration, the Orchestrator SHALL coordinate the registration
operation but SHALL NOT enumerate the source itself.

The Importer is responsible for source enumeration and for submitting
asset registrations through CORE-002 Register Asset.

The Core SHALL persist the result of each registration.

The Orchestrator SHALL use the persistent registration state to
determine whether registration has completed or whether recovery is
required.


## 6.8 Acquisition Coordination

During acquisition, the Orchestrator SHALL coordinate the acquisition
process but SHALL NOT acquire source assets itself.

The Core SHALL request individual assets from the Importer through the
defined Core–Importer interface.

The Orchestrator SHALL determine which registered asset is to be
requested next in accordance with the current project state and
acquisition policy.

A failed acquisition SHALL NOT, by itself, terminate acquisition of the
remaining assets.

Where retry is required, the Orchestrator SHALL coordinate another
acquisition request for the affected asset.

The Orchestrator SHALL NOT require the Importer to maintain the
persistent acquisition sequence or retry count.


## 6.9 Recovery

The Orchestrator is responsible for coordinating recovery following
application interruption or operational failure.

Recovery decisions SHALL be based on persistent project state rather
than on assumptions about the previous runtime state of the application
or Importer.

The Orchestrator SHALL determine whether the project requires:

- Registration recovery.
- Asset acquisition.
- Acquisition retry.
- Source reconnection.
- User intervention.
- No recovery because the operation is complete.

The Orchestrator SHALL delegate the actual operation to the responsible
component.


## 6.10 Error and Failure Handling

The Orchestrator SHALL coordinate the response to operational failures.

It SHALL distinguish between:

- A failure of an individual operation.
- A condition requiring source reconnection.
- A condition requiring user intervention.
- A failure that prevents the current workflow from continuing.
- A failure that permits other independent operations to continue.

The Orchestrator SHALL NOT hide failures that require user attention.

Diagnostic information SHALL be recorded through the Logging Manager.

The Orchestrator SHALL determine the appropriate workflow response but
SHALL NOT replace the diagnostic or error-handling responsibilities of
the component that detected the failure.


## 6.11 User Interaction

The Orchestrator receives workflow-changing requests from user-interface
components.

It SHALL determine whether the requested action is valid in the
current Application State and Workflow Stage.

User-interface components SHALL NOT directly change Application State,
Workflow Stage or persistent project state.

The Orchestrator SHALL communicate the result of workflow decisions to
the appropriate user-interface components through the defined Core
interfaces.


## 6.12 Shutdown

The Orchestrator SHALL coordinate orderly application shutdown.

Where an active operation is in progress, it SHALL coordinate the
appropriate cancellation or termination behaviour before the
application exits.

Shutdown SHALL leave persistent project state in a condition from
which the Core can determine the appropriate recovery operation on the
next application start.


## 6.13 Ownership Boundaries

The Orchestrator owns workflow coordination but does not own the
persistent data or implementation of the operations it coordinates.

The following boundaries apply:

- The Orchestrator owns workflow decisions.
- The Project Manager owns persistent project state.
- The Importer Manager owns Importer discovery and activation.
- Importers own source-specific communication and asset acquisition.
- User-interface components own presentation and user interaction.
- The Logging Manager owns diagnostic logging.
- The Settings Manager owns application configuration.

The Orchestrator SHALL use the appropriate component or service for
each operation and SHALL NOT bypass established ownership boundaries.

---

# 7. Project Manager

The Project Manager is the Core component responsible for managing
Photo Manager projects and their persistent state.

The Project Manager is the authoritative owner of the project workspace
and `project.json`.

It is responsible for creating, discovering, loading, validating and
persisting projects.

The Project Manager does not determine overall application workflow.
Workflow decisions remain the responsibility of the Orchestrator.


## 7.1 Responsibilities

The Project Manager is responsible for:

- Discovering available projects.
- Creating new project workspaces.
- Loading existing projects.
- Validating project data.
- Maintaining `project.json`.
- Persisting changes to project state.
- Providing project information to other Core components.
- Maintaining persistent registration state.
- Maintaining persistent acquisition state.
- Maintaining project metadata policies.
- Maintaining the integrity of the project workspace.
- Determining whether a project is sufficiently valid for the requested
  Core operation.

The Project Manager SHALL be the sole Core owner of persistent project
state.

Other Core components SHALL NOT directly modify `project.json`.


## 7.2 Project Discovery

The Project Manager provides the information required by the Core to
identify available projects.

Project discovery SHALL:

- Identify valid project workspaces.
- Locate the associated `project.json`.
- Validate sufficient project information for the project to be
  presented to the user.
- Provide project information required by Project Selection.
- Identify projects that cannot be used because they are invalid or
  incomplete.

Project discovery SHALL NOT modify project data.

The Project Manager SHALL NOT treat a project as valid merely because a
`project.json` file exists.

The project SHALL satisfy the applicable validation requirements before
being presented as a usable project.


## 7.3 Project Creation

The Project Manager creates a new project when instructed by the
Orchestrator.

Project creation SHALL:

1. Validate the project information supplied by the caller.
2. Establish the project workspace.
3. Create and initialise `project.json`.
4. Initialise the required project state.
5. Store the applicable Metadata Policies.
6. Persist the initial project state.
7. Return the project information required by the caller.

The Project Manager SHALL NOT obtain source information directly from an
external source system.

Source-specific project information is supplied through the Importer
and Core–Importer API.


## 7.4 Project Loading

The Project Manager loads an existing project when instructed by the
Orchestrator.

Loading SHALL:

- Locate the project data.
- Read `project.json`.
- Validate the stored project data.
- Establish the in-memory representation required by the Core.
- Make the persistent project state available to the requesting Core
  component.

A project that fails validation SHALL NOT be made available for normal
editing or workflow operations.

The Project Manager SHALL provide sufficient diagnostic information to
allow the cause of a loading or validation failure to be determined.


## 7.5 Project Validation

The Project Manager is responsible for validating persistent project
data.

Validation SHALL include, as applicable:

- Project schema compatibility.
- Required project fields.
- Valid field types and values.
- Required workspace information.
- Valid project workflow state.
- Valid asset records.
- Required asset identifiers.
- Consistency of persistent project information.
- Valid references to project resources.

Validation SHALL be performed before an incomplete or potentially
inconsistent project is made available for normal operation.

Validation rules defined by the applicable Project JSON specification
are authoritative for the structure and interpretation of
`project.json`.


## 7.6 Persistent Project State

The Project Manager maintains the persistent state required to describe
the current condition of the project.

This includes, where applicable:

- Registration state.
- Acquisition state.
- Asset processing state.
- Retry information.
- Metadata Policies.
- Project configuration.
- User-editable project information.

Persistent state SHALL be sufficient for the Core to determine the
appropriate recovery operation after application restart.

The Project Manager SHALL NOT depend on runtime state retained by an
Importer to determine the persistent state of a project.


## 7.7 Asset Records

The Project Manager maintains the persistent records for assets within
the project.

The Core-managed portions of an asset record include information such
as:

- Acquisition state.
- Retry count.
- Local file information.
- Processing state.
- Derived project information.

Source information supplied by an Importer SHALL be recorded by the
Core in accordance with the applicable project schema.

The Project Manager SHALL preserve the distinction between:

- Source-provided information.
- Core-managed information.
- User-owned metadata.
- Derived information.

The Project Manager SHALL NOT invent source-specific information that
has not been supplied by the Importer or another authorised Core
service.


## 7.8 Registration State

The Project Manager maintains the persistent state required to determine
the progress of asset registration.

Registration state SHALL allow the Core to determine:

- Which assets have been successfully registered.
- Whether registration remains incomplete.
- Whether registration recovery is required.
- Whether acquisition may begin.

The Project Manager SHALL persist registration results as they are
received.

The Project Manager SHALL NOT rely on an Importer's runtime state to
determine whether registration has completed.


## 7.9 Acquisition State

The Project Manager maintains the persistent state required to determine
the progress of asset acquisition.

The persistent project state SHALL allow the Core to determine:

- Which registered assets have been acquired.
- Which assets remain outstanding.
- Which assets have failed acquisition.
- Which assets may be retried.
- Whether acquisition is complete.

The Core SHALL determine acquisition completion from the persistent
state of the registered assets.

The Project Manager SHALL NOT require an Importer to maintain an
overall acquisition-complete flag.


## 7.10 Persistence

The Project Manager is responsible for persisting changes to
`project.json`.

Persistence SHALL be performed in a manner that maintains a valid and
recoverable project state.

The Project Manager SHALL ensure that a failed persistence operation is
reported to the appropriate Core component.

Persistent project changes SHALL NOT be considered complete until the
Project Manager has successfully committed them.


## 7.11 Project Context

The Project Manager is responsible for resolving the Project Context
used by the Core–Importer API to the corresponding project.

The Project Context is an opaque Core-issued value.

The Importer SHALL NOT be required to understand the internal
representation of a Project Context.

The Project Manager SHALL ensure that a Project Context cannot
accidentally resolve to an unrelated project.


## 7.12 Project Integrity

The Project Manager SHALL protect the integrity of persistent project
data.

It SHALL prevent invalid or incomplete data from being committed as a
valid project state.

Where an operation would leave the project in an invalid state, the
Project Manager SHALL reject the operation or ensure that the previous
valid state remains recoverable.

The Project Manager SHALL NOT silently discard persistent project data
in response to an operational failure.


## 7.13 Interaction with the Orchestrator

The Orchestrator coordinates project operations and instructs the
Project Manager to perform them.

The Project Manager SHALL perform the requested project operation and
return its result.

The Project Manager SHALL NOT independently change the overall
Application State or Workflow Stage.

For example:

- The Orchestrator may request creation of a project.
- The Project Manager creates and persists the project.
- The Project Manager reports the result.
- The Orchestrator determines what workflow operation occurs next.

This separation keeps project management independent of overall workflow
coordination.


## 7.14 Interaction with Importers

Importers SHALL NOT access the Project Manager's persistent storage
directly.

Importers communicate with the Core through the Core–Importer API.

The Project Manager receives and persists the results of those
operations through the Core services.

The Importer SHALL NOT modify `project.json` directly.

This ensures that all persistent project state remains under Core
control.


## 7.15 Interaction with User Interface

Project Selection and other user-interface components may request
project information from the Project Manager through the appropriate
Core service.

User-interface components SHALL NOT directly read or modify
`project.json` as part of normal application operation.

The Project Manager provides the project information required for
presentation while retaining ownership of the underlying persistent
data.


## 7.16 Ownership Boundary

The Project Manager owns persistent project state.

It does not own:

- Overall application workflow.
- User-interface presentation.
- Importer discovery or activation.
- Source-system communication.
- Source-specific asset enumeration.
- Source-specific asset acquisition.
- Application-wide diagnostic logging.
- Application configuration.

Those responsibilities belong to the appropriate Core component or
Importer.

The Project Manager SHALL remain the authoritative Core component for
the creation, validation, loading and persistence of Photo Manager
projects.

---

# 8. Importer Manager

The Importer Manager is the Core component responsible for managing the
collection of available Importers.

It discovers Importers, obtains their declared capability information,
validates their compatibility with the Core, and makes valid Importers
available for selection.

The Importer Manager also coordinates activation and initialisation of
the Importer selected for an import operation.

The Importer Manager does not perform source-specific operations. Those
operations remain the responsibility of the selected Importer.


## 8.1 Responsibilities

The Importer Manager is responsible for:

- Discovering available Importers.
- Validating discovered Importers.
- Obtaining Importer Capability Information.
- Determining compatibility with the supported Core API Version.
- Maintaining the collection of available Importers.
- Identifying invalid or unavailable Importers.
- Making valid Importers available for selection.
- Selecting an Importer for an import operation.
- Activating the selected Importer.
- Initialising the selected Importer as required.
- Providing the Orchestrator with access to the active Importer.
- Coordinating termination or release of the active Importer.


## 8.2 Importer Discovery

Importer discovery occurs independently of Importer activation.

During discovery, the Importer Manager SHALL identify Importer
implementations available to the Core.

Discovery SHALL NOT require the Importer to:

- Connect to its source system.
- Authenticate with its source system.
- Enumerate source content.
- Select a source workspace.
- Acquire assets.

Discovery is concerned only with determining whether an Importer is
available and suitable for use by the Core.


## 8.3 Importer Validation

The Importer Manager SHALL validate each discovered Importer before
making it available for selection.

Validation SHALL include, as applicable:

- Importer package structure.
- Importer identity.
- Required interface implementation.
- Declared Core API compatibility.
- Required capability information.
- Duplicate Importer identifiers.
- Load or initialisation errors that prevent the Importer from being
  used.

An Importer that fails validation SHALL NOT be made available for normal
selection.

The Importer Manager SHALL record sufficient diagnostic information to
allow the reason for the validation failure to be determined.

One invalid Importer SHALL NOT prevent other valid Importers from being
discovered and made available.


## 8.4 Capability Information

The Importer Manager obtains the static Capability Information declared
by each Importer.

Capability Information SHALL be sufficient for the Core and user
interface to determine whether an Importer is suitable for the intended
operation.

Capability Information includes, as applicable:

- Importer identifier.
- Importer name.
- Description.
- Supported Core API Version.
- Requirements.
- Supported capabilities.

Capability Information SHALL be available without requiring a connection
to the Importer's source system.

Capability Information describes the Importer itself and SHALL NOT be
used to represent the current runtime state of an import operation.


## 8.5 Importer Selection

The Orchestrator coordinates selection of an Importer for an import
operation.

The Importer Manager SHALL provide the Orchestrator and user interface
with the information required to present the available valid Importers.

The Importer Manager SHALL NOT independently select an Importer on
behalf of the user unless an explicit Core policy provides such
behaviour.

Once an Importer has been selected, the Importer Manager SHALL prepare
that Importer for activation.


## 8.6 Importer Activation

Activation begins only after an Importer has been selected for use.

The Importer Manager SHALL:

1. Identify the selected Importer.
2. Load or instantiate the Importer implementation as required.
3. Initialise the Importer.
4. Establish the runtime interface between the Core and Importer.
5. Report the result to the Orchestrator.

Activation MAY cause the Importer to prepare source-specific resources.

Activation SHALL NOT be confused with discovery.

Discovery establishes that an Importer is available.

Activation prepares a selected Importer for an actual import operation.


## 8.7 Source Interaction

The Importer Manager does not communicate directly with the Importer's
source system as part of normal import operation.

Once activated, the selected Importer is responsible for:

- Source authentication.
- Source connection.
- Source workspace selection.
- Source enumeration.
- Source-specific user interaction.
- Source asset acquisition.

The Importer Manager SHALL provide the runtime environment required for
the Importer to perform these operations but SHALL NOT implement them.


## 8.8 Runtime Importer State

The Importer Manager MAY maintain runtime information about the active
Importer, including:

- Whether an Importer is active.
- Which Importer is active.
- Whether activation has completed.
- Whether the Importer has terminated.
- Runtime errors preventing the Importer from continuing.

Runtime Importer state SHALL NOT become the persistent owner of project
workflow state.

Persistent project state remains the responsibility of the Project
Manager.


## 8.9 Importer and Project Context

The Importer Manager SHALL provide the active Importer with the runtime
environment required to participate in the Core–Importer API.

The Project Context is owned and resolved by the Core.

The Importer Manager SHALL NOT reinterpret the Project Context or assign
project meaning to its internal representation.

Where an existing project is resumed, the Orchestrator and Project
Manager determine the applicable project context and recovery state.


## 8.10 Importer Failure

If an Importer fails during activation or operation, the Importer
Manager SHALL report the condition to the Orchestrator.

The Importer Manager SHALL distinguish between:

- Failure to load or initialise an Importer.
- Runtime failure reported by an active Importer.
- Loss of source connectivity.
- A source-specific condition requiring user interaction.

The Importer Manager SHALL NOT independently determine project recovery
or retry policy.

Those decisions remain the responsibility of the Orchestrator and Core
project state.


## 8.11 Importer Termination

When an import operation is cancelled, completed or otherwise
terminated, the Importer Manager SHALL coordinate termination of the
active Importer.

The Importer SHALL release source-specific resources in accordance with
the Importer SDK requirements.

The Importer Manager SHALL ensure that the active Importer is no longer
treated as available for the terminated operation.

Termination of an Importer SHALL NOT alter persistent project state
except through the normal Core services used to record the result of the
operation.


## 8.12 Importer Collection

The Importer Manager maintains the collection of Importers available to
the application.

Each Importer SHALL have a unique identifier within the Core's Importer
collection.

The Importer Manager SHALL prevent duplicate identifiers from being
treated as separate valid Importers.

The collection SHALL be refreshed when the application starts and MAY
be refreshed by an implementation-defined mechanism where supported.

Importer discovery does not require an installation or registration
database.


## 8.13 Interaction with the Orchestrator

The Orchestrator coordinates Importer-related workflow.

The Importer Manager performs the Importer management operations
requested by the Orchestrator.

For example:

1. The Orchestrator determines that an Importer is required.
2. The Importer Manager provides the available valid Importers.
3. The user selects an Importer.
4. The Orchestrator instructs the Importer Manager to activate it.
5. The Importer Manager activates and initialises the selected
   Importer.
6. The Importer Manager reports the result.
7. The Orchestrator continues the workflow.

The Importer Manager SHALL NOT independently change the overall
Application State or Workflow Stage.


## 8.14 Interaction with User Interface

The Importer Manager provides Importer information required by the user
interface.

The user interface MAY present:

- Importer name.
- Description.
- Requirements.
- Declared capabilities.
- Availability or validation status.

The user interface SHALL NOT directly load, initialise or manipulate
Importer implementations.

Importer selection SHALL be communicated to the Orchestrator through
the appropriate Core interface.


## 8.15 Ownership Boundary

The Importer Manager owns Importer discovery, validation, selection
support, activation and runtime management.

It does not own:

- Overall application workflow.
- Persistent project state.
- Project recovery policy.
- Source-system communication.
- Source authentication.
- Source enumeration.
- Asset acquisition.
- Importer-specific persistent project state.
- User-interface presentation.

Those responsibilities belong to the appropriate Core component or the
active Importer.

The Importer Manager SHALL remain the authoritative Core component for
the management and activation of Importers.

---
# 9. Project Selection

Project Selection provides the user interface and supporting logic used
to select an existing Photo Manager project or request creation of a new
project.

Project Selection obtains available project information from the Project
Manager and communicates the user's selection to the Orchestrator.

Project Selection does not own project data and does not perform project
loading, validation or persistence.


## 9.1 Responsibilities

Project Selection is responsible for:

- Presenting available projects to the user.
- Presenting sufficient project information to allow a project to be
  selected.
- Indicating projects that are unavailable or invalid where appropriate.
- Accepting a user's project selection.
- Providing a request to create a new project.
- Communicating the selected project or new-project request to the
  Orchestrator.
- Refreshing its displayed project information when instructed by the
  Core.


## 9.2 Project List

The Project Selection component obtains the available project list from
the Project Manager.

The project list SHALL contain sufficient information to identify each
project to the user.

This MAY include:

- Project name.
- Project location.
- Project validity.
- Thumbnail information where available.
- Other project information required by the user interface.

Project Selection SHALL NOT determine project validity independently of
the Project Manager.

The Project Manager remains the authoritative source for project
discovery and validation.


## 9.3 Project Selection

When the user selects an existing project, Project Selection SHALL
communicate the selection to the Orchestrator.

The selection SHALL identify the project using the Core-managed project
reference provided for that purpose.

Project Selection SHALL NOT load `project.json` directly as part of the
selection operation.

The Orchestrator SHALL determine the subsequent workflow operation.


## 9.4 New Project

Project Selection SHALL provide a means for the user to request creation
of a new project.

A new-project request SHALL be communicated to the Orchestrator.

Project Selection SHALL NOT:

- Create the project workspace.
- Create `project.json`.
- Select or activate an Importer.
- Communicate with a source system.
- Determine the project workflow.


## 9.5 Project Selection Records

The Core MAY maintain an in-memory Project Selection Record for each
project displayed by Project Selection.

A Project Selection Record may contain information such as:

- Project name.
- Project JSON path.
- Image folder.
- Thumbnail path.
- Whether the entry represents a new-project request.
- Whether the project is currently considered valid for selection.

Project Selection Records are temporary application state.

They SHALL NOT be treated as persistent project state.

The Project Manager remains responsible for the authoritative project
information.


## 9.6 Invalid Projects

If the Project Manager identifies a project as invalid or unavailable,
Project Selection MAY display the project to the user with an
appropriate indication of its condition.

Project Selection SHALL NOT attempt to repair or modify the project.

The user interface MAY provide appropriate information explaining why
the project cannot be selected.

Any recovery or repair operation SHALL be initiated through the
appropriate Core workflow.


## 9.7 Interaction with the Project Manager

The Project Manager provides Project Selection with information about
available projects.

Project Selection presents that information to the user but does not
become its owner.

The general interaction is:

1. The Project Manager discovers available projects.
2. The Project Manager validates the information required for selection.
3. Project Selection receives the resulting project information.
4. Project Selection presents the projects to the user.
5. The user selects a project or requests a new project.
6. Project Selection communicates the request to the Orchestrator.


## 9.8 Interaction with the Orchestrator

The Orchestrator controls the workflow resulting from a user's
selection.

For an existing project, the Orchestrator may instruct the Project
Manager to load and validate the selected project.

For a new project, the Orchestrator coordinates Importer selection and
project creation.

Project Selection SHALL NOT independently initiate these workflow
operations.


## 9.9 Refresh

Project Selection MAY be capable of refreshing its displayed
information when instructed by the Core.

A refresh MAY be required after:

- Creation of a new project.
- Completion of an import operation.
- Changes to the available project collection.
- Detection of a project that has become invalid or unavailable.

Refreshing the displayed project list SHALL NOT modify project data.


## 9.10 Ownership Boundary

Project Selection owns the presentation and selection of available
projects.

It does not own:

- Persistent project state.
- `project.json`.
- Project discovery.
- Project validation.
- Project creation.
- Project loading.
- Project persistence.
- Overall application workflow.
- Importer selection or activation.
- Source-system communication.

Those responsibilities belong to the Project Manager, Orchestrator,
Importer Manager or Importer as appropriate.

Project Selection SHALL remain a user-interface component rather than a
project-management component.

---

# 10. Application State and Workflow Stage

The Photo Manager Core maintains two related but distinct concepts of
state:

- Application State.
- Workflow Stage.

These concepts represent different aspects of the application's
operation and SHALL NOT be treated as a single state machine.

Application State represents the current operational condition of the
running Photo Manager application.

Workflow Stage represents the current progress of the active project
through the Photo Manager workflow.

The Orchestrator is responsible for coordinating both concepts.

---

## 10.1 Application State

Application State represents the current operational condition of the
Photo Manager application.

It describes what the application is currently doing or waiting for.

Examples include:

- Starting.
- Selecting a project.
- Loading a project.
- Selecting an Importer.
- Importing.
- Editing.
- Finalising.
- Waiting for user action.
- Shutting down.

The exact set of Application States is defined by the implementation and
may be extended as required.

The Orchestrator SHALL be the authoritative owner of Application State.

Application State SHALL NOT be treated as persistent project data.

---

## 10.2 Workflow Stage

Workflow Stage represents the progress of the active project through the
overall Photo Manager workflow.

Workflow Stage describes the project's position within the application
workflow rather than the instantaneous operational condition of the
application.

Examples include:

- Project creation.
- Registration.
- Acquisition.
- Editing.
- Finalisation.
- Completion.

The exact set of Workflow Stages is defined by the implementation and
the applicable project workflow.

The Orchestrator SHALL be responsible for coordinating Workflow Stage.

Where Workflow Stage information forms part of persistent project state,
the Project Manager SHALL remain responsible for storing and maintaining
that persistent representation.

---

## 10.3 Separation of Application State and Workflow Stage

Application State and Workflow Stage SHALL remain independent.

A change in Application State does not necessarily imply a change in
Workflow Stage.

A change in Workflow Stage does not necessarily imply an immediate
change in Application State.

For example, while the project remains in the Registration Workflow
Stage, the Application State may change from:

- Importing;
- Waiting for user action;
- Importing again; or
- Handling an error.

Similarly, an existing project may remain at the same Workflow Stage
while the application transitions between operational states while
loading, validating or presenting the project.

This separation allows the Core to represent both the operational
condition of the application and the progress of the project without
combining them into a single state model.

---

## 10.4 State Transitions

The Orchestrator SHALL determine when Application State or Workflow Stage
changes are required.

State transitions SHALL occur through the Orchestrator rather than being
initiated independently by user-interface components or Importers.

Components SHALL report conditions or completed operations to the
Orchestrator through their defined interfaces.

The Orchestrator SHALL determine the resulting Application State and
Workflow Stage in accordance with the current operation.

The implementation MAY provide validation of permitted state
transitions, but such validation SHALL support the Orchestrator rather
than becoming an independent source of workflow decisions.

---

## 10.5 Persistence

Application State is runtime state and SHALL NOT be treated as
persistent project state.

Workflow Stage MAY be represented in persistent project data where
required for project recovery.

The Project Manager is responsible for the persistent representation of
Workflow Stage.

The Orchestrator remains responsible for interpreting the persisted
project information and determining the appropriate runtime state when a
project is loaded or resumed.

Neither Application State nor Workflow Stage requires a separate
persistent State Manager component.

---

## 10.6 Interaction with Core Components

The Orchestrator coordinates state information with the other Core
components as required.

The Project Manager provides project information and persistent workflow
information.

The Importer Manager provides information about Importer activation and
availability.

The Control Tower presents current Application State, Workflow Stage
and current activity to the user.

The Editor presents project information appropriate to the current
workflow.

The Logging Manager records significant state transitions and workflow
events for diagnostic purposes.

No Core component other than the Orchestrator SHALL independently
determine the overall application workflow.

---

## 10.7 Ownership

The following ownership rules apply:

- The Orchestrator owns and coordinates runtime Application State.
- The Orchestrator coordinates Workflow Stage.
- The Project Manager owns persistent project state, including any
  persistent representation of Workflow Stage.
- User-interface components present state but do not own it.
- Importers report operational conditions but do not determine Core
  workflow.
- The Logging Manager records state and workflow events but does not
  control them.

There is therefore no separate State Manager component in the Core
architecture.

The removal of a dedicated State Manager keeps state management with the
component that already owns workflow coordination and avoids introducing
an additional component whose responsibilities would overlap with the
Orchestrator and Project Manager.

---

# 11. Window Manager

The Window Manager is the Core infrastructure service responsible for
coordinating the application's graphical user interface and application
windows.

The Window Manager provides the interface between Core application
components and the graphical user interface.

Application components SHALL NOT communicate directly with GUI windows
where the Window Manager provides the required interface.

The Window Manager provides a consistent application-facing interface
for:

- The Control Tower.
- User interaction dialogs.
- Project selection.
- Activity presentation.
- Workflow status presentation.
- External application windows.
- Window activation, focus and geometry.
- Application shutdown interaction.

The Window Manager does not own application workflow or persistent
project state.


## 11.1 Responsibilities

The Window Manager is responsible for:

- Creating and maintaining the Control Tower interface.
- Presenting application activities through the Control Tower.
- Presenting workflow stage status and results.
- Presenting status messages.
- Presenting project selection.
- Presenting the Editor activity.
- Presenting the Finalise activity.
- Presenting modal user interaction.
- Presenting user confirmation dialogs.
- Providing user directory-selection dialogs.
- Managing Control Tower window geometry and display.
- Managing external application windows used by Photo Manager.
- Forwarding user actions from the Control Tower to the application.
- Releasing Window Manager resources during application shutdown.

The Window Manager SHALL provide these functions without becoming
responsible for determining the overall application workflow.


## 11.2 Relationship with the Orchestrator

The Orchestrator is responsible for application workflow and determines
when user-interface presentation or interaction is required.

The Window Manager provides the interface through which the Orchestrator
requests that presentation or interaction.

The general relationship is:

    Orchestrator
          |
          v
    Window Manager
          |
          v
    Control Tower
          |
          v
    User

User actions travel back through the Window Manager to the application.

The Window Manager therefore provides a two-way interface between the
application workflow and the graphical user interface.

The Orchestrator SHALL NOT directly manipulate Control Tower widgets or
other GUI implementation details.

The Window Manager SHALL translate application-level presentation
requests into the corresponding GUI operations.


## 11.3 Control Tower

The Control Tower is the principal operational user interface presented
by the Window Manager.

The Window Manager creates and maintains the Control Tower instance and
provides the application-facing interface to it.

The Window Manager may instruct the Control Tower to display:

- Project Selection.
- Workflow Stage status.
- Workflow Stage results.
- Current activity information.
- Photo Editor activity.
- Finalise activity.
- Status messages.
- Workflow actions.
- Other application information supported by the Control Tower.

The Window Manager SHALL remain responsible for determining how these
requests are communicated to the Control Tower.

The Control Tower SHALL remain responsible for presenting the supplied
information to the user.

The Control Tower does not own Application State, Workflow Stage or
persistent project state.


## 11.4 User Actions

The Control Tower MAY generate user actions such as:

- Selecting a project.
- Selecting a workflow action.
- Requesting another application operation.
- Responding to an interaction presented by the application.

The Window Manager receives these actions from the Control Tower.

The Window Manager SHALL forward the action to the application through
the defined application callback or interface.

The Window Manager SHALL NOT determine the workflow consequence of a
user action.

The Orchestrator remains responsible for determining what the action
means within the current application workflow.


## 11.5 Activity Presentation

The Window Manager provides operations for presenting the major
application activities.

Activities may include:

- Project Selection.
- Photo Editor.
- Finalise.
- Other operational activities introduced by the application.

When presenting a new activity, the Window Manager MAY clear or replace
the previous activity and update the Control Tower activity title as
required.

The Window Manager is responsible for coordinating the presentation
change.

The Orchestrator remains responsible for determining when the
application changes from one activity to another.


## 11.6 Workflow Stage Presentation

The Window Manager provides the interface through which the current
Workflow Stage status and result are presented in the Control Tower.

The Window Manager SHALL accept the Workflow Stage and associated
display information from the application and pass the information to the
Control Tower.

The Window Manager MAY also request the corresponding workflow actions
to be displayed for the selected Workflow Stage.

The Window Manager does not determine the Workflow Stage or its
transition.

Workflow Stage remains coordinated by the Orchestrator as defined in
Section 10.


## 11.7 User Interaction

The Window Manager provides common user-interaction services for the
application.

These include:

- Informational or warning messages requiring acknowledgement.
- Yes/No confirmation requests.
- Directory selection.
- Other modal interaction required by Core operations.

The Window Manager SHALL present the interaction and return the user's
response where a response is required.

The Window Manager SHALL NOT determine the workflow consequence of the
user's response.

The Orchestrator or the Core component requesting the interaction remains
responsible for interpreting the result.


## 11.8 External Application Windows

The Window Manager MAY coordinate external application windows required
by Photo Manager.

An example is opening a web browser to display Google Maps for the
current photo.

The Window Manager is responsible for:

- Launching the supported external application.
- Maintaining the runtime reference required to manage the external
  application.
- Detecting when the externally launched process has already terminated.
- Closing the external application when required by the associated
  Photo Manager operation.
- Reporting inability to launch the external application through the
  normal user-interaction mechanism.

The external application remains outside the ownership of the Photo
Manager Core.

Closing an external application independently by the user SHALL NOT
necessarily be treated as an application error.

## 11.9 Registered Importer User Interfaces

An Importer MAY create or launch a source-specific user interface during
an import operation.

When such a user interface needs to be managed as part of the import
operation, the Importer SHALL register it with the Core using the
`UI-REGISTRATION` message defined by CORE-004.

The Core SHALL associate the registered user interface with the current
Import Operation.

The Window Manager is responsible for the application-level lifecycle
management of registered Importer user interfaces.

The Importer remains responsible for creating or launching the
source-specific user interface and for determining when and why it is
required.

The Importer SHALL NOT communicate directly with the Window Manager.

The Core SHALL provide the Window Manager with the information required
to manage and release the registered user interface.

A registered Importer user interface SHALL remain associated with the
Import Operation until the operation ends, unless the interface is
otherwise terminated by the implementation.

The Importer SHALL NOT treat a registered user interface as an
Importer-owned resource for normal application-level lifecycle
management.

When the Import Operation ends, the Window Manager SHALL manage the
release or closure of registered Importer user interfaces as
appropriate.

## 11.10 Window and Display Management

The Window Manager is responsible for managing the presentation of the
Control Tower window.

This includes:

- Discovering available display screens.
- Selecting the appropriate display for the Control Tower.
- Setting the Control Tower size.
- Setting the Control Tower position.
- Validating supplied window geometry.
- Applying suitable default geometry when supplied values are invalid
  or unavailable.
- Showing the Control Tower window.

Window geometry and display information are runtime presentation data and
are not project state.

The Window Manager SHALL NOT use window-management operations to
determine application workflow.


## 11.11 Ownership

The following ownership rules apply:

- The Orchestrator owns application workflow coordination.
- The Project Manager owns persistent project state.
- The Window Manager owns the interface between Core application
  components and the graphical user interface.
- The Control Tower owns presentation of information supplied to it.
- The Control Tower does not own application workflow or project state.
- The Window Manager owns the runtime coordination of application
  windows and dialogs.
- External applications remain outside the ownership of the Core.

The Window Manager SHALL NOT:

- Determine application workflow.
- Determine Workflow Stage transitions.
- Modify `project.json` directly.
- Own persistent project state.
- Perform source-specific Importer operations.
- Replace the Orchestrator as the application workflow coordinator.

The Window Manager provides presentation and user-interaction services
to the Core while maintaining a clear separation between application
workflow and graphical user-interface implementation.


## 11.12 Architectural Boundary

The Window Manager forms the boundary between the application workflow
and the graphical user interface.

The intended relationship is:

    Core Workflow
         |
         v
    Orchestrator
         |
         v
    Window Manager
         |
         v
    Control Tower / Dialogs / External Windows

The Orchestrator communicates application-level requirements to the
Window Manager.

The Window Manager performs the required presentation or interaction
using the appropriate GUI component.

User actions are returned through the Window Manager to the application,
where the Orchestrator determines the resulting workflow operation.

This boundary allows the Core workflow to remain independent of the
underlying GUI implementation while providing a single, consistent
interface for application windows and user interaction.

---

# 12. Settings Manager

The Settings Manager is the Core component responsible for managing
persistent application configuration for Photo Manager.

The Settings Manager owns application-level settings and provides
configuration services to the Core.

The Settings Manager does not manage project-specific information.

---

## 12.1 Responsibilities

The Settings Manager is responsible for:

- Loading application settings.
- Saving application settings.
- Validating application settings.
- Maintaining application configuration.
- Providing configuration information to Core components.
- Maintaining configuration consistency.
- Providing appropriate default values where required.

The Settings Manager SHALL be the authoritative owner of persistent
application settings.

The Settings Manager SHALL NOT own persistent project state.


## 12.2 Application Configuration

Application configuration represents settings that apply to the
Photo Manager application rather than to an individual project.

Application configuration MAY include:

- User preferences.
- Application defaults.
- Importer configuration.
- Window preferences.
- Other application-level configuration required by Core components.

The exact configuration items are implementation dependent and may be
extended as the application develops.

Project-specific information SHALL NOT be stored as application
configuration.


## 12.3 Configuration Loading

The Settings Manager SHALL load application configuration when required
by application startup or configuration operations.

The Settings Manager SHALL validate loaded configuration before making
it available to the application.

Where configuration is missing or invalid, the Settings Manager SHALL
apply appropriate defaults or report the configuration condition to the
requesting Core component.

Configuration loading SHALL NOT modify persistent project state.


## 12.4 Configuration Saving

The Settings Manager SHALL provide the means to persist changes to
application configuration.

Configuration changes SHALL be validated before being persisted.

The Settings Manager SHALL ensure that a successfully saved
configuration represents a valid application configuration.

The Settings Manager SHALL NOT modify `project.json` or other
project-specific persistent data.


## 12.5 Interaction with Core Components

The Orchestrator coordinates application workflow and determines when
configuration operations are required.

The Settings Manager provides the required configuration services.

Other Core components MAY obtain configuration information through the
defined Settings Manager interface where that configuration is required
for their operation.

Components SHALL NOT maintain independent persistent copies of
application settings.

A component that requires application configuration SHALL obtain it
through the appropriate configuration interface rather than accessing
the Settings Manager's persistent storage directly.


## 12.6 Configuration Ownership

The Settings Manager is the authoritative owner of persistent
application configuration.

The following ownership rules apply:

- The Settings Manager owns application configuration.
- The Project Manager owns persistent project state.
- The Orchestrator coordinates the use of configuration during
  application workflow.
- Core components may consume configuration required for their
  operation.
- No Core component SHALL directly modify the persistent configuration
  storage owned by the Settings Manager.

This separation ensures that application configuration and project
configuration remain independent.


## 12.7 User Configuration

Where the application provides user-editable settings, the user
interface SHALL obtain and present those settings through the
appropriate Core configuration interface.

The user interface SHALL NOT directly modify persistent configuration
files.

Configuration changes requested by the user SHALL be validated by the
Settings Manager before they become persistent.


## 12.8 Ownership Boundary

The Settings Manager owns application configuration but does not own:

- Application workflow.
- Application State.
- Workflow Stage.
- Project state.
- Importer source communication.
- User-interface presentation.
- Window management.

The Orchestrator remains responsible for workflow coordination.

The Project Manager remains responsible for project-specific persistent
state.

The Window Manager remains responsible for application-window and
user-interface coordination.

The Settings Manager therefore provides a clear boundary between
application configuration and the operational state and persistent data
managed by the other Core components.

---

# 13. User Interface

The User Interface provides the mechanisms through which the user
observes Photo Manager operation and performs user actions.

The User Interface consists of graphical components that present
information supplied by the Core and collect user input.

The User Interface SHALL NOT own application workflow or persistent
application or project state.

The Window Manager provides the principal interface between Core
application components and the graphical user interface.

The Orchestrator remains responsible for application workflow.


## 13.1 User Interface Responsibilities

The User Interface is responsible for:

- Presenting application information.
- Presenting project information.
- Presenting Application State and Workflow Stage information.
- Accepting user input.
- Presenting available user actions.
- Presenting status and progress information.
- Presenting warnings and errors.
- Presenting requests for user interaction.
- Collecting user modifications to project information.
- Presenting application and project editing functions.

User-interface components SHALL NOT independently implement application
workflow.

User-interface components SHALL NOT directly modify persistent
application or project data.

Workflow-changing user actions SHALL be returned to the application
through the Window Manager, where they are interpreted by the
Orchestrator.


## 13.2 User Interface Components

The principal user-interface components are:

- Control Tower.
- Editor.

Additional dialogs and user-interface components MAY be provided where
required by the application.

The Window Manager coordinates the presentation and lifetime of these
components.

The responsibilities of the principal components are described below.


## 13.3 Control Tower

### Purpose

The Control Tower provides the primary operational user interface for
the Photo Manager application.

The Control Tower presents the current operational condition of the
application and provides the user with access to actions appropriate to
the current operation.

The Control Tower is intended to remain available throughout normal
application operation.


### Responsibilities

The Control Tower is responsible for:

- Presenting project selection.
- Presenting Application State information.
- Presenting Workflow Stage information.
- Presenting current activity information.
- Presenting operational status.
- Presenting progress information.
- Presenting workflow actions.
- Presenting warnings and errors.
- Presenting requests for user interaction.
- Collecting user selections and action requests.
- Presenting access to application functions.
- Presenting project summary information where required.

The Control Tower SHALL NOT:

- Determine application workflow.
- Determine Workflow Stage transitions.
- Own project state.
- Modify `project.json` directly.
- Perform Importer operations directly.
- Determine recovery or retry behaviour.


### Interaction with the Core

The Control Tower communicates with the Core through the Window Manager.

The Window Manager provides the Control Tower with information supplied
by the application and receives user actions generated by the Control
Tower.

The Control Tower does not communicate directly with the Project
Manager, Importer Manager, Importers or other Core services.

The Window Manager forwards user actions to the application, where the
Orchestrator determines the appropriate workflow operation.


### Managed Data

The Control Tower does not own persistent application or project data.

It maintains only transient presentation information required to
display the current application operation and collect user input.


### Notes

The Control Tower is the principal operational presentation component of
Photo Manager.

It provides the user-facing representation of the current application
activity but does not own or control the workflow represented by that
activity.


## 13.4 Editor

### Purpose

The Editor provides the primary user interface for viewing and modifying
the contents of an active project.

The Editor enables the user to review imported assets, modify
user-maintained metadata and perform project editing operations.


### Responsibilities

The Editor is responsible for:

- Displaying project assets.
- Displaying asset metadata.
- Displaying asset previews.
- Supporting user modification of editable metadata.
- Supporting asset selection.
- Supporting asset search and filtering.
- Displaying project statistics.
- Providing access to project editing functions.
- Collecting user modifications for submission to the Core.


### Interaction with the Core

The Editor communicates with the Core through the Window Manager and
the appropriate application services.

The Editor SHALL NOT directly access or modify `project.json`.

Changes made by the user SHALL be submitted to the appropriate Core
service for validation and persistence.

The Project Manager remains responsible for persistent project state.


### Managed Data

The Editor does not own persistent project data.

It maintains only transient information required to display the active
project and support user interaction.

The Editor MAY maintain temporary presentation state such as:

- Current asset selection.
- Current displayed asset.
- Search criteria.
- Filter criteria.
- Current editing values prior to submission.

Such information SHALL NOT be treated as authoritative project state.


### Notes

The Editor provides the primary working environment for managing an
active Photo Manager project.

The Editor presents project information and collects user
modifications.

The Editor does not determine application workflow.


## 13.5 Dialogs and Supporting User Interface

Photo Manager MAY use additional dialogs and supporting user-interface
components for specific operations.

Examples include:

- Application Settings.
- Propagation Settings.
- User confirmation.
- User acknowledgement.
- Directory selection.
- Authentication or source interaction.
- Other action-required interactions.

Such components are presentation and interaction mechanisms.

They SHALL NOT independently determine application workflow or directly
modify persistent Core state.

The Window Manager provides the appropriate interface for presenting
these components where required.


## 13.6 User Interface and Workflow

The User Interface represents the current application workflow but does
not own it.

The general relationship is:

    User
      |
      v
    User Interface
      |
      v
    Window Manager
      |
      v
    Orchestrator
      |
      v
    Core Services

The reverse flow is used to present information:

    Core Services
          |
          v
    Orchestrator
          |
          v
    Window Manager
          |
          v
    User Interface
          |
          v
        User

The Orchestrator determines the workflow operation.

The Window Manager provides the GUI interface.

The User Interface presents information and collects user input.

This separation prevents presentation logic from becoming responsible
for application workflow.


## 13.7 Ownership

The following ownership rules apply:

- The Orchestrator owns application workflow coordination.
- The Window Manager owns the interface between Core application
  components and the graphical user interface.
- The Control Tower owns presentation of operational information and
  collection of operational user actions.
- The Editor owns presentation of project information and collection of
  project edits.
- The Project Manager owns persistent project state.
- The Settings Manager owns persistent application configuration.
- User-interface components do not own persistent application or
  project state.

No User Interface component SHALL directly modify persistent Core data.

No User Interface component SHALL independently determine application
workflow.

The User Interface therefore remains a presentation and interaction
layer, while workflow, state and persistent data remain under the
ownership of the appropriate Core components.

---

# 14. Application Lifecycle

The Application Lifecycle describes the major operational conditions and
transitions of the Photo Manager application.

The Orchestrator coordinates the Application Lifecycle.

The Application Lifecycle is concerned with the operation of the running
application and SHALL remain distinct from the Workflow Stage of the
active project.

Application State describes the current operational condition of the
application.

Workflow Stage describes the progress of the active project through the
Photo Manager workflow.

The relationship between Application State and Workflow Stage is defined
in Section 10.


## 14.1 Lifecycle Model

The application operates through a number of major operational
conditions.

These include:

1. Startup.
2. Project Selection and Idle operation.
3. Project Loading or Creation.
4. Import and Recovery Operations.
5. Project Editing.
6. Project Finalisation.
7. Shutdown.

These conditions describe the overall operation of the application.

They SHALL NOT be interpreted as a single linear state machine.

The application MAY move between operational conditions as a result of
user actions, completion of operations, errors, recovery requirements or
application shutdown.

The active project's Workflow Stage remains independently represented
where applicable.


## 14.2 Startup

During startup the Orchestrator SHALL:

- Initialise the required Core components.
- Load application settings.
- Initialise the User Interface through the Window Manager.
- Discover and validate available Importers.
- Verify the application environment as required.
- Establish the initial Application State.
- Present the appropriate initial user interface.

Following successful startup, the application SHALL enter its normal
idle or project-selection operation.

Startup SHALL NOT require an active project.

If startup cannot be completed successfully, the Orchestrator SHALL
present an appropriate error to the user and terminate the application.


## 14.3 Project Selection and Idle Operation

When no project operation is active, the application SHALL remain
available for user interaction.

The user MAY:

- Create a new project.
- Select an existing project.
- Modify application settings.
- Request application Help.
- Exit the application.

The Project Manager provides the available project information.

The Window Manager presents the project-selection interface through the
Control Tower.

The Orchestrator determines the operation resulting from the user's
selection.

No project import, editing or finalisation operation is active while the
application is idle.


## 14.4 Project Loading

When the user selects an existing project, the Orchestrator coordinates
the loading of the project through the Project Manager.

The Project Manager SHALL:

- Locate the project.
- Load the project data.
- Validate the project.
- Establish the project's persistent state for use by the Core.

The Orchestrator SHALL then determine the appropriate next operation
based on the project's persistent workflow information.

If the project contains incomplete registration or acquisition work, the
Orchestrator SHALL coordinate the appropriate recovery operation.

If the project is complete for editing, the Orchestrator MAY present the
project to the Editor.


## 14.5 New Project Creation

When the user requests a new project, the Orchestrator coordinates
selection and activation of the appropriate Importer.

The Importer SHALL perform the source-specific interaction required to
obtain the information needed to create the project.

When sufficient information is available, the Importer invokes
CORE-001 Create Project.

The Project Manager creates and initialises the project workspace and
persistent project data.

Following successful project creation, the Orchestrator coordinates the
remaining import workflow.

The new project SHALL NOT be presented as a normal editing project until
the required import workflow has reached the appropriate Workflow Stage.


## 14.6 Import and Recovery Operations

Import operations are coordinated by the Orchestrator and use the
Core–Importer interfaces defined by the Core–Importer API Specification.

Import processing consists principally of:

- Registration.
- Acquisition.

Registration and acquisition are separate operations and SHALL NOT be
treated as one indivisible operation.

During Registration, the Core coordinates registration of source assets
and maintains the persistent Registration Checkpoint.

If registration is interrupted, the Orchestrator SHALL coordinate
resumption from the persistent registration state.

During Acquisition, the Core coordinates acquisition of registered
assets.

The Core determines acquisition sequence, persistent acquisition state
and retry policy.

If an individual acquisition fails, the Orchestrator SHALL coordinate
the appropriate recovery or retry operation without requiring the entire
import operation to restart.

Import completion is determined by the Core from the persistent project
state and the results of the registration and acquisition operations.

The detailed Import Workflow is defined in the Core–Importer API
Specification and related workflow sections.


## 14.7 Project Editing

When a project is available for editing, the Orchestrator coordinates
presentation of the project through the Editor.

During Project Editing, the user MAY:

- Review project assets.
- Modify user-maintained metadata.
- Search and filter assets.
- Select assets.
- View asset information and previews.
- Perform other supported project editing operations.

The Editor presents the project and collects user modifications.

The appropriate Core services validate and persist those modifications.

The Project Manager remains responsible for persistent project state.

The Orchestrator remains responsible for the overall application
workflow.


## 14.8 Project Finalisation

Project Finalisation is the workflow operation that completes the
project according to the user's selected finalisation options.

The Orchestrator coordinates Finalisation.

Finalise services perform the operations required to transfer or
otherwise process the completed project according to the application's
finalisation requirements.

The Project Manager remains responsible for persistent project state
during the operation.

Following successful finalisation, the Orchestrator SHALL determine the
appropriate next Application State.

Normally this will return the application to project selection or idle
operation.

The detailed behaviour of Project Finalisation is defined by the
Finalise services and associated implementation requirements.


## 14.9 Error and Recovery Conditions

An error or interruption during an operation SHALL NOT automatically be
treated as termination of the Application Lifecycle.

The Orchestrator SHALL determine the appropriate response according to
the nature of the condition.

Possible responses include:

- Requesting user interaction.
- Retrying an operation.
- Resuming an incomplete operation.
- Returning to a previous operational condition.
- Cancelling the current operation.
- Terminating the application where recovery is not possible.

Persistent project state SHALL be maintained by the Project Manager so
that operations requiring recovery can resume from the available
persistent information.

The Importer MAY retain temporary runtime source state but SHALL NOT be
relied upon as the authority for project recovery.


## 14.10 Shutdown

The Orchestrator coordinates orderly application shutdown.

Shutdown SHALL include, as applicable:

- Completing or cancelling active operations.
- Saving application settings.
- Releasing Core resources.
- Releasing Importer resources.
- Closing external application windows managed by Photo Manager.
- Closing application windows.
- Terminating the application.

The Window Manager SHALL release its runtime resources and coordinate
closure of application windows as required.

The Settings Manager SHALL persist any application configuration changes
that require saving.

The Project Manager SHALL ensure that required project state has been
persisted before the application terminates.

Shutdown SHALL leave persistent project data and application
configuration in a valid recoverable state.


## 14.11 Lifecycle Ownership

The Orchestrator owns coordination of the Application Lifecycle.

Individual components remain responsible for operations within their
defined areas of ownership.

The following ownership rules apply:

- The Orchestrator coordinates lifecycle and workflow.
- The Project Manager owns persistent project state.
- The Settings Manager owns persistent application configuration.
- The Importer Manager owns Importer discovery and activation.
- The Window Manager owns application-window and GUI coordination.
- The User Interface presents information and collects user input.
- Importers own source-specific communication and acquisition.
- Finalise services perform project finalisation operations.
- The Logging Manager records significant lifecycle events and
  diagnostics.

No lifecycle phase transfers ownership of persistent state or Core
responsibilities from one component to another.

The Application Lifecycle therefore provides the operational framework
for the application while the component ownership and Application
State/Workflow Stage separation defined elsewhere in this specification
remain in force.

---

# 15. Logging Manager

The Logging Manager provides application-wide diagnostic and operational
logging for Photo Manager.

The Logging Manager provides a consistent logging service to Core
components and records information required to understand application
activity, diagnose failures and support development and maintenance.

The Logging Manager does not determine application workflow and does not
own application or project state.


## 15.1 Responsibilities

The Logging Manager is responsible for:

- Providing the application logging service.
- Recording significant application events.
- Recording workflow activity.
- Recording warnings.
- Recording errors.
- Recording diagnostic information.
- Providing consistent logging behaviour across Core components.
- Managing the application logging configuration.
- Managing logging resources.
- Supporting appropriate logging during application startup and
  shutdown.

The Logging Manager SHALL provide a consistent logging mechanism for
Core components.

Core components SHOULD use the Logging Manager rather than implementing
independent application logging mechanisms.


## 15.2 Logging Levels and Content

The Logging Manager MAY support different logging levels appropriate to
the operational and diagnostic requirements of the application.

The exact logging levels and their implementation are outside the
scope of this architectural specification.

Log records MAY include information such as:

- Timestamp.
- Component or service.
- Severity or logging level.
- Operation or activity.
- Diagnostic information.
- Error information where applicable.

Logging information SHALL be sufficient to support diagnosis of
significant application conditions without becoming a second source of
application state.


## 15.3 Component Logging

Core components SHALL be responsible for generating log information
relevant to their own operations.

Examples include:

- Application startup and shutdown.
- Project discovery and loading.
- Project creation.
- Importer discovery and activation.
- Importer communication.
- Registration activity.
- Acquisition activity.
- Recovery and retry activity.
- User-interface operations requiring diagnostic information.
- Project finalisation.
- Errors and warnings.

The Logging Manager records and manages this information but does not
interpret it as workflow commands.

A log message SHALL NOT by itself change Application State, Workflow
Stage or persistent project state.


## 15.4 Error and Diagnostic Logging

Errors and warnings that may affect application operation SHOULD be
logged with sufficient context to support diagnosis.

Where practical, diagnostic information SHOULD identify:

- The component reporting the condition.
- The operation being performed.
- The relevant project or operation context where appropriate.
- The error or warning condition.
- Additional information required for diagnosis.

Sensitive information SHALL NOT be written to logs unless explicitly
required and appropriately protected.

Credentials, authentication tokens and other sensitive source
information SHALL NOT be logged.


## 15.5 Interaction with Core Components

The Logging Manager provides a service used by Core components.

The Orchestrator MAY use logging to record application workflow and
lifecycle events.

The Project Manager MAY record project-management operations.

The Importer Manager MAY record Importer discovery and activation
events.

The Window Manager MAY record significant user-interface and window
operations.

Other Core components MAY use the Logging Manager where diagnostic or
operational logging is required.

Components SHALL NOT use logging as a substitute for their defined
interfaces or persistent state.


## 15.6 Relationship with Application State

Logging and application state are separate concerns.

The Logging Manager MAY record changes to Application State and Workflow
Stage for diagnostic purposes.

The Logging Manager SHALL NOT own Application State or Workflow Stage.

The Orchestrator remains responsible for determining application
workflow and state transitions.

The Project Manager remains responsible for persistent project state.


## 15.7 Logging Persistence

The Logging Manager MAY persist log information to files or other
appropriate logging destinations.

The exact storage mechanism is implementation dependent.

Logging persistence SHALL remain separate from project persistence.

Log information SHALL NOT be stored in `project.json`.

Loss of historical log information SHALL NOT make a project invalid or
prevent the Core from determining project state from its persistent
project data.


## 15.8 Startup and Shutdown

The Logging Manager SHALL be available sufficiently early during
application startup to record significant startup events.

During application shutdown, the Logging Manager SHALL release its
logging resources and, where required, ensure that pending log
information has been written to its configured destination.

Logging failure during shutdown SHALL NOT prevent orderly application
termination unless the implementation explicitly requires otherwise.


## 15.9 Ownership

The following ownership rules apply:

- The Logging Manager owns application logging services.
- Core components own the operational information they report through
  logging.
- The Orchestrator owns application workflow.
- The Project Manager owns persistent project state.
- The Settings Manager owns persistent application configuration.
- The Logging Manager does not own Application State or Workflow Stage.
- The Logging Manager does not own project state.
- The Logging Manager does not determine workflow.

Logging therefore provides an application-wide diagnostic service while
remaining independent of application control, workflow and persistent
data.
