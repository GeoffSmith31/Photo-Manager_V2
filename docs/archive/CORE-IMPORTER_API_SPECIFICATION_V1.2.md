# Photo Manager V2
# Core-Importer API Specification

**Status:** Superseded
**Superseded by:** ADR-012 — Standalone Importers and Project JSON Contract
**Date:** 2026-10-21

> **Notice:** This specification describes an earlier Photo Manager architecture and is retained for historical reference only. It is no longer authoritative and must not be used as a requirement for new development. The `project.json` format is the contract between standalone Importers and Photo Manager. Refer to the Project JSON Reference for the authoritative description of that contract.
Document Version: 1.2

Defines:
    Core API Version 1

Normative References:

PROJECT_JSON.md               Version 2
SPECIFICATION_STYLE_GUIDE.md  Version 1.0

---

# 1. Purpose

This document defines the application programming interfaces (APIs) used for 
communication between the Photo Manager Core and Importer components.

It specifies the services provided by the Core, the services provided by an 
Importer and the behavioural requirements governing their interaction.

It also defines the interfaces and information used by the Core to discover 
compatible Importers and determine their declared capabilities.

This specification defines the interface contract only. It does not specify 
implementation details, user interface behaviour or internal component design.

---

# 2. Scope

This specification applies to all Importers developed for the Photo
Manager system, regardless of the source from which assets are imported.

It defines:

- The Core API implemented by the Photo Manager Core.
- The Importer API implemented by Importers.
- The interface used by the Core to discover available Importers and
  determine their declared capabilities.
- The communication protocol between these components.
- The behavioural requirements governing interaction between the Core and
  an active Importer.

This specification does not define:

- The internal implementation of the Core.
- The internal implementation of Importers.
- User interface design.
- The Project JSON schema.

---

# 3. Architecture Overview

The Photo Manager import system is composed of two primary components:

- **The Core**, which manages projects, assets, metadata, workflow and
  application-level user interaction.
- **An Importer**, which communicates with a specific source system and
  translates source-specific information into the canonical Photo
  Manager data model.

The Core and Importer communicate through well-defined application
programming interfaces (APIs).

The Core is responsible for discovering available Importers and
determining whether they are compatible with the current Core API.

Importer discovery SHALL NOT activate an Importer or establish a
connection to the source system.

An Importer SHALL be activated only when the Core selects it for an
import operation.

Following activation, the Importer SHALL initialise its source-specific
resources and interact with the user as required to prepare the import.
This interaction MAY include authentication, source or workspace
selection, and gathering information required to construct the initial
project configuration.

Once sufficient information has been obtained to create the project, the
Importer SHALL invoke CORE-001 Create Project.

Following successful project creation, the Importer SHALL perform source
enumeration and register the identified assets with the Core using
CORE-002 Register Asset.

Once Registration has been completed, the Core SHALL coordinate the
Acquisition Phase by issuing CORE-003 Acquire Asset requests for the
registered assets.

The Core owns the project and all persistent project state. The Importer
owns communication with the source system and translation of
source-specific information into the canonical Photo Manager data model.

A typical import operation is illustrated below.

    +----------------------+
    |        User          |
    +----------+-----------+
               |
               | Application UI
               |
    +----------v-----------+
    |         Core         |
    |----------------------|
    | Importer Discovery   |
    | Project Management   |
    | Metadata Management  |
    | Workflow             |
    | User-facing Control  |
    | Status / Recovery    |
    +----------+-----------+
               |
     Discover / Activate / Control
               |
    +----------v-----------+
    |       Importer       |
    |----------------------|
    | Initialisation       |
    | Source Interaction   |
    | Source Translation   |
    | Asset Registration   |
    | Asset Acquisition    |
    +----------+-----------+
               |
               |
    +----------v-----------+
    |    Source System     |
    +----------------------+

Examples:
    • Journi
    • Local Filesystem
    • Google Photos
    • Camera / SD Card

The import operation follows the following conceptual sequence:

    Importer Discovery
            |
            v
    Importer Selection
            |
            v
    Importer Activation / Initialisation
            |
            v
    Importer Interaction
            |
            |  Authentication / Source Selection /
            |  Source-specific Information
            v
    CORE-001 Create Project
            |
            v
    Asset Registration
            |
            v
    Registration Complete
            |
            v
    Asset Acquisition
            |
            v
    Import Operation Complete

The stages shown above describe the conceptual interaction between the
Core and an Importer. They do not define the internal state machine or
the user-facing workflow stages implemented by the Core.

The Core owns the application workflow, persistent project state and
application-level user-facing control.

The Importer owns communication with the source system, including any
source-specific user interaction required to complete the import.

The interfaces defined by this specification are implementation
independent and may be implemented using direct function calls or any
equivalent inter-process communication mechanism.

The detailed implementation of Importer discovery, activation,
initialisation and source interaction is outside the scope of this
specification and is defined by the Importer SDK and Developers
Handbook.

---

---

# 4. Terminology

Terminology used throughout this document is defined by
SPECIFICATION_STYLE_GUIDE.md.

The following terms have specific meanings within this specification.

**Import Operation** – A single execution of the Photo Manager import
workflow involving an active Importer and a selected source, from
Importer activation through successful completion, cancellation or
termination.

**Project Context** – An opaque value returned by CORE-001 Create Project
that identifies a project during subsequent interactions with the Core.
The internal representation of a Project Context is implementation
dependent.

**Importer Discovery** – The process by which the Core identifies
available Importers and determines whether they satisfy the structural
and compatibility requirements for use by the Core. Discovery does not
activate an Importer or establish a connection to its source system.

**Importer Capability Information** – Static information declared by an
Importer that describes its identity, purpose, requirements and
supported capabilities. Capability Information is available to the Core
without activating the Importer or connecting to its source system.

**Importer Activation** – The process by which the Core activates an
Importer that has been selected for an import operation. Activation
makes the Importer available to perform its source-specific
initialisation and interaction.

**Importer Interaction** – The period during which an active Importer
communicates with its source system and obtains the information required
to prepare and perform an import operation. This MAY include
authentication, source or workspace selection, source-specific user
interaction, source enumeration and acquisition of source asset data.

**Initial Metadata Policies** – The initial project-level metadata
propagation policies supplied by the Importer during project creation.
These policies are derived from the characteristics of the selected
source and establish the initial configuration for metadata propagation
within the project. Initial Metadata Policies are stored as part of the
project and MAY subsequently be modified by the user.

**Registration Phase** – The phase during which the Importer enumerates
the assets in the selected source and registers their canonical Asset
Information with the Core.

**Acquisition Phase** – The phase during which the Importer obtains the
binary data associated with registered assets and transfers that data to
the Core.

**Registration Checkpoint** – The position in the source enumeration
immediately following the last asset successfully registered by the
Importer. A Registration Checkpoint is used by the Core to request
resumption of an interrupted Registration Phase.

**Acquisition Retry** – A Core-directed attempt to acquire a specific
asset that was not successfully acquired during an earlier acquisition
attempt. Retry count and retry policy are owned by the Core.

**Source Order** – The order in which an Importer enumerates assets from
its source. For the purposes of RESUME processing, the Importer SHALL
maintain a stable Source Order between interrupted and resumed
operations.

**Source System** – The external system, service, device or filesystem
from which an Importer obtains source information and asset data.
---
---

# 5. Design Principles

The Core–Importer API has been designed according to the following
principles.

- The Core owns the project.
- The Core owns all persistent project state.
- Importers communicate with a specific source system.
- Importers translate source-specific information into the canonical
  Photo Manager data model.
- Importers acquire source assets; the Core owns persistent project
  storage.
- Importers SHALL NOT directly modify `project.json`.
- The Core validates all persistent project data.
- Source-specific behaviour SHALL remain within the Importer.
- The Core SHALL provide a stable interface for future Importers.
- Importers SHALL provide a stable interface for communication with the
  Core.
