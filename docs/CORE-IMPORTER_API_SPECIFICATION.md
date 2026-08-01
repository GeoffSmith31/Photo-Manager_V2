# Photo Manager V2
# Core-Importer API Specification

Document Status: Draft
Document Version: 1.0

Defines:
    Core API Version 1

Normative References:

PROJECT_JSON.md               Version 2
SPECIFICATION_STYLE_GUIDE.md  Version 1.0

---

# 1. Purpose

This document defines the application programming interfaces (APIs)
used for communication between the Photo Manager Core and Importer
components.

It specifies the services provided by the Core, the services provided by
an Importer and the behavioural requirements governing their
interaction.

This specification defines the interface contract only. It does not
specify implementation details, user interface behaviour or internal
component design.

---

# 2. Scope

This specification applies to all Importers developed for the Photo
Manager system, regardless of the source from which assets are imported.

It defines:

- The Core API implemented by the Photo Manager Core.
- The Importer API implemented by Importers.
- The communication protocol between these components.

This specification does not define:

- The internal implementation of the Core.
- The internal implementation of Importers.
- User interface design.
- The Project JSON schema.

---

# 3. Architecture Overview

The Photo Manager import system is composed of two primary components:

- **The Core**, which manages projects, assets, metadata, workflow and
  user interaction.
- **An Importer**, which communicates with a specific source system and
  translates source-specific information into the canonical Photo
  Manager data model.

The Core and Importer communicate through well-defined application
programming interfaces (APIs).

The Core provides services used by the Importer to create and populate a
project.

The Importer provides services that allow the Core to control import
operations when required.

This specification defines the interface contracts between these
components. It does not specify the internal implementation of either
component.

A typical import operation is illustrated below.

```text
                    +----------------------+
                    |        User          |
                    +----------+-----------+
                               |
                               | User Interface
                               |
                    +----------v-----------+
                    |         Core         |
                    |----------------------|
                    | Project Management   |
                    | Metadata Management  |
                    | Workflow             |
                    | User Interface       |
                    +----------+-----------+
                               ^
          Core API             |             Importer API
       (CORE-001 ... 004)      |      (IMPORTER-001 ...)
                               |
                    +----------+-----------+
                    |       Importer       |
                    |----------------------|
                    | Source Translation   |
                    | Source-specific UI   |
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
```

The Core owns the application workflow and user experience.

The Importer owns communication with the source system, including any
temporary source-specific user interfaces required to complete the
import.

The interfaces defined by this specification are implementation
independent and may be implemented using direct function calls or any
equivalent inter-process communication mechanism.

---

# 4. Terminology

Terminology used throughout this document is defined by
SPECIFICATION_STYLE_GUIDE.md.

Project Context – An opaque value returned by CORE-001 Create Project that identifies a project during subsequent interactions with the Core. The internal representation of a Project Context is implementation dependent.

---

# 5. Design Principles

The Core–Importer API has been designed according to the following
principles.

- The Core owns the project.
- Importers describe the source.
- Importers translate source-specific information into the canonical
  Photo Manager data model.
- The Core owns all persistent project data.
- Metadata Providers suggest metadata.
- Users own editable metadata.
- The Core validates all persistent data.
- Importers SHALL NOT directly modify `project.json`.
- The Core SHALL provide a stable interface for future Importers.
- Importers SHALL provide a stable interface for communication with the
  Core.

The Core–Importer API has been designed to support future extension
through additional service definitions.

Future versions MAY introduce additional Core services, Importer
services, Metadata Provider services and other extension interfaces
without affecting the services defined by this specification.

=====================================================
# PART I – Core API
=====================================================


# 6. Core Responsibilities

The Core is responsible for:

- Creating and managing projects.
- Managing project workspaces.
- Maintaining `project.json`.
- Validating all persistent project data.
- Storing downloaded assets.
- Managing project workflow.
- Applying Metadata Policies.
- Invoking Metadata Providers.
- Writing editable metadata to assets.
- Providing services to Importers.
- Communicating with Importers through the interfaces defined by this
  specification.

The Core SHALL be the sole owner of all persistent project state.

# 7. Core Services

The Core exposes a minimal set of public services for use by Importers.

These services define the complete public interface implemented by the
Core.

Importers SHALL use these services to create projects, register assets,
transfer asset and communicate runtime information to the Core.

