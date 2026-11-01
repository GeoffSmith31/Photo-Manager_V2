# Photo Manager V2
# Core Design Specification

Document Status: Published
Document Version: 1.3

Defines:
    Photo Manager Design Version 2.0.0

Normative References:

Photo-Manager_Project-JSON-Reference.odt  Version 1.0
SPECIFICATION_STYLE_GUIDE.md              Version 1.0

---

# 1. Purpose

This document defines the internal design and architecture of the
Photo Manager Application.

The Application is responsible for managing project state
and providing the services required to load,
validate, edit and maintain Photo Manager projects.

Importers are standalone companion applications responsible for interacting with
their respective source systems, acquiring assets and producing
projects that conform to the Project JSON specification. The Photo
Manager Application consumes these projects; `project.json` defines
the contract between an Importer-produced project and Photo Manager.

This specification describes the internal organisation of the
Application, including its components, responsibilities and
interactions.

This document is intended for developers maintaining
the Photo Manager Application.  It may also be used by developers
of Importers, to understand Photo Manager.

---

# 2. Scope

This specification defines the internal architecture and design of the
Photo Manager Application, including:

- Application architecture and components.
- Project lifecycle and project state management.
- Application workflow and coordination.
- State management.
- Window management and user interaction.
- Metadata management.
- Settings management.
- Error handling and recovery.

This specification does not define:

- Individual companion Importer applications or their implementations.
- The structure and constraints of `project.json`, which are defined by
  the Project JSON Reference.
- The detailed visual design of the user interface.

Companion Importer applications operate independently of the Photo
Manager Application. Their interaction with Photo Manager is based on
the project structure and contract defined by the Project JSON
specification, rather than a runtime Core–Importer API.

This document describes the Application's internal design. It does not
prescribe the internal implementation of companion Importer
applications.

---

# 3. Application Architecture Overview

The Photo Manager Application is organised as a collection of
cooperating components, each with a defined responsibility.

These components work together to provide project management, workflow
coordination, user interaction, metadata management, configuration and
diagnostic logging.

The Application coordinates its own activities and manages the
projects it opens. Individual components remain responsible for their
assigned functions and SHALL NOT assume ownership of responsibilities
assigned to other components.

Companion Importer applications operate independently of Photo Manager.
They interact with their respective source systems, acquire assets and
produce projects conforming to the Project JSON specification. The
Photo Manager Application consumes these projects through the
project structure defined by that specification. It does not manage
Importer execution through a runtime Core–Importer API.

## 3.1 Architectural Model

The Photo Manager Application uses a component-based architecture.

At the highest level, the Application consists of:

- **Application services** that establish and manage the running
  application.
- **Coordination services** that control application workflow and
  component interaction.
- **Project services** that discover, load, validate and maintain
  projects.
- **User-interface components** that present information and accept
  user actions.
- **Supporting services** that provide application state, configuration
  and diagnostic logging.

The architecture separates workflow coordination from project
management and user interaction. The Orchestrator coordinates
application activity, while the Project Manager is responsible for
project data and persistence.

The Application's internal components communicate through defined
interfaces and respect the responsibilities assigned to each component.

## 3.2 Application Components

The principal components of the Photo Manager Application are described
in the following sections.

These descriptions define the intended responsibilities and boundaries
of each component. The detailed operation of each component, including
its interactions with other components, is specified in the relevant
sections of this document.

### 3.2.1 Application

The Application is responsible for establishing and terminating the
Photo Manager Application.

It creates and connects the principal application components and
provides the top-level environment in which they operate.

The Application manages application startup and shutdown but does not
itself coordinate project workflow. That responsibility belongs to the
Orchestrator.

### 3.2.2 Orchestrator

The Orchestrator coordinates activity within the Photo Manager
Application.

It is responsible for:

- Controlling the overall application workflow.
- Coordinating the activities of application components.
- Responding to user actions that require workflow changes.
- Initiating project discovery, loading and editing operations.
- Managing transitions between application states and workflow stages.
- Determining appropriate responses to operational conditions and
  failures.

The Orchestrator coordinates these activities but does not replace the
services responsible for performing them.

For example, the Orchestrator may instruct the Project Manager to load
a project, but the Project Manager remains responsible for the project
operation itself.

The Orchestrator is also responsible for maintaining the distinction
between application state and project workflow stage.


### 3.2.3 Project Manager

The Project Manager is responsible for managing Photo Manager projects.

It is responsible for:

- Discovering available projects.
- Loading existing projects.
- Validating project data.
- Maintaining `project.json`.
- Persisting project changes.
- Providing project information required by other application
  components.

The Project Manager is responsible for maintaining the integrity of
project data managed by the Photo Manager Application.

Other components SHALL NOT directly modify `project.json`. Project
data changes SHALL be performed through the appropriate project
management services.

The Project Manager does not determine the overall application
workflow. Workflow decisions remain the responsibility of the
Orchestrator.

Companion Importer applications are responsible for producing their
projects. The Project Manager manages those projects when they are
made available to the Photo Manager Application.


### 3.2.4 Project Selection

Project Selection provides the user interface and supporting logic
required to select an existing Photo Manager project.

It presents the projects discovered by the Project Manager and
communicates the user's selection to the Orchestrator.

Project Selection does not load or modify project data directly.
Loading the selected project is the responsibility of the appropriate
application services.


### 3.2.5 Control Tower

The Control Tower provides operational visibility and control for the
Photo Manager Application.

It presents information such as:

- Current application state.
- Current workflow stage.
- Current activity.
- Operational status.
- Errors, warnings and actions requiring user attention.

The Control Tower communicates user control requests to the Orchestrator
and presents operational information provided by the Application.

The Control Tower does not own workflow state or project state.
These remain the responsibility of the appropriate application
components.


### 3.2.6 Editor and User Interaction

The Editor and other user-interface components provide the user's
interaction with an active project.

They allow the user to view and modify information made available by
the Application for editing.

User-interface components SHALL request project operations through
the appropriate application services rather than directly modifying
persistent project data.

User interaction does not determine application workflow
independently. Actions that change workflow are communicated to the
Orchestrator.


### 3.2.7 Application State and Workflow Stage

The Application maintains two related but distinct concepts of state.

**Application State** represents the current operational state of the
running Photo Manager Application.

**Workflow Stage** represents the current progress of the active
project through the Photo Manager workflow.

These concepts SHALL remain distinct.

A change in Application State does not necessarily imply a
corresponding change in Workflow Stage, and a change in Workflow
Stage does not necessarily imply an immediate change in Application
State.

The Orchestrator coordinates transitions between application states
and workflow stages in accordance with the current application
operation.


### 3.2.8 Settings Manager

The Settings Manager provides access to application configuration
required by the Photo Manager Application.

It manages application-level settings and environment information
rather than project-specific persistent state.

Components SHALL obtain configuration through the Settings Manager
service rather than maintaining independent copies of application
settings.

### 3.2.9 Logging Manager

The Logging Manager provides application-wide diagnostic and
operational logging.

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


### 3.2.10 Finalise Services

Finalise Services provide the operations required to complete a project
and transfer its processed assets to the user-selected destination.

Finalisation operations are initiated and coordinated by the
Orchestrator.

Finalise Services are responsible for performing the finalisation
operation but do not own overall application workflow.


## 3.3 Component Interaction

The Photo Manager Application components cooperate through defined
interfaces, with the Orchestrator coordinating application workflow.

The general relationship between the principal components is:

```text


             +-------------------+-------------------+
             |                                       |
             v                                       v
     +---------------+                       +---------------+
     | Settings      |                       | Logging       |
     | Manager       |                       | Manager       |
     +---------------+                       +---------------+


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
     | Project       |   | Finalise       |   | Application   |
     | Manager       |   | Services       |   | State /       |
     |               |   |               |   | Workflow      |
     +-------+-------+   +---------------+   +---------------+
             |
             v
       `project.json`

```

The diagram is conceptual and does not prescribe the implementation
mechanism or require every interaction between components to pass
through the Orchestrator.

The Orchestrator coordinates application workflow but does not replace
the services responsible for performing individual operations.

The Project Manager is responsible for project data and persistence,
including maintaining `project.json`. Other components SHALL use the
appropriate project management services rather than directly modifying
persistent project data.