- Importer Discovery SHALL be separate from Importer Activation.
- Importer Discovery SHALL NOT establish connections to source systems
  or perform source-specific authentication.
- Importer Capability Information SHALL describe the declared
  capabilities and requirements of an Importer without requiring the
  Importer to be activated.
- An Importer SHALL be activated only when selected for an import
  operation.
- Initial Metadata Policies SHALL be supplied by the Importer as part of
  project creation and MAY subsequently be modified by the user.
- The Core SHALL own project recovery state, including registration and
  acquisition status and acquisition retry information.
- Importers SHALL NOT maintain persistent project-specific recovery
  state.
- Registration and Acquisition SHALL be treated as separate phases.
- RESUME SHALL continue processing from the position specified by the
  Core.
- Acquisition retry SHALL identify a specific asset and SHALL be
  implemented by a new ACQUIRE_ASSET operation issued by the Core.

The Core–Importer API has been designed to support future extension
through additional service definitions.

Future versions MAY introduce additional Core services, Importer
services, Metadata Provider services and other extension interfaces
without affecting the services defined by this specification.

=====================================================
# PART I – Core API
=====================================================


# 6. Core Responsibilities

The Photo Manager Core is responsible for managing the application
workflow and all persistent project state associated with an import
operation.

The Core SHALL:

- Discover available Importers.
- Validate Importer compatibility with the Core API.
- Obtain and expose Importer Capability Information.
- Activate an Importer selected by the user.
- Manage the application workflow associated with an import operation.
- Provide the services defined by the Core API.
- Create and manage Photo Manager projects.
- Own all persistent project state.
- Validate project data before it is committed to persistent storage.
- Assign and manage Core-owned project state and identifiers.
- Receive and validate Asset Information supplied by an Importer.
- Establish Core-owned information associated with registered assets,
  including storage and acquisition state.
- Manage the Registration Phase and its persistent status.
- Manage the Acquisition Phase and its persistent status.
- Maintain registration recovery information.
- Maintain acquisition retry counts and retry policy.
- Determine when an import operation may be resumed.
- Determine when an individual asset may be retried.
- Provide the information required by an Importer to resume an interrupted
  Registration Phase.
- Provide the information required by an Importer to retry an individual
  asset during the Acquisition Phase.
- Persist project state independently of the lifetime of an Importer.
- Re-establish the state of an incomplete import when an existing project
  is subsequently selected.
- Ensure that incomplete projects remain valid and discoverable.
- Manage communication with the active Importer.
- Present Importer status, warnings, errors and required user actions to
  the user.
- Issue control commands to the active Importer.
- Ensure that source-specific behaviour remains within the Importer.
- Own the canonical Photo Manager project model.
- Apply Initial Metadata Policies supplied during project creation.
- Allow Initial Metadata Policies to be subsequently modified through the
  normal project editing workflow.
- Maintain the separation between importer-owned, Core-owned and
  user-owned project information.
- Persist the project without requiring the Importer to modify
  `project.json` directly.

The Core SHALL NOT:

- Communicate directly with an Importer's source system on behalf of the
  Importer.
- Perform source-specific authentication.
- Perform source-specific enumeration of assets.
- Interpret source-specific data structures.
- Implement source-specific translation logic.
- Require knowledge of the internal structure of an Importer's source
  system.
- Delegate ownership of persistent project state to an Importer.
- Rely on an Importer to retain persistent recovery information between
  import sessions.
- Permit an Importer to modify `project.json` directly.

### 6.1 Project Ownership

The Core is the authoritative owner of Photo Manager projects.

An Importer supplies source-specific information required to create and
populate a project, but does not own the project.

Once a project has been created, its persistent state SHALL remain
available independently of the Importer's runtime state.

If an import operation is interrupted after project creation, the Core
SHALL retain the project and its current persistent state.

When the project is subsequently selected, the Core SHALL determine
whether Registration or Acquisition remains incomplete and SHALL
coordinate recovery with the Importer as required.

### 6.2 Import Workflow Ownership

The Core owns the application workflow surrounding an import operation.

The Core SHALL determine the application-level state of the import
operation, including whether the Importer is:

- discovered;
- selected;
- activated;
- initialised;
- ready to perform source interaction;
- participating in Registration;
- participating in Acquisition;
- awaiting recovery;
- complete; or
- terminated.

These states describe the relationship between the Core and the active
Importer. They do not require a one-to-one correspondence with the
internal state machine or application state representation used by the
Core or Importer.

The Importer remains responsible for its internal source-specific
processing and SHALL determine how it performs source interaction,
enumeration, acquisition and other source-specific operations required
to satisfy Core requests.

The Core SHALL remain responsible for the user-facing workflow and SHALL
coordinate the Importer's participation in the Registration and
Acquisition Phases.

The Core SHALL NOT require knowledge of the Importer's internal
processing state beyond the information communicated through the defined
API.

### 6.3 Recovery Ownership

The Core owns persistent recovery information.

The Core SHALL maintain sufficient information to determine:

- whether Registration is complete;
- whether Acquisition is complete;
- the Registration Checkpoint;
- which assets require Acquisition;
- the retry count associated with an asset; and
- whether further retry attempts are permitted.

An Importer SHALL NOT be required to persist this information between
import sessions.

When resuming an interrupted Registration Phase, the Core SHALL provide
the Importer with the information required to continue from the
appropriate Registration Checkpoint.

When issuing an IMPORTER-001 operation that may require communication
with the source system, the Core SHALL provide the source information
required by the Importer to establish or restore source communication.

The source information supplied by the Core SHALL include the source
type or implementation, the stable source identifier and the
human-readable source title associated with the project.

When retrying an individual asset, the Core SHALL identify the asset to
the Importer using the source-specific asset identifier previously
supplied by that Importer.

The Core SHALL remain responsible for determining whether an interrupted
Registration Phase or unsuccessful Acquisition attempt is eligible for
recovery or retry.

### 6.4 Persistence and Project Integrity

The Core SHALL be responsible for writing persistent project state.

The Importer SHALL communicate project and asset information to the Core
through the defined API rather than modifying persistent project files
directly.

The Core SHALL validate information received from an Importer before
incorporating it into persistent project state.

The Core SHALL ensure that an incomplete import does not leave the
project in an invalid persistent state.

The Core MAY persist intermediate state during an import operation so
that processing can be resumed following interruption or failure.

### 6.5 Separation of Responsibilities

The Core and Importer responsibilities are deliberately separated.

The Core is responsible for:

- application workflow;
- project ownership;
- persistent state;
- validation;
- recovery;
- retry policy;
- user-facing status and control;
- management of registered source-specific user interfaces; and
- the canonical Photo Manager data model.

The Importer is responsible for:

- communication with the source system;
- source-specific authentication;
- source-specific selection and interaction;
- source enumeration;
- translation of source information into the canonical data model;
- asset registration information;
- acquisition of source asset data; and
- source-specific error and status information.

For source-specific user interfaces, the Importer is responsible for
creating or launching the UI and registering it with the Core when
required. The Core and Photo Manager window-management infrastructure are
responsible for the application-level lifecycle of a registered UI.

Neither component SHALL assume ownership of responsibilities assigned to
the other by this specification.

# 7. Core Services

The Core exposes a defined set of public services that form the Core API
used for communication between the Core and active Importers.

These services define the interfaces through which the Core and an
Importer exchange project information, asset registration information,
asset data, runtime information and control information during an import
operation.

The direction of an individual request or communication is defined by the
service or interface in which it occurs.

Importers SHALL use these services rather than accessing Core internal
implementation details or persistent project files directly.

The Core SHALL NOT expose internal implementation details through the
public API.

Each Core Service is assigned a permanent Service Identifier (`CORE-xxx`)
within the applicable Core API Version.

Service Identifiers SHALL remain stable for the lifetime of that Core API
Version.

The Core API defines the interface contract only. The implementation of
the services, including the mechanism used to invoke them, is outside the
scope of this specification.