The Core SHALL NOT expose internal implementation details through the
public API.

Each Core Service is assigned a permanent Service Identifier (`CORE-xxx`)
within the applicable Core API Version. Service Identifiers SHALL remain
stable for the lifetime of that Core API Version.

All synchronous Core API services SHALL return a standard Result indicating success or failure. Failure to complete a service SHALL be reported by the service's return value and not by the asynchronous reporting protocol.

The Core SHALL record sufficient diagnostic information for every unsuccessful service invocation to allow the cause of the failure to be determined.

Each Core Service defines:

- Purpose
- Inputs
- Outputs
- Preconditions
- Postconditions
- Errors
- Notes

The implementation of each service is outside the scope of this
specification.

## 7.1 CORE-001 – Create Project

### Purpose

Creates a new Photo Manager project and initialises the project
workspace.

This service transfers Workspace Information from the Importer to the
Core prior to importing any assets.

The Core SHALL validate the supplied Workspace Information, create the
project workspace and initialise `project.json`.

This service SHALL be invoked exactly once before the first invocation
of CORE-002 Register Asset.

---

### Responsibilities

#### Importer

- Gather Workspace Information.
- Supply all mandatory Workspace Information.
- Supply suggested Metadata Policies.
- Invoke this service once per project.

#### Core

- Validate the supplied Workspace Information.
- Validate the supplied Metadata Policies.
- Create the project workspace.
- Create and initialise `project.json`.
- Store the Metadata Policies.
- Return a valid Project Context.

---

### 7.1.1 Workspace Information

Workspace Information contains the canonical information required by the
Core to create a new Photo Manager project.

The Importer SHALL supply all mandatory Workspace Information when
invoking CORE-001 Create Project.

The parameter names defined below form the canonical interface between
the Importer and the Core.

The Core is responsible for mapping the supplied Workspace Information
to the persistent Project Schema defined by `PROJECT_JSON.md`.

| Parameter | Type | Mandatory | Description |
|-----------|------|-----------|-------------|
| `source_type` | String | Yes | Identifies the source implementation (e.g. Journi, Filesystem, Google Photos). |
| `source_id` | String | Yes | Unique identifier of the selected source. |
| `source_name` | String | Yes | Human-readable name supplied by the source. |
| `metadata_policies` | Object | Yes | Suggested initial Metadata Policies for the project. |
| `source_information` | Object | No | Optional source-specific workspace information. |

---

### 7.1.2 Canonical Parameter Mapping

The Core SHALL map the canonical Workspace Information supplied by the
Importer to the persistent Project Schema defined by
`PROJECT_JSON.md`.

The following table illustrates the mapping used by Core API Version 1.

| API Parameter | `project.json` Field | Notes |
|---------------|----------------------|-------|
| `source_type` | `workspace.source_type` | Source implementation identifier. |
| `source_id` | `workspace.source_id` | Persistent source identifier. |
| `source_name` | *(Not stored directly)* | Used by the Core as the default suggested Workspace name. The user MAY modify this value before project creation. |
| `metadata_policies` | `workspace.metadata_policies` | Initial metadata policy configuration after Core validation. |
| `source_information` | *(Implementation-defined)* | Optional source-specific workspace information. |

---

### 7.1.3 Workspace Creation Rules

The following rules apply to all invocations of
CORE-001 Create Project.

1. CORE-001 SHALL be invoked exactly once for each import operation.

2. The Importer SHALL supply all mandatory Workspace Information.

3. The Core SHALL validate all supplied Workspace Information before
   creating the project.

4. The Core SHALL validate the supplied Metadata Policies before storing
   them.

5. The Core SHALL derive an initial Workspace name from the supplied
   `source_name`.

6. The user MAY modify the proposed Workspace name prior to project
   creation.

7. The Core SHALL create the project workspace and initialise
   `project.json`.

8. Upon successful completion the Core SHALL return a valid Project
   Context.

9. The returned Project Context SHALL uniquely identify the project for
   all subsequent Core Service invocations.

10. The Importer SHALL supply the returned Project Context to every Core
    Service requiring identification of the target project.

11. The Importer SHALL NOT modify `project.json` directly.

---

### Notes

The Project Context uniquely identifies the project throughout the
lifetime of the import operation.