Supporting services, including the Settings Manager and Logging
Manager, provide application-wide functions to the components that
require them.

Companion Importer applications are outside this component model. They
operate independently and produce projects that the Photo Manager
Application can discover and load according to the Project JSON
specification.


## 3.4 Workflow Coordination

The Orchestrator coordinates the major workflows within the Photo
Manager Application.

The Application works with projects produced by standalone companion
Importer applications. It does not select or activate Importers, perform
source-specific operations, or coordinate the acquisition of assets
from source systems.

A typical workflow for opening an existing project involves the
following steps:

1. The Application discovers available projects.
2. The user selects a project through Project Selection.
3. The Orchestrator coordinates loading of the selected project.
4. The Project Manager loads and validates the project data.
5. The Application makes the loaded project available for the
   appropriate workflow.
6. The user can edit the project and its associated metadata.
7. When required, the Orchestrator coordinates project finalisation.

The Project Manager performs project loading, validation and
persistence operations. The Editor and other user-interface components
provide the appropriate editing and interaction facilities, while
Finalise Services perform the finalisation operations.

The Orchestrator coordinates these activities but does not replace the
components responsible for performing them.

The Application SHALL handle project loading and validation in
accordance with the Project JSON specification. Any failure to load or
validate a project SHALL be handled through the Application's normal
error-handling and reporting mechanisms.


## 3.5 Project JSON Contract

Standalone companion Importer applications and the Photo Manager
Application are independent applications. Their integration is based
on the project structure defined by the Project JSON specification,
rather than a runtime API.

Companion Importer applications are responsible for:

- Interacting with their respective source systems.
- Acquiring the required assets.
- Translating source information into the Photo Manager project
  structure.
- Producing projects that conform to the Project JSON specification.

The Photo Manager Application is responsible for:

- Discovering available projects.
- Loading and validating selected projects.
- Managing project data and persistent changes.
- Providing project editing and finalisation operations.

The `project.json` file defines the project structure and provides the
contract through which an Importer-produced project is consumed by the
Photo Manager Application.

The Project JSON Reference is the authoritative specification for the
structure, fields, constraints and interpretation of `project.json`.
This design specification SHALL NOT redefine those details.

The Photo Manager Application SHALL validate project data before
relying on it for application operations. Project data changes made by
Photo Manager SHALL preserve the requirements of the Project JSON
specification.

No runtime communication between a companion Importer and the
Photo Manager Application is required by this architecture. The
Importer produces the project, and Photo Manager consumes it
independently.

This separation allows companion Importer applications and the
Photo Manager Application to be developed and maintained independently,
provided that the projects they exchange conform to the Project JSON
specification.


## 3.6 Architectural Ownership

The following ownership rules apply throughout the Photo Manager Application architecture.

- **The Application** owns application startup, shutdown and the establishment of the principal application components.
- **The Orchestrator** owns application workflow coordination and coordinates transitions between application states and workflow stages.
- **The Project Manager** owns project data management, validation and persistence, including maintenance of `project.json`.
- **Project Selection, Control Tower, Editor and other user-interface components** own their respective presentation and user interaction responsibilities. They SHALL request application operations through the appropriate services.
- **Application State and Workflow Stage** represent distinct concepts maintained by the Application and coordinated by the Orchestrator.
- **The Settings Manager** owns application configuration.
- **The Logging Manager** owns application-wide diagnostic and operational logging.
- **Finalise Services** own the execution of project finalisation operations.
- **Standalone companion Importer applications** own source-specific communication, asset acquisition and the production of projects conforming to the Project JSON specification.

The Project JSON specification defines the contract between standalone Importer applications and the Photo Manager Application. Neither application assumes responsibility for the internal operation of the other.

Within Photo Manager, components SHALL respect the responsibilities assigned to other components. A component SHALL NOT directly modify data or state owned by another component except through the appropriate defined interface or service.

These ownership boundaries are intended to preserve modularity, make responsibilities explicit and allow individual components and companion applications to evolve independently without transferring their responsibilities to unrelated components.
---

# 4. Design Goals

The Photo Manager Application architecture has been designed to achieve the following goals.

- Provide a clear separation of responsibilities between Application components.
- Keep application workflow coordination separate from the services that perform individual operations.
- Maintain clear ownership of project data and persistent project state.
- Keep source-specific behaviour within standalone companion Importer applications.
- Provide a stable and well-defined project contract between Importers and Photo Manager through the Project JSON specification.
- Keep user-interface components separate from project and workflow management.
- Maintain a clear distinction between Application State and Workflow Stage.
- Keep workflow coordination and operational decisions under Orchestrator control, while leaving individual operations to their responsible components.
- Allow Application components to evolve independently while maintaining their defined interfaces and responsibilities.
- Minimise direct dependencies between components.
- Prevent components from directly modifying data or state owned by another component outside the appropriate defined interfaces or services.
- Provide sufficient diagnostic information to understand application activity and failures.
- Allow future companion Importers to be added without requiring changes to source-independent Photo Manager functionality, provided their projects conform to the Project JSON specification.
- Maintain the integrity and consistency of persistent project data.

The architecture should favour simple, explicit component interactions over implicit dependencies or duplicated responsibility.

Where a responsibility can be clearly assigned to one component, that component SHALL remain the authoritative owner of that responsibility.

The architecture should also allow future functionality to be added without unnecessarily changing the responsibilities or interfaces of existing components.

---

# 5. Architectural Principles

The following principles govern the design and implementation of the Photo Manager Application.

## 5.1 Clear Responsibility

Each Application component SHALL have a clearly defined responsibility.

A component SHALL NOT assume responsibility for functions that belong to another component.

Where responsibilities overlap, the owning component SHALL remain the authoritative source for the affected state or behaviour.

## 5.2 Explicit Ownership

Persistent data and application state SHALL have a clearly defined owner.

Components SHALL NOT directly modify data or state owned by another component except through the appropriate defined interface or service.

The Project Manager is the authoritative owner of project data managed by Photo Manager, including persistent project state.

The Orchestrator is the authoritative coordinator of application workflow.

## 5.3 Coordination and Execution are Separate

The Orchestrator SHALL coordinate application activity but SHALL NOT perform operations that belong to specialised components.

For example, the Orchestrator may coordinate project discovery, project loading, editing workflows or finalisation without itself implementing the project-management, user-interface or finalisation operations required to perform those activities.

This separation keeps workflow logic independent from the implementation details of individual operations.

## 5.4 Separation of Source-Specific Behaviour

Source-specific behaviour SHALL remain within standalone companion Importer applications.

The Photo Manager Application SHALL operate on the project structure defined by the Project JSON specification and SHALL NOT contain assumptions about the implementation or behaviour of a particular source system.

This principle allows additional Importers to be developed without introducing source-specific logic into Photo Manager, provided their projects conform to the Project JSON specification.

## 5.5 Separation of User Interaction

User-interface components SHALL be responsible for presenting information and receiving user interaction.

They SHALL NOT become the authoritative owners of project data or application workflow state.

User interaction SHALL cause the appropriate Application service or workflow operation to be invoked.

## 5.6 Application State and Workflow Stage

Application State and Workflow Stage SHALL remain distinct concepts.

Application State represents the current operational condition of the running application.

Workflow Stage represents the progress of the active project through the application workflow.

A change in one SHALL NOT be assumed to imply an immediate change in the other.

The Orchestrator coordinates transitions involving application state and workflow stage.

## 5.7 Persistent State and Recovery

The Project Manager SHALL maintain the persistent project data managed by Photo Manager.

Project loading and validation SHALL follow the requirements of the Project JSON specification.

The Application SHALL handle operational failures through its established error-handling and reporting mechanisms.

The detailed requirements for recovery after application restart, including the persistence of incomplete-operation state and the handling of interrupted operations, SHALL be defined in the relevant project-lifecycle and error-handling sections of this specification.

Standalone Importers are responsible for producing projects that conform to the Project JSON specification. They do not own the persistent project state subsequently managed by Photo Manager.

## 5.8 Stable Interfaces

Interfaces between Application components SHALL be explicit and stable.

Internal implementation details SHALL NOT become implicit dependencies between components.

The integration boundary between standalone Importers and Photo Manager SHALL be defined by the Project JSON specification, rather than by a runtime API or assumptions about a particular Importer implementation.