The services MAY be implemented using direct function calls or any
equivalent inter-process communication mechanism.

### 7.0.1 Service Invocation and Results

Core Services that perform a synchronous operation SHALL return a
standard Result indicating success or failure.

A service failure SHALL be reported through the service Result and SHALL
NOT be represented solely through the asynchronous CORE-004
Communications interface.

The Core SHALL record sufficient diagnostic information for an
unsuccessful service invocation to allow the cause of the failure to be
determined.

An Importer SHALL NOT assume that a successful service invocation implies
successful completion of the overall import operation.

The result of each service SHALL indicate only whether that service
invocation completed successfully and, where defined by the service,
return the information required for subsequent processing.

### 7.0.2 Service Definitions

Each Core Service defined by this specification describes:

- Purpose
- Responsibilities
- Inputs
- Outputs
- Preconditions
- Postconditions
- Errors
- Processing Rules
- Notes

Where a service transfers information between an Importer and the Core,
the receiving component SHALL validate the supplied information before
incorporating it into persistent project state or using it to control
subsequent processing.

Where a service modifies persistent project state, the Core SHALL remain
the authoritative owner of that state.

An Importer SHALL NOT modify `project.json` or other persistent project
files directly.

### 7.0.3 Project Context

CORE-001 Create Project returns a Project Context identifying the newly
created project.

The Project Context is opaque to the Importer.

The internal representation of a Project Context is implementation
dependent and is outside the scope of this specification.

An Importer SHALL supply the Project Context to subsequent Core Services
that require identification of the target project.

The Core SHALL ensure that the Project Context identifies the same
project for the lifetime of the associated import operation.

The Project Context SHALL NOT be interpreted by an Importer as a
persistent project identifier.

### 7.0.4 Service Sequence

For a new import operation, the Core API interactions SHALL follow the
following sequence:

    CORE-001 Create Project
            |
            v
    CORE-002 Register Asset
            |
            v
    Registration Complete
            |
            v
    CORE-003 Acquire Asset
            |
            v
    Acquisition Complete

CORE-004 Communications MAY be used throughout the import operation to
report runtime information to the Core.

CORE-002 Register Asset SHALL NOT be invoked before successful completion
of CORE-001 Create Project.

CORE-003 Acquire Asset SHALL NOT be invoked until Registration has been
successfully completed for the project.

The Core SHALL NOT permit acquisition of any asset while the project's
Registration Phase is incomplete.

All assets that are to be acquired SHALL first be registered using
CORE-002 Register Asset.

Once Registration is complete, the Core SHALL determine the assets
requiring acquisition and SHALL coordinate their acquisition through
CORE-003 Acquire Asset.

Recovery of an interrupted import operation MAY cause the Core to invoke
CORE-002 or CORE-003 again during a later import session.

Such recovery SHALL be directed by the Core using the persistent project
state and recovery information defined elsewhere in this specification.

A resumed Registration Phase SHALL be completed before Acquisition is
started or resumed.

---

## 7.1 CORE-001 – Create Project

### Purpose

Creates a new Photo Manager project and initialises its persistent
project state.

CORE-001 transfers the project-level information gathered by the
Importer to the Core before asset registration begins.

The Core SHALL validate the supplied information, create the project
workspace, initialise `project.json` and return a valid Project Context.

CORE-001 SHALL be invoked exactly once for each new import operation.

Successful completion of CORE-001 SHALL establish the project before any
asset registration is performed.

---

### Responsibilities

#### Importer

The Importer SHALL:

- Gather the source and workspace information required to create the
  project.
- Supply all mandatory project-level information.
- Supply the Initial Metadata Policies appropriate to the selected
  source.
- Invoke CORE-001 once for the new project.
- Wait for successful completion of CORE-001 before commencing asset
  registration.

The Importer MAY perform source-specific authentication, source
selection and other source-specific interaction before invoking CORE-001.

#### Core

The Core SHALL:

- Validate the supplied project-level information.
- Validate the supplied Initial Metadata Policies.
- Create the project workspace.
- Create and initialise `project.json`.
- Store the supplied project-level information.
- Store the Initial Metadata Policies.
- Initialise the project's Registration and Acquisition status.
- Return a valid Project Context.

---

### 7.1.1 Project Information

The Importer SHALL supply the following information when invoking
CORE-001.

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `source` | String | Yes | Identifies the source type or source implementation used for the import. |
| `source_id` | String | Yes | Stable identifier for the selected source or source workspace. |
| `source_title` | String | Yes | Human-readable title identifying the selected source or source workspace. |
| `metadata_policies` | Object | Yes | Initial Metadata Policies for the project. |

The exact representation of `metadata_policies` SHALL conform to the
Metadata Policies structure defined by the Project JSON specification.

Additional source-specific information MAY be supplied through an
optional source information structure where required by the API
implementation.

The Core SHALL NOT require source-specific information that it cannot
interpret or validate as part of the canonical project model.

---

### 7.1.2 Initial Metadata Policies

The `metadata_policies` parameter contains the Initial Metadata Policies
supplied by the Importer for the selected source.

Initial Metadata Policies define the initial project-level rules for
propagating user-entered metadata to other assets.

The Importer SHALL supply Initial Metadata Policies based on information
available from the selected source and from any source-specific
interaction required with the user.

The Core SHALL validate the supplied Initial Metadata Policies and SHALL
store them as part of the newly created project.

Once stored, the Initial Metadata Policies become part of the
Core-owned persistent project state.

Initial Metadata Policies are initial project configuration only.

The user MAY subsequently modify the Metadata Policies through the
normal project editing workflow.

The Core SHALL NOT require the Importer to remain involved in subsequent
changes to Metadata Policies.

---

### 7.1.3 Project Creation Rules

The following rules apply to CORE-001 Create Project.

1. CORE-001 SHALL be invoked exactly once when creating a new
   Photo Manager project for an import operation.

2. The Importer SHALL supply all mandatory project information.

3. The Core SHALL validate all supplied project information before
   creating the project.

4. The Core SHALL validate the supplied Initial Metadata Policies before
   storing them.

5. The Core SHALL create the project workspace and initialise
   `project.json`.

6. The Core SHALL initialise the project's Registration status as
   `NOT_STARTED`.

7. The Core SHALL initialise the project's Acquisition status as
   `NOT_STARTED`.

8. Upon successful completion, the Core SHALL return a valid Project
   Context.

9. The returned Project Context SHALL identify the newly created project
   for subsequent Core Service invocations during the import operation.

10. The Importer SHALL supply the Project Context to every subsequent
    Core Service requiring identification of the target project.

11. Asset registration SHALL NOT commence until CORE-001 has completed
    successfully.

12. The Importer SHALL NOT modify `project.json` directly.

CORE-001 SHALL NOT be invoked again when an existing project is resumed
or when individual assets are subsequently acquired.

---

### 7.1.4 Project Context

The Project Context is a temporary Core-issued identifier used to
identify the project associated with an import operation.

The Project Context is opaque to the Importer.

The internal representation of the Project Context is implementation
dependent.

For a newly created project, CORE-001 Create Project SHALL return the
Project Context to the Importer.

The Importer SHALL retain the Project Context for the duration of the
import operation and SHALL supply it with subsequent Core Service
requests that require identification of the project.

When the Core resumes Registration for an existing project, the Core
SHALL provide the Project Context to the Importer as part of the
`RESUME_REGISTRATION` operation.

When the Core requests acquisition of an asset from an existing project,
the Core SHALL provide the Project Context as part of the
`ACQUIRE_ASSET` operation.

A subsequent `ACQUIRE_ASSET` operation for the same asset SHALL use the
same Project Context and SHALL be treated as a new acquisition attempt.

The Project Context is not part of the persistent Project JSON schema.

The Core SHALL remain responsible for resolving a Project Context to the
corresponding project.

---

### Notes

CORE-001 establishes the project but does not register any assets.