The representation of the Project Context is implementation dependent
and is outside the scope of this specification.

Individual assets SHALL subsequently be registered using
CORE-002 Register Asset.

## 7.2 CORE-002 – Register Asset

### Purpose

Registers a single asset with the Core.

This service transfers the canonical Asset Information from the Importer
to the Core prior to acquisition of the asset data.

The Core SHALL validate the supplied Asset Information, create the
corresponding Photo Object within `project.json` and initialise all
Core-managed fields.

This service SHALL be invoked once for every asset to be imported into
the project.

The final invocation SHALL indicate completion of the Registration phase
using the `is_registration_complete` parameter.

---

### Responsibilities

#### Importer

- Translate source-specific information into the canonical Asset
  Information model.
- Supply all mandatory Asset Information.
- Ensure each asset has a unique `asset_id`.
- Assign a valid `group_id` to every asset.
- Supply the most authoritative available `asset_time` for each
  asset.
- Correctly identify completion of the Registration phase using
  `is_registration_complete`.

#### Core

- Validate the supplied Asset Information.
- Create the corresponding Photo Object.
- Initialise all Core-managed Photo Object fields.
- Map the canonical Asset Information to the persistent Project Schema.
- Update the Workspace registration status.
- Detect completion of the Registration phase.

---

### 7.2.1 Asset Information

The following Asset Information SHALL be supplied by the Importer when
registering an asset.

The parameter names defined below form the canonical interface between
the Importer and the Core.

The Core is responsible for mapping the supplied Asset Information to
the persistent Project Schema defined by `PROJECT_JSON.md`.

| Field | Type | Mandatory | Description |
|-----------|------|-----------|-------------|
| `asset_id` | String | Yes | Unique identifier for the asset within the source. The value SHALL remain stable for the lifetime of the source. |
| `group_id` | String | Yes | Identifier of the logical group containing the asset. The interpretation of the group is defined by the Importer (e.g. Journi Moment, filesystem folder, album). |
| `asset_time` | Timestamp | No | Best available timestamp representing when the asset was created or captured. The Importer SHALL determine the most authoritative value available from the source. |
| `latitude` | Float | No | Geographic latitude associated with the asset. |
| `longitude` | Float | No | Geographic longitude associated with the asset. |
| `suggested_event` | String | No | Suggested initial value for the project event associated with the asset. |
| `suggested_location` | String | No | Suggested initial user location associated with the asset. |
| `suggested_info` | String | No | Suggested descriptive information associated with the asset. |
| `is_registration_complete` | Boolean | Yes | Indicates whether this registration completes the Registration phase for the project. |

---

### 7.2.2 Canonical Parameter Mapping

The Core SHALL map the canonical Asset Information supplied by the
Importer to the persistent Project Schema defined by
`PROJECT_JSON.md`.

The following table illustrates the mapping used by Core API Version 1.

| API Parameter | `project.json` Field | Notes |
|---------------|----------------------|-------|
| `asset_id` | `guid` | Immutable source identifier. |
| `group_id` | `moment_id` | Logical asset grouping. |
| `asset_time` | *(Not stored directly)* | Used by the Core and Metadata Policies to initialise user metadata where appropriate. |
| `latitude` | `lat` | Source latitude. |
| `longitude` | `lng` | Source longitude. |
| `suggested_event` | `event` | Initialises the user-owned `event` field in accordance with the Metadata Policies. |
| `suggested_location` | `location` | Initialises the user-owned `location` field in accordance with the Metadata Policies. |
| `suggested_info` | `info` | Initialises the user-owned `info` field in accordance with the Metadata Policies. |
| `is_registration_complete` | `workspace.registration_status` | When `true`, the Core SHALL update the Workspace registration status to `COMPLETE`. |

---

### 7.2.3 Asset Registration Rules

The following rules apply to all invocations of
CORE-002 Register Asset.

1. Each invocation SHALL register exactly one asset.

2. Every asset to be included in the project SHALL be registered using a
   separate invocation of CORE-002 Register Asset.

3. CORE-001 Create Project SHALL complete successfully before the first
   invocation of CORE-002 Register Asset.

4. The Importer SHALL supply all mandatory Asset Information for the
   asset being registered.

5. The Core SHALL create a corresponding Photo Object for each
   successfully registered asset.

6. The `is_registration_complete` parameter SHALL be `false` for every
   asset except the final registration.