The Project JSON Reference is authoritative for the structure, fields and constraints of `project.json`.

## 5.9 Validation at Ownership Boundaries

A component SHALL validate data for which it is responsible before that data is accepted as authoritative within its domain.

The Project Manager SHALL validate project data in accordance with the Project JSON specification before relying on that data for application operations or persisting changes to it.

Standalone Importers SHALL ensure that the projects they produce conform to the Project JSON specification.

## 5.10 Controlled Extension

New functionality SHOULD be added by extending the appropriate component or service rather than by transferring responsibility to an unrelated component.

New components or interfaces SHOULD be introduced only where they provide a clear architectural responsibility.

The architecture SHALL favour explicit and understandable interactions over unnecessary abstraction or indirection.

---

# 6. Orchestrator

The Orchestrator is the principal workflow coordination component of the Photo Manager Application.

It coordinates the activities of other Application components and controls the progress of the Application through its defined workflow.

The Orchestrator does not own persistent project data, project-management operations, user-interface presentation or the implementation of individual operations performed by other components.

The Orchestrator SHALL coordinate these operations through the appropriate Application services and component interfaces.

## 6.1 Responsibilities

The Orchestrator is responsible for:

- Coordinating the overall application workflow.
- Coordinating project discovery, selection and loading.
- Coordinating project editing operations.
- Maintaining and coordinating Application State.
- Maintaining and coordinating Workflow Stage.
- Responding to workflow-changing user actions.
- Determining the next workflow operation following completion or failure.
- Coordinating the response to operational failures.
- Coordinating project finalisation.
- Communicating operational status to user-interface components.
- Coordinating orderly application shutdown.

The Orchestrator SHALL coordinate workflow operations without assuming responsibility for the underlying project-management, user-interface or finalisation services.

## 6.2 Workflow Coordination

The Orchestrator determines which operation should occur next based on the current Application State, Workflow Stage, active project and relevant operational conditions.

The Orchestrator SHALL delegate individual operations to the component responsible for performing them.

For example:

- Project discovery, loading, validation and persistence SHALL be performed by the Project Manager.
- Project selection SHALL be provided by Project Selection.
- Project editing and user interaction SHALL be provided by the appropriate user-interface components and Application services.
- Application configuration SHALL be provided by the Settings Manager.
- Diagnostic logging SHALL be performed by the Logging Manager.
- Project finalisation SHALL be performed by Finalise Services.

The Orchestrator SHALL coordinate these activities but SHALL NOT replace the components responsible for performing them.

Standalone Importer applications operate independently of the Photo Manager Application. The Orchestrator does not discover, select, activate or coordinate Importers, or manage their source-specific operations.

## 6.3 Application State

The Orchestrator coordinates Application State.

Application State represents the current operational condition of the running Application.

Application State SHALL describe what the Application is currently doing or waiting for, rather than the persistent progress of the project.

The Orchestrator SHALL coordinate changes to Application State as the Application enters, progresses through or leaves an operational condition.

Application State SHALL NOT be used as a substitute for persistent project state or Workflow Stage.

## 6.4 Workflow Stage

The Orchestrator coordinates Workflow Stage.

Workflow Stage represents the progress of the active project through the Photo Manager workflow.

Workflow Stage SHALL remain distinct from Application State.

The Orchestrator SHALL use Workflow Stage when determining the appropriate next workflow operation and SHALL use Application State to represent the current operational condition while that operation is being performed.

A change in Workflow Stage SHALL NOT be assumed to require an immediate change in Application State, and a change in Application State SHALL NOT necessarily change Workflow Stage.

## 6.5 Project Discovery and Selection

The Orchestrator coordinates the workflow for discovering and selecting an existing Photo Manager project.

The Project Manager is responsible for discovering available projects. Project Selection presents the available projects to the user and communicates the user's selection to the Orchestrator.

Following selection, the Orchestrator SHALL coordinate loading and validation of the selected project through the Project Manager.

The Photo Manager Application does not create a new project through this workflow. Projects are produced by standalone companion Importer applications and made available for Photo Manager to discover and load.

## 6.6 Existing Project Operations

When an existing project is selected, the Orchestrator SHALL coordinate its loading and validation through the Project Manager.

Following successful loading, the Orchestrator SHALL coordinate the appropriate workflow for the active project.

This may include:

- Making the project available for editing.
- Coordinating further project operations.
- Responding to operational errors or conditions requiring user attention.
- Coordinating finalisation when requested and appropriate.

The Orchestrator SHALL base workflow decisions on the project information provided by the Project Manager and the current Application State and Workflow Stage.

The Project Manager remains responsible for project data, validation and persistence. The Orchestrator SHALL NOT directly modify `project.json`.

## 6.7 Project Editing Coordination

The Orchestrator coordinates workflow-changing actions arising from project editing.

User-interface components SHALL communicate relevant user actions through the appropriate Application interfaces.

The Orchestrator SHALL determine whether a requested workflow change is appropriate in the current Application State and Workflow Stage, and SHALL coordinate the corresponding operation through the responsible component or service.

The Orchestrator does not own the editing interface or directly perform project-data persistence.

Project changes SHALL be handled through the appropriate project-management services.

## 6.8 Finalisation Coordination

The Orchestrator coordinates project finalisation when requested and appropriate for the current workflow.

It SHALL determine whether finalisation can proceed under the current application conditions and SHALL delegate the operation to Finalise Services.

Finalise Services are responsible for performing the finalisation operation.

The Orchestrator SHALL coordinate the workflow response to the reported outcome, including completion or failure, without assuming responsibility for the implementation of finalisation itself.

## 6.9 Error and Failure Handling

The Orchestrator SHALL coordinate the workflow response to operational failures.

It SHALL distinguish between:

- A failure of an individual operation.
- A condition requiring user intervention.
- A failure that prevents the current workflow from continuing.
- A failure for which the workflow can continue after an appropriate response.

The Orchestrator SHALL NOT suppress failures that require user attention.

Diagnostic information SHALL be recorded through the Logging Manager.

The Orchestrator SHALL determine the appropriate workflow response but SHALL NOT replace the diagnostic or error-handling responsibilities of the component that detected the failure.

Detailed recovery requirements, including behaviour following application interruption or restart, SHALL be defined in the relevant project-lifecycle and error-handling sections of this specification.

## 6.10 User Interaction

The Orchestrator receives workflow-changing requests from user-interface components.

It SHALL determine whether the requested action is appropriate in the current Application State and Workflow Stage.

User-interface components SHALL NOT directly change Application State, Workflow Stage or persistent project state.

The Orchestrator SHALL communicate workflow decisions and operational outcomes to the appropriate user-interface components through the defined Application interfaces.

## 6.11 Shutdown

The Orchestrator SHALL coordinate orderly application shutdown.

Where an operation is in progress, the Orchestrator SHALL coordinate the appropriate shutdown behaviour through the responsible Application components.

The Application SHALL handle persistent project data in accordance with the Project Manager's responsibilities and the requirements of the Project JSON specification.

The detailed behaviour for interrupted operations and recovery following application restart SHALL be defined by the relevant lifecycle and error-handling requirements.

## 6.12 Ownership Boundaries

The Orchestrator owns workflow coordination but does not own the persistent data or implementation of the operations it coordinates.

The following boundaries apply:

- The Orchestrator owns workflow coordination and decisions.
- The Project Manager owns project data management, validation and persistence.
- Project Selection owns the project-selection interface and supporting logic.
- Other user-interface components own their respective presentation and user interaction responsibilities.
- The Settings Manager owns application configuration.
- The Logging Manager owns diagnostic and operational logging.
- Finalise Services own the execution of project finalisation operations.
- Standalone Importer applications own source-specific communication, asset acquisition and production of projects conforming to the Project JSON specification.

The Orchestrator SHALL use the appropriate component or service for each operation and SHALL NOT bypass established ownership boundaries.

---

# 7. Project Manager

The Project Manager is the Application component responsible for managing Photo Manager projects and their persistent state.

The Project Manager is the authoritative owner of project data managed by Photo Manager, including `project.json`.

It is responsible for discovering available projects, loading and validating selected projects, and persisting project changes.

Projects are produced by standalone companion Importer applications. The Project Manager manages these projects when they are made available to Photo Manager; it does not create new projects through the Photo Manager user interface.