Following successful completion of CORE-001, the Importer SHALL commence
the Registration Phase using CORE-002 Register Asset.

The project remains a valid Photo Manager project even if subsequent
Registration or Acquisition operations are interrupted.


## 7.2 CORE-002 – Register Asset

### Purpose

Registers a single source asset with the Core.

CORE-002 transfers the canonical Asset Information for an asset from the
Importer to the Core.

The Core SHALL validate the supplied Asset Information, create the
corresponding Photo Object within the project and initialise all
Core-managed fields.

The Importer SHALL invoke CORE-002 once for each asset identified during
the Registration Phase.

Registration is driven by the Importer. The Importer is responsible for
enumerating the source and determining when all assets to be included in
the project have been identified.

Completion of the Registration Phase SHALL be communicated separately
from the registration of an individual asset.

Asset acquisition SHALL NOT commence until the Core has received
confirmation that Registration is complete.

---

### Responsibilities

#### Importer

The Importer SHALL:

- Enumerate the selected source.
- Identify each asset to be included in the project.
- Translate source-specific information into the canonical Asset
  Information model.
- Supply all mandatory Asset Information.
- Ensure each asset has a stable `asset_id`.
- Assign a valid `group_id` to each asset.
- Supply available geographic information.
- Supply any supported initial user metadata values derived from the
  source.
- Invoke CORE-002 for each asset identified during enumeration.
- Preserve stable Source Order for the purposes of Registration RESUME.
- Explicitly notify the Core when source enumeration and Registration are
  complete.

#### Core

The Core SHALL:

- Validate the supplied Asset Information.
- Verify that the supplied Project Context identifies a valid project.
- Verify that the asset has not already been registered.
- Create the corresponding Photo Object.
- Initialise all Core-managed Photo Object fields.
- Map the canonical Asset Information to the persistent Project Schema.
- Update the project's Registration status.
- Maintain the Registration Checkpoint.
- Record sufficient information to support Registration RESUME.
- Prevent Acquisition from commencing until Registration is complete.

---

### 7.2.1 Asset Information

The following Asset Information SHALL be supplied by the Importer when
registering an asset.

The parameter names defined below form the canonical interface between
the Importer and the Core.

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `project_context` | Project Context | Yes | Temporary Core-issued identifier of the project receiving the asset. |
| `asset_id` | String | Yes | Stable identifier for the asset within the source. |
| `group_id` | String | Yes | Identifier of the logical group containing the asset. The interpretation of the group is defined by the Importer. |
| `asset_time` | Timestamp | No | Best available source timestamp associated with the asset. |
| `latitude` | Float | No | Geographic latitude associated with the asset. |
| `longitude` | Float | No | Geographic longitude associated with the asset. |
| `suggested_event` | String | No | Optional initial value for the project event associated with the asset. |
| `suggested_location` | String | No | Optional initial value for the user location associated with the asset. |
| `suggested_info` | String | No | Optional initial descriptive information associated with the asset. |

The Core SHALL treat `asset_id` as the stable source identifier for the
registered asset.

The Core SHALL NOT interpret the meaning of `group_id` beyond maintaining
the association supplied by the Importer.

Optional Asset Information SHALL only be supplied when the Importer has
reliable source information to provide.

The Importer SHALL NOT invent source information solely to populate an
optional field.

---

### 7.2.2 Canonical Parameter Mapping

The Core SHALL map the canonical Asset Information supplied by the
Importer to the persistent Project Schema defined by
`PROJECT_JSON.md`.

The mapping is:

| API Parameter | `project.json` Field | Notes |
|---------------|----------------------|-------|
| `project_context` | *(Not stored)* | Temporary Core-issued project identifier. |
| `asset_id` | `guid` | Stable source identifier for the asset. |
| `group_id` | `moment_id` | Source-defined logical grouping. |
| `asset_time` | *(Not stored)* | Source or file date/time that MAY be used by the Core when determining an initial value for the project's date/year information. |
| `latitude` | `lat` | Source latitude. |
| `longitude` | `lng` | Source longitude. |
| `suggested_event` | `event` | Optional initial value for the user-owned event field. |
| `suggested_location` | `location` | Optional initial value for the user-owned location field. |
| `suggested_info` | `info` | Optional initial value for the user-owned information field. |

`asset_time` is source information supplied to assist the Core in
constructing the initial project data. It SHALL NOT be treated as a
persistent Project JSON field.

The Core MAY use `asset_time` as evidence when determining an initial
value for project date or year information, subject to the rules defined
by the Project JSON specification and the project's metadata policies.

The Core SHALL NOT assume that `asset_time` is authoritative where more
reliable source information is available.

The Core SHALL initialise Core-owned fields independently of the
Importer-supplied Asset Information.

These include, as applicable:

- `file`
- `downloaded`
- `retry_count`
- `status`
- `exif_written`
- `last_updated`
- `location_key`
- `geo_location`

The Core SHALL determine the initial values of these fields according
to the Project JSON specification and the current state of the project.

---

### 7.2.3 Asset Registration Rules

The following rules apply to CORE-002 Register Asset.

1. CORE-001 Create Project SHALL have completed successfully before
   CORE-002 is invoked.

2. Each invocation of CORE-002 SHALL register exactly one asset.

3. The `project_context` supplied by the Importer SHALL identify the
   project receiving the asset.

4. The `asset_id` SHALL identify the asset within the selected source.

5. The Importer SHALL NOT register the same source asset more than once
   during a Registration Phase.

6. The Core SHALL reject an attempt to register an asset that has already
   been successfully registered for the project.

7. The Core SHALL create a corresponding Photo Object for each
   successfully registered asset.

8. A successfully registered asset SHALL become part of the persistent
   project state before the Core reports successful completion of the
   registration request.

9. The Core SHALL update the Registration Checkpoint following each
   successful registration.

10. Registration SHALL continue until the Importer has enumerated all
    assets to be included in the project.

11. Completion of Registration SHALL be communicated using
    CORE-004 Communications.

12. The Core SHALL NOT commence Acquisition until Registration has been
    explicitly completed.

13. The Importer SHALL NOT modify `project.json` directly.

---

### 7.2.4 Registration Completion

The Importer SHALL communicate completion of the Registration Phase to the
Core using CORE-004 Communications.

Registration completion SHALL be reported using a `STATUS` message
containing the information required by the Core to identify the affected
Import Operation and Project Context.

The Registration Completion status indicates that the Importer has
completed enumeration of the selected source and has successfully
submitted all assets identified for inclusion in the project using
CORE-002 Register Asset.

Upon receiving a valid Registration Completion status, the Core SHALL:

- Verify that the Registration Phase is in a valid state.
- Verify that all preceding CORE-002 registration requests have
  completed successfully.
- Mark the project's Registration status as `COMPLETE`.
- Persist the completed Registration status.
- Determine the assets requiring Acquisition.
- Make the project eligible for the Acquisition Phase.

The Core SHALL NOT interpret successful registration of an individual
asset as completion of Registration.

Registration Completion SHALL only be accepted after all preceding
CORE-002 registration requests have completed successfully.

If the Importer encounters an error that prevents completion of source
enumeration, it SHALL NOT report Registration Completion. Instead, it
SHALL report the condition using CORE-004 Communications.

---

### 7.2.5 Registration RESUME

If Registration is interrupted before completion, the project SHALL
remain valid and its Registration status SHALL remain incomplete.

The Core SHALL retain the Registration Checkpoint.

When Registration is resumed, the Core SHALL issue a
`RESUME_REGISTRATION` operation using IMPORTER-001.

The `RESUME_REGISTRATION` operation SHALL provide the Importer with:

- the Project Context; and
- the Registration Checkpoint identifying the position from which
  Registration is to resume.

The Core SHALL also provide the source information required by the
Importer to establish or restore communication with the source system.

The Importer SHALL re-establish source communication as required and
re-enumerate the source in stable Source Order.

The Importer SHALL continue Registration from the position specified by
the Core.