7. Exactly one successful registration SHALL have
   `is_registration_complete = true`.

8. Receipt of `is_registration_complete = true` SHALL indicate
   completion of the Registration phase.

9. Asset acquisition SHALL NOT commence until the Registration phase has
   completed.

10. The Importer SHALL NOT modify `project.json` directly.

---

### Notes

Asset Information describes the source asset using the canonical Photo
Manager data model.

Binary asset data is transferred separately using
CORE-003 Transfer Asset.

## 7.3 CORE-003 – Transfer Asset

### Purpose

Transfers the binary asset data for a previously registered asset from
the Importer to the Core.

This service transfers the asset data associated with a previously
registered asset.

The Core SHALL validate the supplied Asset Data, store the asset within
the project workspace and update the corresponding Photo Object.

This service SHALL only be invoked for assets that have previously been
registered using CORE-002 Register Asset.

The final invocation SHALL indicate completion of the Acquisition phase
using the `is_download_complete` parameter.

---

### Responsibilities

#### Importer

- Acquire the requested asset from the source system.
- Supply the corresponding `asset_id`.
- Supply the Asset Data.
- Correctly identify completion of the Acquisition phase using
  `is_download_complete`.

#### Core

- Validate the supplied Asset Data.
- Locate the corresponding Photo Object.
- Store the asset within the project workspace.
- Update all Core-managed download fields.
- Update the Workspace download status.
- Detect completion of the Acquisition phase.

---

### 7.3.1 Asset Data

The following Asset Data SHALL be supplied by the Importer when transferring
an asset.

The field names defined below form the canonical interface between the
Importer and the Core.

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `asset_id` | String | Yes | Identifier of the previously registered asset. |
| `asset_data` | Binary | Yes | Binary representation of the asset. |
| `is_download_complete` | Boolean | Yes | Indicates whether this transfer completes the Acquisition phase for the project. |

---

### 7.3.2 Asset Transfer Rules

The following rules apply to all invocations of
CORE-003 Transfer Asset.

1. Each invocation SHALL transfer exactly one asset.

2. The specified `asset_id` SHALL previously have been registered using
   CORE-002 Register Asset.

3. The Core SHALL reject attempts to transfer data for unknown assets.

4. The Importer SHALL supply valid Asset Data for the specified asset.

5. The Core SHALL update the corresponding Photo Object following
   successful storage.

6. The `is_download_complete` field SHALL be `false` for every asset
   except the final asset transfer.

7. Exactly one successful asset transfer SHALL have
   `is_download_complete = true`.

8. Receipt of `is_download_complete = true` SHALL indicate completion of
   the Acquisition phase.

9. The Importer SHALL NOT invoke CORE-003 Transfer Asset after
   successfully transferring an asset with
   `is_download_complete = true`.

10. The Importer SHALL NOT modify `project.json` directly.

---

### Notes

CORE-003 transfers binary asset data only.

All Asset Information SHALL previously have been transferred using
CORE-002 Register Asset.

The Core is responsible for determining the persistent storage location
of the asset within the project workspace.

## 7.4 CORE-004 - Communications

### Purpose

Provides the communications interface implemented by the Core during an
import operation.

This interface enables the Importer to communicate progress,
informational messages, warnings and errors to the Core.

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
| `data` | No | Optional implementation-defined data associated with the message. |

### Message Types

CORE-004 supports the following message types.

| Message Type | Purpose |
|--------------|---------|
| `STATUS` | Reports normal runtime status information. No user action is required. |
| `ACTION_REQUIRED` | Indicates that the Importer cannot continue until the user performs a required action. |
| `WARNING` | Reports a recoverable condition that does not prevent the current operation from continuing. |
| `ERROR` | Reports an unrecoverable condition that prevents the Importer from continuing the current operation. |

#### STATUS

Reports normal runtime status information from the Importer.

STATUS messages are intended to keep the user informed of the current
activity being performed by the Importer.

The Core MAY display the message to the user, record it in the log, or
both.

Receipt of a STATUS message SHALL NOT alter the state of the current
import operation.

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

The Core SHALL determine the appropriate recovery action and MAY
subsequently instruct the Importer to RESUME, RETRY or CANCEL the
operation using IMPORTER-001.

### Notes