The Project Manager does not determine overall application workflow. Workflow decisions remain the responsibility of the Orchestrator.

## 7.1 Responsibilities

The Project Manager is responsible for:

- Discovering available projects.
- Loading existing projects.
- Validating project data.
- Maintaining `project.json`.
- Persisting project changes.
- Providing project information to other Application components.
- Maintaining the integrity of the project workspace.
- Determining whether a project satisfies the applicable validation requirements for the requested operation.

The Project Manager SHALL be the authoritative owner of project data managed by Photo Manager.

Other Application components SHALL NOT directly modify `project.json`.

## 7.2 Project Discovery

The Project Manager provides the information required to identify available Photo Manager projects.

Project discovery SHALL:

- Identify candidate project workspaces.
- Locate the associated `project.json`.
- Validate sufficient project information for project selection.
- Provide project information required by Project Selection.
- Identify projects that cannot be presented as usable because they are invalid or incomplete.

Project discovery SHALL NOT modify project data.

The Project Manager SHALL NOT treat a project as valid merely because a `project.json` file exists.

A project SHALL satisfy the applicable validation requirements before being presented as a usable project.

### Project Discovery and Importer Separation

Standalone Importers are responsible for producing projects that conform to the Project JSON specification.

A project SHALL NOT be discoverable by Photo Manager unless it passes the validation requirements applied during project discovery. A project that fails those requirements SHALL be excluded from the available project list.

An Importer SHALL NOT modify a project once that project is discoverable by Photo Manager. Consequently, an Importer SHALL ensure that a project under construction is not discoverable by Photo Manager until its production is complete and the project satisfies the applicable validation requirements.

This boundary prevents Photo Manager from discovering projects that are still being created by an Importer. It does not imply that a project, once discovered, can never subsequently become invalid or unavailable.

## 7.3 Project Creation

The Photo Manager Application does not provide a project-creation workflow.

Standalone companion Importer applications are responsible for producing projects that conform to the Project JSON specification.

The Project Manager manages those projects when they become available to Photo Manager. It does not obtain source information directly from external source systems or create the initial project on behalf of an Importer.

## 7.4 Project Loading

The Project Manager loads an existing project when instructed by the Orchestrator.

Loading SHALL:

- Locate the selected project data.
- Read `project.json`.
- Validate the stored project data.
- Establish the in-memory representation required by the Application.
- Make the loaded project information available to the appropriate Application components.

A project that fails the applicable validation requirements SHALL NOT be made available for normal editing or workflow operations.

The Project Manager SHALL provide sufficient diagnostic information to help determine the cause of a loading or validation failure.

## 7.5 Project Validation

The Project Manager is responsible for validating project data before relying on it for Application operations.

Validation SHALL be performed in accordance with the Project JSON specification and SHALL include the applicable requirements for:

- Project structure and required fields.
- Field types, values and constraints.
- Project resources and references.
- Asset records and identifiers.
- Consistency of persistent project information.

The Project JSON Reference is authoritative for the structure, fields, constraints and interpretation of `project.json`.

This design specification SHALL NOT redefine those requirements.

The Project Manager SHALL distinguish between a project that satisfies the requirements for normal operation and one that cannot safely be used for the requested operation.

## 7.6 Persistent Project State

The Project Manager maintains the persistent project data managed by Photo Manager.

This includes the project information and asset records defined by the Project JSON specification, including user changes that Photo Manager is responsible for persisting.

Persistent project data SHALL remain consistent with the applicable Project JSON requirements.

The Project Manager SHALL NOT depend on runtime state retained by an Importer to determine the persistent state of a project.

Any additional requirements for recording incomplete operations or supporting recovery after application restart SHALL be defined in the relevant project-lifecycle and error-handling sections of this specification.

## 7.7 Asset Records

The Project Manager maintains the persistent asset records within a loaded project.

It SHALL preserve the distinction between source-provided information, user-editable information and information maintained or derived by Photo Manager, as defined by the Project JSON specification and the applicable application requirements.

The Project Manager SHALL preserve valid asset information when processing project changes.

It SHALL NOT invent source-specific information that has not been supplied by an Importer or another authorised source.

The structure and permitted contents of asset records are defined by the Project JSON Reference.

## 7.8 Project Data Integrity

The Project Manager SHALL protect the integrity of persistent project data.

It SHALL validate project changes before accepting them as valid persistent state.

Where a requested change would leave the project inconsistent with the Project JSON specification, the Project Manager SHALL reject the change or otherwise prevent the invalid data from being committed.

The Project Manager SHALL report persistence failures to the appropriate Application component.

It SHALL NOT silently discard persistent project data in response to an operational failure.

## 7.9 Persistence

The Project Manager is responsible for persisting changes to `project.json` and other project data for which it is responsible.

Persistence SHALL be performed in a manner that maintains the integrity of project data and protects against incomplete or failed updates to the extent supported by the implementation.

The Project Manager SHALL ensure that a failed persistence operation is reported to the appropriate Application component.

Persistent project changes SHALL NOT be reported as successfully committed until the Project Manager has confirmed that the persistence operation succeeded.

The detailed requirements for atomic updates, interrupted writes and recovery SHALL be specified where the relevant persistence and lifecycle behaviour is defined.

## 7.10 Interaction with the Orchestrator

The Orchestrator coordinates project operations and instructs the Project Manager to perform them.

The Project Manager SHALL perform the requested project operation and return its result.

The Project Manager SHALL NOT independently determine the overall Application State or Workflow Stage.

For example:

- The Orchestrator coordinates discovery and project selection.
- The Project Manager discovers available projects and provides their information.
- The user selects a project through Project Selection.
- The Orchestrator requests that the Project Manager load the selected project.
- The Project Manager loads and validates the project and reports the result.
- The Orchestrator determines the appropriate next workflow operation.

This separation keeps project management independent of overall workflow coordination.

## 7.11 Interaction with Standalone Importers

Standalone Importer applications produce projects that conform to the Project JSON specification.

The Photo Manager Application consumes those projects independently of the Importers.

There is no runtime API between standalone Importers and the Photo Manager Application. Importers produce projects conforming to the Project JSON specification, which Photo Manager discovers and consumes independently.

The Project Manager is responsible for managing project data once it is available to Photo Manager.

The Project Manager SHALL NOT assume responsibility for source-specific communication, source enumeration or asset acquisition performed by a companion Importer.

The Importer SHALL NOT directly modify project data while it is being managed by Photo Manager outside an explicitly defined and supported application workflow.

## 7.12 Interaction with User Interface

Project Selection and other user-interface components may request project information through the appropriate Application services.

User-interface components SHALL NOT directly modify `project.json` as part of normal application operation.

The Project Manager provides the project information required for presentation while retaining responsibility for the underlying persistent data.

Project-selection and loading failures SHALL be reported to the appropriate Application components so that the user can be informed where necessary.

## 7.13 Ownership Boundary

The Project Manager owns project data management, validation and persistence within the Photo Manager Application.

It does not own:

- Overall application workflow.
- User-interface presentation.
- Importer discovery or activation.
- Source-system communication.
- Source-specific asset enumeration or acquisition.
- Application-wide diagnostic logging.
- Application configuration.
- Execution of project finalisation operations.

Those responsibilities belong to the appropriate Application component or standalone companion Importer.

The Project Manager SHALL remain the authoritative component for managing the project data that Photo Manager loads and maintains.

---
# 8. Project Selection

Project Selection provides the user interface and supporting logic used to select an existing Photo Manager project.

Project Selection obtains available project information from the Project Manager and communicates the user's selection to the Orchestrator.

Project Selection does not own project data and does not perform project loading, validation or persistence.

## 8.1 Responsibilities

Project Selection is responsible for:

- Presenting available projects to the user.
- Presenting sufficient project information to allow a project to be selected.
- Indicating projects that are unavailable or invalid where appropriate.
- Accepting a user's project selection.
- Communicating the selected project to the Orchestrator.
- Refreshing its displayed project information when instructed by the Application.

## 8.2 Project List

Project Selection obtains the available project list from the Project Manager.

The project list SHALL contain sufficient information to identify each project to the user.

This MAY include:

- Project name.
- Project location.
- Project validity or availability.
- Thumbnail information where available.
- Other project information required by the user interface.

Project Selection SHALL NOT determine project validity independently of the Project Manager.