The Importer SHALL return the supplied Project Context with subsequent
CORE-002 Register Asset requests.

The Importer SHALL NOT determine or modify the Registration Checkpoint.

The Importer SHALL NOT rely on persistent internal state to determine
where Registration should resume.

A successful `RESUME_REGISTRATION` operation does not itself indicate
that Registration has completed.

Registration completion SHALL be communicated separately using
CORE-004 Communications as defined in §7.2.4.

The Core SHALL remain the authoritative owner of the Registration
Checkpoint and SHALL determine whether Registration has completed.

---

### Notes

CORE-002 transfers Asset Information only.

Binary Asset Data is transferred separately during the Acquisition Phase.

The Importer owns source enumeration and Registration processing.

The Core owns persistent registration state and the Registration
Checkpoint.

Registration MUST be complete before Acquisition begins.

## 7.3 CORE-003 – Acquire Asset

### Purpose

Requests acquisition of the binary data associated with a previously
registered asset.

CORE-003 is initiated by the Core after Registration has completed.

The Core identifies the specific asset to be acquired and provides the
Project Context, source information and source asset identifier to the
Importer.

The source information SHALL identify the source system associated with
the project and SHALL provide the information required by the Importer to
establish or restore source communication.

The Importer SHALL obtain the requested asset data from the source system
and transfer that data to the Core.

CORE-003 operates on one asset at a time.

The Core SHALL NOT request acquisition of an asset that has not been
successfully registered.

---

### Responsibilities

#### Core

The Core SHALL:

- Determine which registered asset is to be acquired.
- Identify the asset using the Project Context and its registered
  `asset_id`.
- Request acquisition of one asset at a time.
- Ensure that Registration has completed before issuing acquisition
  requests.
- Record the result of each acquisition.
- Update the persistent acquisition state of the asset.
- Maintain the asset's retry count.
- Determine whether an unsuccessful acquisition should be retried.
- Determine which asset should be requested next.
- Determine when Acquisition is complete.

#### Importer

The Importer SHALL:

- Receive an acquisition request from the Core.
- Use the supplied Project Context to identify the associated import
  operation.
- Use the supplied `asset_id` to identify the corresponding source
  asset.
- Acquire the requested binary data from the source system.
- Transfer the binary Asset Data to the Core.
- Report acquisition errors using CORE-004 Communications where
  appropriate.
- Return the supplied Project Context with the Asset Data transferred to
  the Core.

The Importer SHALL NOT determine the overall acquisition sequence.

The Importer SHALL NOT maintain persistent acquisition progress or retry
state.

---

### 7.3.1 Acquisition Request

An acquisition request from the Core SHALL contain:

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `project_context` | Project Context | Yes | Temporary Core-issued identifier of the project containing the asset. |
| `source` | String | Yes | Identifies the source type or source implementation associated with the project. |
| `source_id` | String | Yes | Stable identifier for the selected source or source workspace associated with the project. |
| `source_title` | String | Yes | Human-readable title identifying the selected source or source workspace associated with the project. |
| `asset_id` | String | Yes | Identifier of the previously registered asset to be acquired. |

The Importer SHALL treat `project_context`, `source`, `source_id` and
`source_title` as values supplied by the Core.

The Project Context SHALL be treated as an opaque identifier.

The Importer SHALL NOT construct, modify or reinterpret the Project
Context.

The Importer SHALL use the supplied source information to establish or
restore communication with the source system as required.

The `asset_id` SHALL correspond to an asset previously registered using
CORE-002 Register Asset.

The Importer SHALL treat `asset_id` as the source-specific identifier
previously supplied during Asset Registration.

---

---

### 7.3.2 Asset Data

The Importer SHALL provide the following information when returning
successfully acquired Asset Data to the Core.

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `project_context` | Project Context | Yes | The Project Context supplied by the Core in the acquisition request. |
| `asset_id` | String | Yes | Identifier of the asset whose data has been acquired. |
| `asset_data` | Binary | Yes | Binary representation of the requested asset. |

The Core SHALL validate the supplied Asset Data before storing it.

The Core SHALL associate the received Asset Data with the registered
asset identified by `asset_id`.

The Core SHALL determine the persistent storage location of the asset.

---

### 7.3.3 Acquisition Rules

The following rules apply to CORE-003 Acquire Asset.

1. Registration SHALL be complete before CORE-003 is first invoked for a
   project.

2. The Core SHALL request acquisition of only one asset per request.

3. The requested `asset_id` SHALL identify an asset that has previously
   been registered successfully.

4. The Importer SHALL acquire the asset identified by the request.

5. The Importer SHALL NOT substitute a different asset for the requested
   asset.

6. The Importer SHALL return the requested Asset Data only when the
   requested asset has been successfully obtained from the source system.

7. The Core SHALL validate the received Asset Data before storing it.

8. The Core SHALL mark the corresponding asset as successfully acquired
   only after the Asset Data has been successfully validated and written
   to the project workspace.

9. The Core SHALL persist the acquisition result before requesting the
   next asset.

10. The Core SHALL determine which registered asset is requested next.

11. The Core SHALL NOT rely on the Importer to maintain acquisition
    sequence between requests.

12. The Core SHALL determine whether an unsuccessful acquisition is
    retried.

13. Retry count and retry policy SHALL be owned by the Core.

14. A failed acquisition of one asset SHALL NOT by itself require the
    acquisition of other registered assets to stop.

15. The Core MAY continue requesting other registered assets after an
    individual acquisition failure.

16. The Core SHALL determine when all registered assets have reached a
    terminal acquisition state.

17. The Core SHALL update the project's Acquisition status according to
    the results of individual asset acquisition attempts.

---

### 7.3.4 Acquisition Failure

If the Importer cannot successfully acquire the requested asset, the
`ACQUIRE_ASSET` operation SHALL return a `FAILED` Result.

The Importer MAY additionally report the failure using CORE-004
Communications when diagnostic or user-facing information is required.

The Importer SHALL NOT silently substitute another asset or mark the
requested asset as successfully acquired.

The Core SHALL retain the registered asset following an unsuccessful
acquisition attempt.

The Core SHALL update the asset's persistent acquisition and retry state
as required by its retry policy.

The Core SHALL determine whether the asset is eligible for another
acquisition attempt according to its retry policy.

A retry SHALL constitute a new `ACQUIRE_ASSET` operation for the same
`project_context` and `asset_id`.

The Importer SHALL treat each such operation as a new acquisition
attempt.

An acquisition failure SHALL NOT by itself terminate the import
operation unless the Core determines that the failure requires
termination or no further acquisition attempts are permitted.

---

### 7.3.5 Acquisition Completion

The Core SHALL determine when Acquisition is complete.

The Importer SHALL NOT indicate overall Acquisition completion through
CORE-003.

The Core SHALL determine Acquisition completion from the persistent
acquisition state of the registered assets and the Core's acquisition
workflow.

Acquisition is complete when the Core has completed acquisition
processing for every registered asset, such that each asset has either:

- been successfully acquired and stored in the project workspace; or
- been determined by the Core to require no further acquisition
  attempts.

The Core SHALL NOT consider Acquisition complete while any registered
asset remains subject to further acquisition processing.

There is therefore no `is_download_complete` parameter in CORE-003.

## 7.4 CORE-004 - Communications

### Purpose

Provides the communications interface implemented by the Core during an
import operation.

This interface enables the Importer to communicate progress,
informational messages, warnings, errors and source-specific UI
registration information to the Core.

The Core SHALL determine how received information is processed,
recorded and presented to the user.

---

### Interface Overview

CORE-004 defines the communications interface implemented by the Core.

Importers SHALL use this interface to communicate runtime information to
the Core.

The mechanism used to transport these communications is implementation
dependent.

A native implementation MAY use direct function calls, while distributed
implementations MAY use any equivalent inter-process communication
mechanism.

---

### Message Format

Every communication sent using CORE-004 SHALL contain the following
information.