CORE-004 MAY be invoked at any time during an import operation,
including before invocation of CORE-001 Create Project.

CORE-004 communications are not associated with a Project Context.

Importers SHALL NOT assume how the Core displays or records received
messages.

The Core MAY present messages using any implementation-defined user
interface.

=====================================================
PART II – Importer API
=====================================================

# 8. Importer Responsibilities

The Importer is responsible for:

- Communicating with a specific source system.
- Enumerating source assets in a deterministic order.
- Translating source-specific information into the canonical Photo
  Manager data model.
- Registering assets with the Core.
- Acquiring asset data from the source system.
- Transferring asset data to the Core.
- Reporting runtime status, warnings and errors to the Core.
- Responding to commands issued by the Core.
- Managing any source-specific user interfaces required during an import
  operation.
- Managing any source-specific configuration and authentication
  information.

The Importer MAY maintain persistent source-specific configuration,
authentication information and other source state independent of any
Photo Manager project.

The Importer SHALL NOT directly modify `project.json`.

The Importer SHALL NOT maintain persistent project state.

# 9. Importer Services

The Importer exposes a minimal set of public services for use by the
Core.

These services define the complete public interface implemented by an
Importer.

## 9.1 IMPORTER-001 – Core Communications

### Purpose

Provides the communications interface implemented by the Importer during
an import operation.

This interface enables the Core to control the execution of an import
operation.

The Importer SHALL respond appropriately to commands issued by the Core.

---

### Interface Overview

IMPORTER-001 defines the communications interface implemented by the
Importer.

The Core SHALL use this interface to control the execution of an import
operation.

The mechanism used to transport these communications is implementation
dependent.

A native implementation MAY use direct function calls, while distributed
implementations MAY use any equivalent inter-process communication
mechanism.

---

### Command Format

Every communication sent using IMPORTER-001 SHALL contain the following
information.

| Field | Mandatory | Description |
|-------|-----------|-------------|
| `command` | Yes | Identifies the command to be performed. |
| `data` | No | Command-specific data associated with the command. The structure of this field is defined by the individual command type. |

---

### Command Types

IMPORTER-001 supports the following command types.

| Command | Purpose |
|---------|---------|
| `PAUSE` | Suspends the current import operation. |
| `RESUME` | Commences or continues the specified import phase. |
| `RETRY` | Retries acquisition of the specified asset. |
| `CANCEL` | Terminates the current import operation. |

#### PAUSE

Suspends the current import operation.

Upon receipt of a PAUSE command, the Importer SHALL suspend the import
operation at the next safe interruption point.

The Importer SHALL NOT terminate an operation that is already in
progress if doing so could leave the source system or the project in an
inconsistent state.

Following successful suspension, the Importer SHALL wait for either a
RESUME or CANCEL command from the Core.

#### RESUME

Commences or continues an import phase.

The RESUME command SHALL identify:

- the import phase to be resumed; and
- the last asset successfully processed during that phase.

A value of `NULL` for the last successfully processed asset indicates
that processing SHALL commence with the first asset in the source.

Upon receipt of a RESUME command, the Importer SHALL commence or
continue processing with the asset immediately following the last
successfully processed asset.

The Importer SHALL continue processing subsequent assets in the normal
source enumeration order until the current phase completes or another
command is received.

Supported phases are:

| Phase | Description |
|--------|-------------|
| `REGISTRATION` | Resume asset registration. |
| `ACQUISITION` | Resume asset acquisition. |

The Core determines the phase to be resumed.

The Importer SHALL NOT infer the current phase from project state.

#### RETRY

Retries acquisition of the specified asset.

The RETRY command SHALL identify the asset to be retried.

Upon receipt of a RETRY command, the Importer SHALL attempt to acquire
the specified asset from the source system.

Following completion of the retry attempt, the Importer SHALL await
further commands from the Core.

If the retry is unsuccessful, the Importer SHALL report the failure to
the Core using CORE-004.

#### CANCEL

Terminates the current import operation.

Upon receipt of a CANCEL command, the Importer SHALL terminate the
current import operation at the next safe interruption point.

The Importer SHALL release any resources associated with the current
import operation, including any connections to the source system.

The Importer SHALL NOT leave the source system or the project in an
inconsistent state.

Following completion of the cancellation, the Importer SHALL terminate
the current import operation and release all associated resources.