The Project Manager remains the authoritative source for project discovery and validation.

## 8.3 Project Selection

When the user selects an existing project, Project Selection SHALL communicate the selection to the Orchestrator.

The selection SHALL identify the project using the project reference or identifier provided for that purpose by the Application.

Project Selection SHALL NOT load `project.json` directly as part of the selection operation.

The Orchestrator SHALL determine the subsequent workflow operation.

## 8.4 Project Selection Records

The Application MAY maintain temporary in-memory records for projects displayed by Project Selection.

Such records MAY contain information required to identify and present each project, including its name, location, thumbnail information and availability for selection.

These records are temporary application state and SHALL NOT be treated as persistent project state.

The Project Manager remains responsible for authoritative project information.

## 8.5 Invalid Projects

If the Project Manager identifies a project as invalid or unavailable, Project Selection MAY display the project with an appropriate indication of its condition.

Project Selection SHALL NOT attempt to repair or modify the project.

The user interface MAY provide information explaining why the project cannot be selected.

Any recovery or repair operation SHALL be initiated through the appropriate Application workflow.

## 8.6 Interaction with the Project Manager

The Project Manager provides Project Selection with information about available projects.

Project Selection presents that information to the user but does not become its owner.

The general interaction is:

1. The Project Manager discovers available projects.
2. The Project Manager validates the information required for selection.
3. Project Selection receives the resulting project information.
4. Project Selection presents the projects to the user.
5. The user selects a project.
6. Project Selection communicates the selection to the Orchestrator.

## 8.7 Interaction with the Orchestrator

The Orchestrator controls the workflow resulting from the user's selection.

For an existing project, the Orchestrator coordinates loading and validation through the Project Manager.

Project Selection SHALL NOT independently initiate project loading or other workflow operations.

## 8.8 Refresh

Project Selection MAY refresh its displayed information when instructed by the Application.

A refresh MAY be required after:

- Changes to the collection of available projects.
- Detection of a project that has become invalid or unavailable.
- Changes to project information that affect its presentation.

Refreshing the displayed project list SHALL NOT modify project data.

## 8.9 Ownership Boundary

Project Selection owns the presentation and selection of available projects.

It does not own:

- Persistent project state.
- `project.json`.
- Project discovery.
- Project validation.
- Project loading.
- Project persistence.
- Overall application workflow.
- Source-system communication or asset acquisition.

Those responsibilities belong to the Project Manager, Orchestrator or standalone companion Importers, as appropriate.

Project Selection SHALL remain a user-interface component rather than a project-management component.

---

# 9. Application State and Workflow Stage

The Photo Manager Application maintains two related but distinct concepts of state:

- Application State.
- Workflow Stage.

These concepts represent different aspects of the Application's operation and SHALL NOT be treated as a single state machine.

Application State represents the current operational condition of the running Photo Manager Application.

Workflow Stage represents the current progress of the active project through the Photo Manager workflow.

The Orchestrator is responsible for coordinating both concepts.

## 9.1 Application State

Application State represents the current operational condition of the running Photo Manager Application.

It describes what the Application is currently doing or waiting for.

Examples include:

- Starting.
- Selecting a project.
- Loading a project.
- Editing.
- Finalising.
- Waiting for user action.
- Shutting down.

The exact set of Application States is defined by the implementation and MAY be extended as required.

The Orchestrator SHALL be the authoritative owner of runtime Application State.

Application State SHALL NOT be treated as persistent project data.

## 9.2 Workflow Stage

Workflow Stage represents the progress of the active project through the Photo Manager workflow.

Workflow Stage describes the project's position within the application workflow rather than the instantaneous operational condition of the Application.

The existing implementation defines Workflow Stages associated with:

- Project creation.
- Registration.
- Acquisition.
- Editing.
- Finalisation.
- Completion.

These stages have been retained in the implementation following the architectural separation of Importers from the Photo Manager Application.

The Project Creation, Registration and Acquisition stages are legacy stages and are not used by the current Photo Manager workflow.

No new Workflow Stages have been introduced as part of the architectural revision.

The Orchestrator SHALL coordinate Workflow Stage.

Where Workflow Stage information forms part of persistent project data, the Project Manager SHALL remain responsible for storing and maintaining that persistent representation.

## 9.3 Separation of Application State and Workflow Stage

Application State and Workflow Stage SHALL remain distinct.

A change in Application State does not necessarily imply a change in Workflow Stage.

A change in Workflow Stage does not necessarily imply an immediate change in Application State.

The Application may transition between operational states without changing the active project's Workflow Stage.

Similarly, a change in Workflow Stage does not necessarily require an immediate change in the Application's operational condition.

This separation allows the Application to represent both its current operational condition and the progress of the active project without combining them into a single state model.

## 9.4 State Transitions

The Orchestrator SHALL determine when Application State or Workflow Stage changes are required.

State transitions SHALL be coordinated through the Orchestrator rather than initiated independently by user-interface components.

Components SHALL report relevant conditions or completed operations to the Orchestrator through their defined interfaces.

The Orchestrator SHALL determine the resulting Application State and Workflow Stage in accordance with the current operation.

The implementation MAY validate permitted state transitions. Such validation SHALL support the Orchestrator rather than becoming an independent source of workflow decisions.

## 9.5 Persistence

Application State is runtime state and SHALL NOT be treated as persistent project data.

Workflow Stage MAY be represented in persistent project data where required by the project workflow.

The Project Manager is responsible for the persistent representation of Workflow Stage where one exists.

The Orchestrator remains responsible for interpreting the available project information and determining the appropriate runtime state when a project is loaded.

Neither Application State nor Workflow Stage requires a separate State Manager component.

## 9.6 Interaction with Application Components

The Orchestrator coordinates state information with other Application components as required.

The Project Manager provides project information, including any persistent workflow information.

The Control Tower presents current Application State, Workflow Stage and current activity to the user.

The Editor presents project information appropriate to the current workflow.

The Logging Manager records significant state transitions and workflow events for diagnostic purposes.

No component other than the Orchestrator SHALL independently determine the overall application workflow.

## 9.7 Ownership

The following ownership rules apply:

The Orchestrator owns runtime Application State and coordinates Workflow Stage.

The Project Manager owns persistent project state, including any persistent representation of Workflow Stage.

User-interface components present state but do not own it.

Standalone Importers do not determine Photo Manager workflow.

The Logging Manager records state and workflow events but does not control them.

There is no separate State Manager component in the Photo Manager Application architecture.

Keeping state coordination with the Orchestrator and persistent project state with the Project Manager avoids introducing an additional component whose responsibilities would overlap with those components.

---

# 10. Window Manager

The Window Manager is the Application infrastructure service responsible for coordinating the graphical user interface and application windows.

The Window Manager provides the interface between Application components and the graphical user interface.

Application components SHALL NOT communicate directly with GUI windows where the Window Manager provides the required interface.

The Window Manager provides a consistent application-facing interface for:

- The Control Tower.
- User interaction dialogs.
- Project selection.
- Activity presentation.
- Workflow status presentation.
- External application windows.
- Window activation, focus and geometry.
- Application shutdown interaction.

The Window Manager does not own application workflow or persistent project state.

## 10.1 Responsibilities

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
- Forwarding user actions from the Control Tower to the Application.
- Releasing Window Manager resources during application shutdown.

The Window Manager SHALL provide these functions without becoming responsible for determining the overall application workflow.

## 10.2 Relationship with the Orchestrator

The Orchestrator is responsible for application workflow and determines when user-interface presentation or interaction is required.

The Window Manager provides the interface through which the Orchestrator requests that presentation or interaction.

The general relationship is:

```text
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
```

User actions travel back through the Window Manager to the Application.

The Window Manager therefore provides a two-way interface between application workflow and the graphical user interface.

The Orchestrator SHALL NOT directly manipulate Control Tower widgets or other GUI implementation details.

The Window Manager SHALL translate application-level presentation requests into the corresponding GUI operations.

## 10.3 Control Tower

The Control Tower is the principal operational user interface presented by the Window Manager.

The Window Manager creates and maintains the Control Tower instance and provides the application-facing interface to it.

The Window Manager MAY instruct the Control Tower to display:

- Project Selection.
- Workflow Stage status.
- Workflow Stage results.
- Current activity information.
- Photo Editor activity.
- Finalise activity.
- Status messages.
- Workflow actions.
- Other application information supported by the Control Tower.