| Field | Mandatory | Description |
|-------|-----------|-------------|
| `message_type` | Yes | Identifies the type of communication. |
| `message` | Yes | Human-readable text intended for presentation to the user. |
| `data` | No | Optional data associated with the message. The structure of this field is defined by the individual message type. |

### Message Types

CORE-004 supports the following message types.

| Message Type | Purpose |
|--------------|---------|
| `STATUS` | Reports normal runtime status information. No user action is required. |
| `ACTION_REQUIRED` | Indicates that the Importer cannot continue until the user performs a required action. |
| `WARNING` | Reports a recoverable condition that does not prevent the current operation from continuing. |
| `ERROR` | Reports an unrecoverable condition that prevents the Importer from continuing the current operation. |
| `UI-REGISTRATION` | Registers a source-specific user interface created or launched by the Importer for association with the current Import Operation. |

#### STATUS

Reports normal runtime status information from the Importer.

STATUS messages are intended to keep the user informed of the current
activity being performed by the Importer.

The Core MAY display the message to the user, record it in the log, or
both.

A normal STATUS message SHALL NOT alter the state of the current import
operation.

A STATUS message MAY additionally communicate a defined phase completion
condition when the `data` field contains the information specified for
that condition by this specification.

For Registration, a STATUS message indicating Registration Completion
SHALL identify the affected Project Context and SHALL indicate that the
Importer has completed source enumeration and successfully submitted all
assets identified for inclusion in the project.

The Core SHALL process a valid Registration Completion status as defined
in §7.2.4.

The Importer SHALL NOT use STATUS to indicate Acquisition Completion.
Acquisition completion SHALL be determined by the Core from persistent
acquisition state as defined in §7.3.5.

#### ACTION_REQUIRED

Indicates that the Importer cannot continue until the user performs a
required action.

Typical examples include user authentication, source selection or other
operations that require user interaction with the source system.

The Core SHALL present the message to the user using an
implementation-defined user interface.

Following transmission of an ACTION_REQUIRED message, the Importer SHALL
wait until the required action has been completed before continuing the
current operation.

The Importer SHALL NOT continue the current operation until the required
action has been completed.

#### WARNING

Reports a recoverable condition encountered by the Importer.

WARNING messages indicate that the current operation can continue, but
the user SHOULD be informed of the condition.

The Core MAY display the warning to the user, record it in the log, or
both.

Receipt of a WARNING message SHALL NOT alter the state of the current
import operation.

#### ERROR

Reports an unrecoverable condition encountered by the Importer.

Following transmission of an ERROR message, the Importer SHALL suspend
the current operation pending further instructions from the Core.

The Core SHALL determine the appropriate recovery action.

If recovery requires continuation of an interrupted Registration Phase,
the Core SHALL issue a new `RESUME_REGISTRATION` operation using
IMPORTER-001.

If recovery requires another acquisition attempt, the Core SHALL issue a
new `ACQUIRE_ASSET` operation for the affected asset.

If the operation cannot or should not continue, the Core SHALL issue a
`CANCEL` operation using IMPORTER-001.

The Importer SHALL NOT assume which recovery action the Core will select
based solely on the ERROR message.

#### UI-REGISTRATION

Registers a source-specific user interface created or launched by the
Importer during an import operation.

The purpose of UI-REGISTRATION is to associate the UI with the current
Import Operation so that the Core can ensure that the UI remains under
the control of the Photo Manager window-management infrastructure for
the duration of the operation and can be released when the operation
ends.

The Importer SHALL use UI-REGISTRATION when it creates or launches a
source-specific UI that needs to be managed as part of the import
operation.

The UI MAY be any source-specific user interface required by the
Importer, including but not limited to:

- a browser window;
- a directory or file selection interface;
- a terminal or command interface;
- a third-party application interface.

The Core SHALL treat the supplied UI handle as an opaque value.

The Core SHALL NOT interpret the UI handle or depend on the type or
implementation of the associated UI.

The Importer SHALL remain responsible for creating or launching the
source-specific UI and for determining when and why the UI is required.

Once registered using UI-REGISTRATION, the application-level lifecycle
of the UI SHALL be managed by the Photo Manager window-management
infrastructure.

The Importer SHALL NOT communicate directly with the Window Manager.
Source-specific UI management SHALL be coordinated through the Core.

The `data` field of a UI-REGISTRATION message SHALL contain the
following information.

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `ui_handle` | Opaque | Yes | Handle identifying the UI to be associated with the current Import Operation. The value is implementation-defined and SHALL be treated as opaque by the Core. |

The Core SHALL associate the registered UI with the current Import
Operation.

A registered UI SHALL remain associated with the Import Operation until
the operation ends, unless the UI is otherwise terminated by the
implementation.

The Core SHALL retain sufficient information to allow the associated UI
to be managed and released when the Import Operation ends.

The detailed interface between the Core and the Window Manager is outside
the scope of CORE-004.

---

### Notes

CORE-004 MAY be invoked at any time during an import operation,
including before invocation of CORE-001 Create Project.

CORE-004 does not require a Project Context as a top-level message
field.

Individual CORE-004 message types MAY require a Project Context within
their `data` field when the communication relates to a specific project
or import operation.

A UI-REGISTRATION message is associated with the current Import
Operation, not with the Project Context.

Importers SHALL NOT assume how the Core displays or records received
messages.

The Core MAY present messages using any implementation-defined user
interface.

The UI handle supplied by UI-REGISTRATION is opaque to the Core.

=====================================================
PART II – Importer API
=====================================================

# 8. Importer Responsibilities

An Importer is responsible for communicating with its source system and
translating source-specific information into the canonical Photo Manager
data model.

The Importer SHALL operate through the interfaces defined by the
Core–Importer API and SHALL NOT access or modify Core persistent project
state directly.

The Importer SHALL:

- Provide the interfaces required for Importer Discovery.
- Provide static Capability Information describing the Importer.
- Initialise its source-specific runtime environment when activated.
- Establish communication with the source system as required.
- Perform source-specific authentication as required.
- Present source-specific user interaction where required.
- Identify and select the source workspace or content to be imported.
- Determine the project-level information required by the Core.
- Determine the Initial Metadata Policies appropriate to the selected
  source.
- Invoke CORE-001 Create Project when sufficient project information has
  been obtained.
- Enumerate assets in the selected source.
- Translate source-specific asset information into the canonical Asset
  Information model.
- Register assets with the Core using CORE-002 Register Asset.
- Maintain stable Source Order for Registration.
- Report Registration completion using CORE-004 Communications.
- Respond to Core-directed Registration RESUME operations.
- Respond to Core-directed asset acquisition requests.
- Acquire requested asset data from the source system.
- Transfer acquired Asset Data to the Core using the defined acquisition
  interface.
- Report runtime status, warnings, errors and user-action requirements
  using CORE-004 Communications.
- Release source-specific resources owned by the Importer when the
  import operation ends.

The Importer SHALL NOT:

- Modify `project.json` directly.
- Modify other persistent Core project files directly.
- Create or assign persistent Photo Manager project identifiers.
- Maintain persistent project recovery state.
- Determine the Core's acquisition sequence.
- Determine the Core's retry policy.
- Mark an asset as successfully acquired without successfully
  transferring its Asset Data to the Core.
- Determine overall Acquisition completion.
- Assume ownership of Core-managed project state.

### 8.1 Importer Ownership

The Importer owns communication with the external source system.

This includes all source-specific behaviour required to obtain source
information and asset data.

The Core SHALL NOT require knowledge of the internal structure or
protocol of the source system.

The Importer MAY maintain source-specific configuration, authentication
information and runtime state required to communicate with the source.

Such information remains the responsibility of the Importer and SHALL NOT
become part of the canonical Photo Manager project model unless
explicitly supplied through the defined Core API.

### 8.2 Source Interaction

The Importer SHALL perform all source-specific interaction required to
prepare and perform an import.