The Window Manager SHALL remain responsible for determining how these requests are communicated to the Control Tower.

The Control Tower SHALL remain responsible for presenting the supplied information to the user.

The Control Tower does not own Application State, Workflow Stage or persistent project state.

## 10.4 User Actions

The Control Tower MAY generate user actions such as:

- Selecting a project.
- Selecting an available workflow action.
- Requesting another application operation.
- Responding to an interaction presented by the Application.

The Window Manager receives these actions from the Control Tower.

The Window Manager SHALL forward the action to the Application through the defined application callback or interface.

The Window Manager SHALL NOT determine the workflow consequence of a user action.

The Orchestrator remains responsible for determining what the action means within the current application workflow.

## 10.5 Activity Presentation
Project Discovery and Importer Separation

Standalone Importers are responsible for producing projects that conform to the Project JSON specification.

A project SHALL NOT be discoverable by Photo Manager unless it passes the validation requirements applied during project discovery. A project that fails those requirements SHALL be excluded from the available project list.

An Importer SHALL NOT modify a project once that project is discoverable by Photo Manager. Consequently, an Importer SHALL ensure that a project under construction is not discoverable by Photo Manager until its production is complete and the project satisfies the applicable validation requirements.

This boundary prevents Photo Manager from discovering projects that are still being created by an Importer. It does not imply that a project, once discovered, can never subsequently become invalid or unavailable.
The Window Manager provides operations for presenting the major application activities.

Activities may include:

- Project Selection.
- Photo Editor.
- Finalise.
- Other operational activities introduced by the Application.

When presenting a new activity, the Window Manager MAY clear or replace the previous activity and update the Control Tower activity title as required.

The Window Manager is responsible for coordinating the presentation change.

The Orchestrator remains responsible for determining when the Application changes from one activity to another.

## 10.6 Workflow Stage Presentation

The Window Manager provides the interface through which the current Workflow Stage status and result are presented in the Control Tower.

The Window Manager SHALL accept the Workflow Stage and associated display information from the Application and pass the information to the Control Tower.

The Window Manager MAY also request that corresponding workflow actions be displayed for the selected Workflow Stage.

The Window Manager does not determine the Workflow Stage or its transition.

Workflow Stage remains coordinated by the Orchestrator as defined in Section 9.

## 10.7 User Interaction

The Window Manager provides common user-interaction services for the Application.

These include:

- Informational or warning messages requiring acknowledgement.
- Yes/No confirmation requests.
- Directory selection.
- Other modal interaction required by Application operations.

The Window Manager SHALL present the interaction and return the user's response where a response is required.

The Window Manager SHALL NOT determine the workflow consequence of the user's response.

The Orchestrator or the Application component requesting the interaction remains responsible for interpreting the result.

## 10.8 External Application Windows

The Window Manager MAY coordinate external application windows required by Photo Manager.

An example is opening a web browser to display Google Maps for the current photo.

The Window Manager is responsible for:

- Launching the supported external application.
- Maintaining the runtime reference required to manage the external application.
- Detecting when the externally launched process has already terminated.
- Closing the external application when required by the associated Photo Manager operation.
- Reporting inability to launch the external application through the normal user-interaction mechanism.

The external application remains outside the ownership of the Photo Manager Application.

Closing an external application independently by the user SHALL NOT necessarily be treated as an application error.

## 10.9 Window and Display Management

The Window Manager is responsible for managing the presentation of the Control Tower window.

This includes:

- Discovering available display screens.
- Selecting the appropriate display for the Control Tower.
- Setting the Control Tower size.
- Setting the Control Tower position.
- Validating supplied window geometry.
- Applying suitable default geometry when supplied values are invalid or unavailable.
- Showing the Control Tower window.

Window geometry and display information are runtime presentation data and are not project state.

The Window Manager SHALL NOT use window-management operations to determine application workflow.

## 10.10 Ownership

The following ownership rules apply:

- The Orchestrator owns application workflow coordination.
- The Project Manager owns persistent project state.
- The Window Manager owns the interface between Application components and the graphical user interface.
- The Control Tower owns presentation of information supplied to it.
- The Control Tower does not own application workflow or project state.
- The Window Manager owns the runtime coordination of application windows and dialogs.
- External applications remain outside the ownership of the Photo Manager Application.

The Window Manager SHALL NOT:

- Determine application workflow.
- Determine Workflow Stage transitions.
- Modify `project.json` directly.
- Own persistent project state.
- Perform source-specific Importer operations.
- Replace the Orchestrator as the application workflow coordinator.

The Window Manager provides presentation and user-interaction services to the Application while maintaining a clear separation between application workflow and graphical user-interface implementation.

## 10.11 Architectural Boundary

The Window Manager forms the boundary between application workflow and the graphical user interface.

The intended relationship is:

```text
    Application Workflow
            |
            v
       Orchestrator
            |
            v
      Window Manager
            |
            v
    Control Tower / Dialogs /
      External Windows
```

The Orchestrator communicates application-level requirements to the Window Manager.

The Window Manager performs the required presentation or interaction using the appropriate GUI component.

User actions are returned through the Window Manager to the Application, where the Orchestrator determines the resulting workflow operation.

This boundary allows application workflow to remain independent of the underlying GUI implementation while providing a consistent interface for application windows and user interaction.

---

# 11. Settings Manager

The Settings Manager is the Application component responsible for managing persistent application configuration for Photo Manager.

The Settings Manager owns application-level settings and provides configuration services to Application components.

The Settings Manager does not manage project-specific information.

## 11.1 Responsibilities

The Settings Manager is responsible for:

- Loading application settings.
- Saving application settings.
- Validating application settings.
- Maintaining application configuration.
- Providing configuration information to Application components.
- Maintaining configuration consistency.
- Providing appropriate default values where required.

The Settings Manager SHALL be the authoritative owner of persistent application settings.

The Settings Manager SHALL NOT own persistent project state.

## 11.2 Application Configuration

Application configuration represents settings that apply to the Photo Manager Application rather than to an individual project.

Application configuration MAY include:

- User preferences.
- Application defaults.
- Window preferences.
- Other application-level configuration required by Application components.

The exact configuration items are implementation dependent and MAY be extended as the Application develops.

Project-specific information SHALL NOT be stored as application configuration.

## 11.3 Configuration Loading

The Settings Manager SHALL load application configuration when required by application startup or configuration operations.

The Settings Manager SHALL validate loaded configuration before making it available to the Application.

Where configuration is missing or invalid, the Settings Manager SHALL apply appropriate defaults or report the configuration condition to the requesting Application component.

Configuration loading SHALL NOT modify persistent project state.

## 11.4 Configuration Saving

The Settings Manager SHALL provide the means to persist changes to application configuration.

Configuration changes SHALL be validated before being persisted.

The Settings Manager SHALL ensure that successfully saved configuration represents valid application configuration.

The Settings Manager SHALL NOT modify `project.json` or other project-specific persistent data.

## 11.5 Interaction with Application Components

The Orchestrator coordinates application workflow and determines when configuration operations are required.

The Settings Manager provides the required configuration services.

Other Application components MAY obtain configuration information through the defined Settings Manager interface where that configuration is required for their operation.

Components SHALL NOT maintain independent persistent copies of application settings.

A component that requires application configuration SHALL obtain it through the appropriate configuration interface rather than accessing the Settings Manager's persistent storage directly.

## 11.6 Configuration Ownership

The Settings Manager is the authoritative owner of persistent application configuration.

The following ownership rules apply:

- The Settings Manager owns application configuration.
- The Project Manager owns persistent project state.
- The Orchestrator coordinates the use of configuration during application workflow.
- Application components may consume configuration required for their operation.
- No Application component SHALL directly modify the persistent configuration storage owned by the Settings Manager.

This separation ensures that application configuration and project-specific persistent data remain independent.

## 11.7 User Configuration

Where the Application provides user-editable settings, the user interface SHALL obtain and present those settings through the appropriate Application configuration interface.

The user interface SHALL NOT directly modify persistent configuration files.

Configuration changes requested by the user SHALL be validated by the Settings Manager before they become persistent.

## 11.8 Ownership Boundary

The Settings Manager owns application configuration but does not own:

- Application workflow.
- Application State.
- Workflow Stage.
- Project state.
- Source-specific communication performed by standalone Importers.
- User-interface presentation.
- Window management.

The Orchestrator remains responsible for workflow coordination.

The Project Manager remains responsible for project-specific persistent state.

The Window Manager remains responsible for application-window and user-interface coordination.

The Settings Manager therefore provides a clear boundary between application configuration and the operational state and persistent data managed by other Application components.

---

# 12. User Interface

The User Interface provides the mechanisms through which the user observes Photo Manager operation and performs user actions.

The User Interface consists of graphical components that present information supplied by the Application and collect user input.

The User Interface SHALL NOT own application workflow or persistent application or project state.

The Window Manager provides the principal interface between Application components and the graphical user interface.

The Orchestrator remains responsible for application workflow.

## 12.1 User Interface Responsibilities

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

User-interface components SHALL NOT independently implement application workflow.

User-interface components SHALL NOT directly modify persistent application or project data.

Workflow-changing user actions SHALL be returned to the Application through the Window Manager, where they are passed to the appropriate application workflow services and interpreted by the Orchestrator.

## 12.2 User Interface Components

The principal user-interface components are:

- Control Tower.
- Editor.

Additional dialogs and user-interface components MAY be provided where required by the Application.

The Window Manager coordinates the presentation and lifetime of these components.

The responsibilities of the principal components are described below.

## 12.3 Control Tower

### Purpose

The Control Tower provides the primary operational user interface for the Photo Manager Application.

The Control Tower presents the current operational condition of the Application and provides the user with access to actions appropriate to the current operation.

The Control Tower is intended to remain available throughout normal application operation.

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
- Perform source-specific Importer operations.
- Determine recovery or retry behaviour.

### Interaction with the Application

The Control Tower communicates with the Application through the Window Manager.

The Window Manager provides the Control Tower with information supplied by the Application and receives user actions generated by the Control Tower.

The Control Tower does not directly communicate with the Project Manager or other Application services to perform project-management or workflow operations.

The Window Manager forwards user actions to the Application, where the Orchestrator determines the appropriate workflow operation.

### Managed Data

The Control Tower does not own persistent application or project data.

It maintains only transient presentation information required to display the current application operation and collect user input.

### Notes

The Control Tower is the principal operational presentation component of Photo Manager.

It provides the user-facing representation of the current application activity but does not own or control the workflow represented by that activity.

## 12.4 Editor

### Purpose

The Editor provides the primary user interface for viewing and modifying the contents of an active project.

The Editor enables the user to review project assets, modify user-maintained metadata and perform project editing operations.

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
- Collecting user modifications for submission to the appropriate Application services.

### Interaction with the Application

The Editor communicates with the Application through the Window Manager for GUI coordination and through the appropriate Application services for project operations.

The Editor SHALL NOT directly access or modify `project.json`.

Changes made by the user SHALL be submitted to the appropriate Application service for validation and persistence.

The Project Manager remains responsible for persistent project state.

### Managed Data

The Editor does not own persistent project data.

It maintains only transient information required to display the active project and support user interaction.

The Editor MAY maintain temporary presentation state such as:

- Current asset selection.
- Current displayed asset.
- Search criteria.
- Filter criteria.
- Current editing values prior to submission.

Such information SHALL NOT be treated as authoritative project state.

### Notes

The Editor provides the primary working environment for managing an active Photo Manager project.

The Editor presents project information and collects user modifications.

The Editor does not determine application workflow.

## 12.5 Dialogs and Supporting User Interface

Photo Manager MAY use additional dialogs and supporting user-interface components for specific operations.

Examples include:

- Application Settings.
- Propagation Settings.
- User confirmation.
- User acknowledgement.
- Directory selection.
- Other interactions requiring user input.

Such components are presentation and interaction mechanisms.

They SHALL NOT independently determine application workflow or directly modify persistent application or project state.

The Window Manager provides the appropriate interface for presenting these components where required.

## 12.6 User Interface and Workflow

The User Interface represents the current application workflow but does not own it.

The general relationship is:

```text
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
    Application Services
```

The reverse flow is used to present information:

```text
    Application Services
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
```

The Orchestrator determines the workflow operation.

The Window Manager provides the GUI interface.

The User Interface presents information and collects user input.

This separation prevents presentation logic from becoming responsible for application workflow.

## 12.7 Ownership

The following ownership rules apply:

- The Orchestrator owns application workflow coordination.
- The Window Manager owns the interface between Application components and the graphical user interface.
- The Control Tower owns presentation of operational information and collection of operational user actions.
- The Editor owns presentation of project information and collection of project edits.
- The Project Manager owns persistent project state.
- The Settings Manager owns persistent application configuration.
- User-interface components do not own persistent application or project state.

No User Interface component SHALL directly modify persistent application or project data.

No User Interface component SHALL independently determine application workflow.

The User Interface therefore remains a presentation and interaction layer, while workflow, state and persistent data remain under the ownership of the appropriate Application components.

---

# 13. Application Lifecycle

The Application Lifecycle describes the major operational conditions and transitions of the Photo Manager Application.

The Orchestrator coordinates the Application Lifecycle.

The Application Lifecycle is concerned with the operation of the running Application and SHALL remain distinct from the Workflow Stage of the active project.

Application State describes the current operational condition of the Application.

Workflow Stage describes the progress of the active project through the Photo Manager workflow.

The relationship between Application State and Workflow Stage is defined in Section 9.

## 13.1 Lifecycle Model

The Application operates through a number of major operational conditions.

These include:

1. Startup.
2. Project Selection and idle operation.
3. Project Loading and Validation.
4. Project Editing.
5. Project Finalisation.
6. Shutdown.

These conditions describe the overall operation of the Application.

They SHALL NOT be interpreted as a single linear state machine.

The Application MAY move between operational conditions as a result of user actions, completion of operations, errors or application shutdown.

The active project's Workflow Stage remains independently represented where applicable.

## 13.2 Startup

During startup, the Orchestrator SHALL coordinate the initialisation of the Photo Manager Application.

Startup activities include:

- Initialising the required Application components.
- Loading application settings.
- Initialising the User Interface through the Window Manager.
- Verifying the application environment as required.
- Establishing the initial Application State.
- Presenting the appropriate initial user interface.

Startup SHALL NOT require an active project.

Startup SHALL NOT require the discovery, selection or activation of companion Importer applications.

Following successful startup, the Application SHALL enter its normal project-selection or idle operation.

If startup cannot be completed successfully, the Application SHALL report the failure through its available error-reporting mechanisms and terminate where continued operation is not possible.

## 13.3 Project Selection and Idle Operation

When no project operation is active, the Application SHALL remain available for user interaction.

The user MAY:

- Select an existing project.
- Modify application settings.
- Request application Help, where available.
- Exit the Application.

The Project Manager provides information about available projects.

The Window Manager presents the project-selection interface through the Control Tower.

The Orchestrator determines the operation resulting from the user's selection.

No project-editing or finalisation operation is active while the Application is idle.

The Photo Manager Application does not provide a workflow for creating a new project. Projects are produced by standalone companion Importer applications and made available for Photo Manager to discover and load.

## 13.4 Project Loading and Validation

When the user selects an existing project, the Orchestrator coordinates loading of the project through the Project Manager.

The Project Manager SHALL:

- Locate the selected project.
- Load the project data.
- Validate the project in accordance with the Project JSON specification.
- Establish the project representation required by the Application.
- Report the result of the loading and validation operation.

The Orchestrator SHALL determine the appropriate next operation based on the result and the project information made available by the Project Manager.

A project that passes the applicable validation requirements MAY be presented to the Editor.

A project that fails validation SHALL NOT be made available for normal editing or workflow operations.

Loading or validation failures SHALL be reported through the Application's error-handling mechanisms.

The detailed handling of incomplete or invalid projects SHALL be defined by the applicable project-lifecycle and error-handling requirements.

## 13.5 Project Editing

When a project is available for editing, the Orchestrator coordinates its presentation through the Editor.

During Project Editing, the user MAY:

- Review project assets.
- Modify user-maintained metadata.
- Search and filter assets.
- Select assets.
- View asset information and previews.
- Perform other supported project-editing operations.

The Editor presents project information and collects user modifications.

The appropriate Application services validate and process those modifications.