This MAY include:

- authentication;
- source or workspace selection;
- source-specific configuration;
- source enumeration;
- source-specific metadata extraction;
- acquisition of source asset data; and
- source-specific error handling.

The Importer MAY present source-specific user interaction where required.

The Core SHALL remain responsible for the overall application workflow
and SHALL determine how Importer status and user-action requirements are
presented within the application.

### 8.3 Project Creation

The Importer SHALL gather the information required to create a new
Photo Manager project.

This includes:

- source information;
- source identifier;
- source title; and
- Initial Metadata Policies.

Once sufficient information has been obtained, the Importer SHALL invoke
CORE-001 Create Project.

The Importer SHALL NOT commence asset registration until CORE-001 has
completed successfully and the Core has returned a Project Context.

The Importer SHALL retain the Project Context and SHALL supply it with
subsequent Core Service requests associated with the project.

### 8.4 Registration

The Importer SHALL drive the Registration Phase.

During Registration, the Importer SHALL:

- Enumerate the selected source.
- Identify each asset to be included in the project.
- Determine the stable source `asset_id`.
- Determine the appropriate `group_id`.
- Extract available source metadata.
- Construct the canonical Asset Information.
- Invoke CORE-002 Register Asset for each asset.

The Importer SHALL maintain stable Source Order for the purposes of
Registration RESUME.

The Importer SHALL continue Registration until the source has been fully
enumerated and all assets to be included in the project have been
successfully submitted to the Core.

The Importer SHALL then communicate Registration completion using
CORE-004 Communications.

The Importer SHALL NOT commence Acquisition merely because Registration
has completed locally.

Acquisition SHALL commence only when requested by the Core.

### 8.5 Acquisition

The Core SHALL control the Acquisition Phase.

The Importer SHALL respond to individual acquisition requests issued by
the Core.

For each acquisition request, the Importer SHALL:

- Identify the requested source asset.
- Acquire the corresponding binary Asset Data from the source.
- Return the Asset Data to the Core using the defined acquisition
  interface.
- Report any acquisition failure using CORE-004 Communications where
  appropriate.

The Importer SHALL process only the asset requested by the Core.

The Importer SHALL NOT determine which registered asset is requested
next.

The Importer SHALL NOT maintain persistent acquisition progress.

The Importer SHALL NOT determine when Acquisition is complete.

### 8.6 Recovery

The Importer SHALL support recovery operations initiated by the Core.

For Registration recovery, the Importer SHALL:

- Receive the Project Context supplied by the Core.
- Receive the Registration resume position supplied by the Core.
- Receive the source information supplied by the Core that is required
  to establish or restore source communication.
- Re-establish source communication as required.
- Re-enumerate the source in stable Source Order.
- Continue Registration from the position specified by the Core.
- Return the Project Context with subsequent CORE-002 requests.

For Acquisition recovery, the Importer SHALL:

- Receive the Project Context supplied by the Core.
- Receive the acquisition request identifying the asset to be acquired.
- Receive the source information supplied by the Core that is required
  to establish or restore source communication.
- Re-establish source communication as required.
- Acquire the requested asset from the source.
- Return the Project Context with the resulting Asset Data.

The source information supplied by the Core SHALL include:

- `source`;
- `source_id`; and
- `source_title`.

The Importer SHALL treat the Project Context and source information
supplied by the Core as authoritative for the operation.

The Importer SHALL NOT rely on persistent internal state to determine
where a Registration or Acquisition operation should resume.

The Core is the authoritative owner of persistent recovery information.

### 8.7 Runtime Communication

The Importer SHALL use CORE-004 Communications to report runtime
conditions to the Core.

This includes:

- normal status;
- progress information;
- user actions required;
- warnings;
- errors;
- Registration completion; and
- source-specific user interface registration.

When the Importer creates or launches a source-specific user interface
that requires management as part of the import operation, the Importer
SHALL register that user interface with the Core using the
`UI-REGISTRATION` message defined by CORE-004.

The Importer SHALL provide sufficient information for the Core to
identify the affected operation and, where applicable, the affected
asset.

The Importer SHALL NOT use runtime messages as a substitute for the
defined Core Services.

### 8.8 Resource Management

The Importer SHALL manage all source-specific runtime resources that it
creates or acquires during an import operation, except for user
interfaces that have been registered with the Core using
`UI-REGISTRATION`.

Source-specific runtime resources include, as applicable:

- network connections;
- authenticated sessions;
- temporary files;
- source-specific processes;
- source-specific caches; and
- other resources required to communicate with or obtain data from the
  source system.

The Importer SHALL release source-specific resources when they are no
longer required and SHALL release any remaining Importer-owned resources
when the import operation ends, including following cancellation or
failure.

When the Importer creates or launches a source-specific user interface
that is required to remain associated with the import operation, the
Importer SHALL register that interface with the Core using
`UI-REGISTRATION`.

Once a source-specific user interface has been successfully registered
using `UI-REGISTRATION`, its lifecycle SHALL be managed through the Core
and the Photo Manager window-management infrastructure as defined by
CORE-004.

The Importer SHALL NOT directly communicate with or control the Window
Manager.

The Importer SHALL remain responsible for any source-specific resources
used by the UI that are not part of the registered UI lifecycle.

Resource cleanup SHALL NOT require the Importer to modify persistent
project state directly.

# 9. Importer Discovery and Capability Information

The Core SHALL be able to discover available Importers without activating
them or establishing a connection to their source systems.

An Importer SHALL provide static Capability Information that can be
obtained during discovery.

Capability Information allows the Core to identify the Importer, determine
its compatibility with the Core API and present information about the
Importer to the user.

Capability Information SHALL describe the Importer's declared
characteristics only. It SHALL NOT represent the current runtime state of
the Importer or its source system.

### 9.1 Discovery Requirements

Importer discovery SHALL:

- identify available Importer implementations;
- validate the Importer's declared identity;
- determine the Core API Version supported by the Importer;
- obtain the Importer's Capability Information;
- determine whether the Importer satisfies the structural requirements
  for activation; and
- report invalid or incompatible Importers to the Core diagnostics
  mechanism.

Discovery SHALL NOT:

- activate the Importer;
- authenticate with the source system;
- establish a source-system connection;
- enumerate source content;
- select a source workspace;
- acquire asset data; or
- modify a Photo Manager project.

An Importer that is discovered successfully is not thereby proven to be
operational against its source system.

### 9.2 Capability Information

An Importer SHALL provide static Capability Information containing:

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `identifier` | String | Yes | Stable unique identifier for the Importer. |
| `name` | String | Yes | Human-readable Importer name. |
| `description` | String | Yes | Human-readable description of the Importer's purpose. |
| `api_version` | String | Yes | Core API Version supported by the Importer. |
| `requirements` | Object | No | Requirements that must be satisfied for the Importer to operate. |
| `capabilities` | Object | Yes | Declared capabilities supported by the Importer. |

The exact structure of `requirements` and `capabilities` SHALL be defined
by the applicable Core API Version.

Capability Information SHALL be available without requiring source-system
authentication or source-system access.

### 9.3 Capability Information and Runtime State

Capability Information describes what an Importer supports.

It SHALL NOT be used to report transient runtime conditions such as:

- whether the user is currently authenticated;
- whether a source system is currently available;
- which source workspace has been selected;
- whether a source connection is currently active; or
- whether an import operation is currently in progress.

Such information SHALL be obtained during Importer activation and
interaction.

The Core MAY use Capability Information to determine whether an Importer
is suitable for presentation or selection, but SHALL NOT assume that
declared capabilities guarantee successful operation against a particular
source system.

### 9.4 Capability Query

The Importer SHALL provide a capability query that can be invoked by the
Core during discovery.

The capability query SHALL return the Importer's static Capability
Information without activating the Importer.

The capability query SHALL NOT perform source-specific authentication,
source enumeration or asset acquisition.

The Core MAY invoke the capability query repeatedly during discovery.

The returned Capability Information SHALL be deterministic for a given
Importer implementation and Core API Version, except where explicitly
defined otherwise by a future specification.

### Notes

Discovery and Capability Information are concerned with identifying and
describing an Importer before it is activated.

Activation, source connection, authentication, source selection and
runtime interaction are outside the discovery operation and are defined
by the Importer workflow.

---

## 10.1 IMPORTER-001 – Control

### Purpose

Provides the control interface through which the Core directs an active
Importer during an import operation.

IMPORTER-001 supports Registration recovery, individual asset
acquisition and termination of the import operation.

The Core SHALL invoke IMPORTER-001 only for an Importer that has been
successfully activated and initialised.

---

### 10.1.1 Control Operations

IMPORTER-001 supports the following operations:

| Operation | Purpose |
|-----------|---------|
| `RESUME_REGISTRATION` | Instructs the Importer to resume Registration from the position specified by the Core. |
| `ACQUIRE_ASSET` | Requests the Importer to acquire one specific registered asset and return its Asset Data. |
| `CANCEL` | Instructs the Importer to terminate the current import operation. |

A future Core API Version MAY define additional control operations.

---

### 10.1.2 Project Context

Every IMPORTER-001 operation SHALL identify the project using the
Project Context.

The Project Context SHALL be supplied by the Core.

The Importer SHALL treat the Project Context as an opaque value.

The Importer SHALL NOT construct, modify or reinterpret the Project
Context.

The Project Context identifies the Photo Manager project associated with
the operation but does not necessarily provide sufficient information
for the Importer to establish or restore communication with the source
system.

---

### 10.1.3 Source Connection

An Importer MAY retain an active connection to its source system while
an import operation is in progress.

The Importer SHALL NOT assume that such a connection remains available
after an application restart, Importer reactivation, source connection
failure or other interruption.

For every IMPORTER-001 operation that requires source communication, the
Core SHALL supply the source information required to establish or
restore that communication.

The source information SHALL include:

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `source` | String | Yes | Identifies the source type or source implementation. |
| `source_id` | String | Yes | Stable identifier for the selected source or source workspace. |
| `source_title` | String | Yes | Human-readable title identifying the selected source or source workspace. |

The Importer SHALL use the supplied source information to establish or
restore communication with the source system.

The Importer MAY perform source-specific authentication or other
source-specific interaction required to establish the connection.

The Core SHALL NOT be required to interpret the meaning of
`source_id`.

The Importer SHALL NOT modify the Project Context or supplied source
information when establishing the source connection.

If the Importer cannot establish the required source connection, it
SHALL return a `FAILED` Result and SHALL report any relevant runtime
condition using CORE-004 Communications where appropriate.

`CANCEL` does not require source information because it does not require
source communication in order to terminate the current import operation.

---

### 10.1.4 RESUME_REGISTRATION

The Core SHALL use `RESUME_REGISTRATION` when Registration of an existing
project has been interrupted before completion.

The request SHALL contain:

- `project_context`;
- the Registration Checkpoint from which Registration is to resume;
- `source`;
- `source_id`; and
- `source_title`.

The supplied source information SHALL be the information retained by the
Core for the selected source.

The Importer SHALL use the supplied source information to establish or
restore source communication as required.

After source communication has been established, the Importer SHALL:

- re-enumerate the source;
- maintain the defined stable Source Order;
- continue Registration from the position specified by the Core; and
- return the supplied Project Context with subsequent CORE-002 requests.

The Importer SHALL NOT rely on persistent internal state to determine the
Registration Checkpoint.

The Core SHALL remain the authoritative owner of the Registration
Checkpoint.

A successful `RESUME_REGISTRATION` request does not itself indicate that
Registration has completed.

The Importer SHALL communicate Registration completion using CORE-004
Communications after all remaining assets have been successfully
registered.

---

### 10.1.5 ACQUIRE_ASSET

The Core SHALL use `ACQUIRE_ASSET` to request the binary data for one
specific registered asset.

The request SHALL contain:

- `project_context`;
- `source`;
- `source_id`;
- `source_title`; and
- `asset_id`.

The supplied source information SHALL be the information retained by the
Core for the selected source.

The Importer SHALL use the supplied source information to establish or
restore source communication as required.

After source communication has been established, the Importer SHALL:

1. Identify the source asset corresponding to `asset_id`.
2. Acquire the binary Asset Data from the source.
3. Return the Asset Data as the result of the `ACQUIRE_ASSET` operation.

The Importer SHALL NOT acquire a different asset from the one requested.

The Importer SHALL NOT determine which asset is requested next.

The Core SHALL determine the order of acquisition requests.

A successful `ACQUIRE_ASSET` operation SHALL return:

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `project_context` | Project Context | Yes | The Project Context supplied by the Core in the request. |
| `asset_id` | String | Yes | Identifier of the asset whose data has been acquired. |
| `asset_data` | Binary | Yes | Binary representation of the requested asset. |

The returned `project_context` SHALL match the Project Context supplied in
the request.

The returned `asset_id` SHALL match the `asset_id` supplied in the
request.

The Core SHALL validate the returned Asset Data before storing it.

The Core SHALL determine the persistent storage location of the asset
and SHALL update the persistent acquisition state of the asset following
successful storage.

A subsequent `ACQUIRE_ASSET` request for the same `asset_id` SHALL be
treated as a new acquisition attempt.

The Core MAY therefore use `ACQUIRE_ASSET` to retry a previously failed
acquisition.

No separate `RETRY` operation is required.

---

### 10.1.6 CANCEL

The Core MAY issue `CANCEL` when the current import operation is to be
terminated.

The Importer SHALL:

- stop source-specific processing as soon as reasonably possible;
- release source-specific resources;
- leave persistent project state under the control of the Core; and
- report any relevant termination condition using CORE-004 where
  appropriate.

`CANCEL` SHALL NOT require the Importer to modify `project.json`.

The Core SHALL remain responsible for determining the resulting
persistent project state.

---

### 10.1.7 Control Operation Results

Each IMPORTER-001 operation SHALL return a Result indicating the outcome
of the requested control operation.

The Result SHALL indicate one of the following states:

| Result | Meaning |
|--------|---------|
| `COMPLETED` | The requested control operation completed successfully. |
| `FAILED` | The requested control operation could not be completed. |

For `RESUME_REGISTRATION`, a `COMPLETED` Result indicates that the
requested Registration resume operation has been accepted and completed
its control processing. It does not by itself indicate that Registration
has completed.

Registration completion is established only when the Importer
subsequently reports Registration Completion using CORE-004.

For `ACQUIRE_ASSET`, a `COMPLETED` Result indicates that the requested
Asset Data has been successfully acquired and returned to the Core.

For `CANCEL`, a `COMPLETED` Result indicates that the Importer has
completed the requested termination processing.

A `FAILED` Result SHALL provide sufficient information for the Core to
determine the appropriate workflow response.

If a `FAILED` Result is caused by an inability to establish or restore
source communication, the Importer SHALL report any relevant runtime
condition using CORE-004 Communications where appropriate.

The Core SHALL determine the appropriate recovery action following a
failed control operation.

The Importer SHALL NOT assume that a failed operation will be retried.

---

### 10.1.8 Control and Persistent State

The Importer SHALL NOT maintain persistent project recovery state.

The Core SHALL remain the authoritative owner of:

- Registration status;
- Registration Checkpoint;
- Acquisition status;
- asset acquisition state;
- retry counts; and
- retry policy.

The Importer SHALL use the information supplied by the Core for each
operation.

An Importer MAY maintain temporary runtime state required to communicate
with the source system while an operation is active.

The Importer SHALL NOT rely on such temporary runtime state being
available after the import operation has been interrupted or terminated.

The source information supplied by the Core MAY be used by the Importer
to restore source communication after such an interruption.

The Core SHALL remain responsible for retaining the source information
required to restore communication with the selected source.