The Project Manager remains responsible for persistent project state and the persistence of project changes.

The Orchestrator remains responsible for overall application workflow.

## 13.6 Project Finalisation

Project Finalisation is the workflow operation that completes the project according to the applicable finalisation requirements and user-selected options.

The Orchestrator coordinates Finalisation.

Finalise Services perform the operations required to transfer or otherwise process the project according to the application's finalisation requirements.

The Project Manager remains responsible for persistent project state during the operation.

Following successful finalisation, the Orchestrator SHALL determine the appropriate next Application State.

Normally, this will return the Application to project selection or idle operation.

The detailed behaviour of Project Finalisation is defined by the Finalise Services and associated implementation requirements.

## 13.7 Error and Recovery Conditions

The Application SHALL respond to operational errors and interruptions according to the nature of the condition and the requirements of the affected operation.

### Project Discovery and Importer Separation

Standalone Importers are responsible for producing projects that conform to the Project JSON specification.

A project SHALL NOT be discoverable by Photo Manager unless it passes the validation requirements applied during project discovery. A project that fails those requirements SHALL be excluded from the available project list. Invalid projects MAY be logged with information to explain why the project is invalid.

An Importer SHALL NOT modify a project once that project is discoverable by Photo Manager. Consequently, an Importer SHALL ensure that a project under construction is not discoverable by Photo Manager until its production is complete and the project satisfies the applicable validation requirements.

This boundary prevents Photo Manager from discovering projects that are still being created by an Importer. It does not imply that a project, once discovered, can never subsequently become invalid or unavailable.

### Operational Errors and Interruptions

The Orchestrator SHALL coordinate the response to operational errors and interruptions.

Depending on the condition and the capabilities of the affected operation, the Application MAY:

- Request user interaction.
- Return to an appropriate operational condition.
- Cancel the current operation where supported.
- Terminate the Application where continued operation is not possible.

The Project Manager SHALL report the results of project loading, validation and persistence operations to the appropriate Application component.

A project that fails validation during loading SHALL NOT be made available for normal editing or workflow operations.

The Application SHALL NOT assume that an incomplete or invalid project can be repaired automatically or that an interrupted operation can be resumed unless that behaviour is explicitly supported by the implementation.

Errors and failures SHALL be reported through the Application's established error-reporting and diagnostic mechanisms.

The Application's recovery behaviour is limited to the responses supported by the affected operations and the implemented error-handling mechanisms. No additional recovery capability is implied by this specification.

## 13.8 Shutdown

The Orchestrator coordinates orderly application shutdown.

Shutdown SHALL include, as applicable:

- Completing or cancelling active operations where supported.
- Saving application settings where required.
- Releasing Application resources.
- Closing external application windows managed by Photo Manager where required.
- Closing application windows.
- Terminating the Application.

The Window Manager SHALL release its runtime resources and coordinate closure of application windows as required.

The Settings Manager SHALL persist application configuration changes that require saving.

The Project Manager SHALL manage project persistence in accordance with its responsibilities and the requirements of the Project JSON specification.

Shutdown SHALL NOT be reported as successful if a required shutdown operation has failed without being appropriately handled.

## 13.9 Lifecycle Ownership

The Orchestrator owns coordination of the Application Lifecycle.

Individual components remain responsible for operations within their defined areas of ownership.

The following ownership rules apply:

- The Orchestrator coordinates lifecycle and workflow.
- The Project Manager owns project data management and persistent project state.
- The Settings Manager owns persistent application configuration.
- The Window Manager owns application-window and GUI coordination.
- User-interface components present information and collect user input.
- Standalone Importers own source-specific communication, asset acquisition and production of projects conforming to the Project JSON specification.
- Finalise Services perform project-finalisation operations.
- The Logging Manager records significant lifecycle events and diagnostics.

No lifecycle phase transfers ownership of persistent state or Application responsibilities from one component to another.

The Application Lifecycle therefore provides the operational framework for Photo Manager while preserving the component ownership boundaries and the separation between Application State and Workflow Stage defined elsewhere in this specification.

---

# 14. Logging Manager

The Logging Manager provides application-wide diagnostic and operational logging for Photo Manager.

The Logging Manager provides a consistent logging service to Application components and records information required to understand application activity, diagnose failures and support development and maintenance.

The Logging Manager does not determine application workflow and does not own application or project state.

## 14.1 Responsibilities

The Logging Manager is responsible for:

- Providing the application logging service.
- Recording significant application events.
- Recording workflow activity.
- Recording warnings.
- Recording errors.
- Recording diagnostic information.
- Providing consistent logging behaviour across Application components.
- Managing logging resources.
- Supporting appropriate logging during application startup and shutdown.

The Logging Manager SHALL provide a consistent logging mechanism for Application components.

Application components SHOULD use the Logging Manager rather than implementing independent application logging mechanisms.

## 14.2 Logging Levels and Content

The Logging Manager MAY support different logging levels appropriate to the operational and diagnostic requirements of the Application.

The exact logging levels and their implementation are outside the scope of this architectural specification.

Log records MAY include information such as:

- Timestamp.
- Component or service.
- Severity or logging level.
- Operation or activity.
- Diagnostic information.
- Error information where applicable.

Logging information SHALL be sufficient to support diagnosis of significant application conditions without becoming a second source of application state.

## 14.3 Component Logging

Application components SHALL be responsible for generating log information relevant to their own operations.

Examples include:

- Application startup and shutdown.
- Project discovery and loading.
- Project validation and persistence.
- Project editing operations requiring diagnostic information.
- User-interface operations requiring diagnostic information.
- Project finalisation.
- Errors and warnings.

The Logging Manager records and manages this information but does not interpret it as workflow commands.

A log message SHALL NOT by itself change Application State, Workflow Stage or persistent project state.

## 14.4 Error and Diagnostic Logging

Errors and warnings that may affect application operation SHOULD be logged with sufficient context to support diagnosis.

Where practical, diagnostic information SHOULD identify:

- The component reporting the condition.
- The operation being performed.
- The relevant project or operation context where appropriate.
- The error or warning condition.
- Additional information required for diagnosis.

Sensitive information SHALL NOT be written to logs unless explicitly required and appropriately protected.

Credentials, authentication tokens and other sensitive source information SHALL NOT be logged.

## 14.5 Interaction with Application Components

The Logging Manager provides a service used by Application components.

The Orchestrator MAY use logging to record application workflow and lifecycle events.

The Project Manager MAY record project-management operations.

The Window Manager MAY record significant user-interface and window operations.

The Settings Manager MAY record configuration operations.

Finalise Services MAY record project-finalisation operations.

Other Application components MAY use the Logging Manager where diagnostic or operational logging is required.

Components SHALL NOT use logging as a substitute for their defined interfaces or persistent state.

## 14.6 Relationship with Application State

Logging and application state are separate concerns.

The Logging Manager MAY record changes to Application State and Workflow Stage for diagnostic purposes.

The Logging Manager SHALL NOT own Application State or Workflow Stage.

The Orchestrator remains responsible for determining application workflow and coordinating state transitions.

The Project Manager remains responsible for persistent project state.

## 14.7 Logging Persistence

The Logging Manager MAY persist log information to files or other appropriate logging destinations.

The exact storage mechanism is implementation dependent.

Logging persistence SHALL remain separate from project persistence.

Log information SHALL NOT be stored in `project.json`.

Loss of historical log information SHALL NOT make a project invalid or prevent the Application from determining project state from its persistent project data.

## 14.8 Startup and Shutdown

The Logging Manager SHALL be available sufficiently early during application startup to record significant startup events.

During application shutdown, the Logging Manager SHALL release its logging resources and, where required, ensure that pending log information has been written to its configured destination.

Logging failure during shutdown SHALL NOT prevent orderly application termination unless the implementation explicitly requires otherwise.

## 14.9 Ownership

The following ownership rules apply:

- The Logging Manager owns application logging services.
- Application components own the operational information they report through logging.
- The Orchestrator owns application workflow coordination.
- The Project Manager owns persistent project state.
- The Settings Manager owns persistent application configuration.
- The Logging Manager does not own Application State or Workflow Stage.
- The Logging Manager does not own project state.
- The Logging Manager does not determine workflow.

Logging therefore provides an application-wide diagnostic service while remaining independent of application control, workflow and persistent data.
