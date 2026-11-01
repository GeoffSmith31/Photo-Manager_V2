# Photo Manager V2
# Importer SDK Specification

**Status:** Superseded
**Superseded by:** ADR-012 — Standalone Importers and Project JSON Contract
**Date:** 2026-10-21

> **Notice:** This specification describes an earlier Photo Manager architecture and is retained for historical reference only. It is no longer authoritative and must not be used as a requirement for new development. The `project.json` format is the contract between standalone Importers and Photo Manager. Refer to the Project JSON Reference for the authoritative description of that contract.

Document Version: 1.2

Defines:

    Importer SDK Version 1

Normative References:

CORE_IMPORTER_API_SPECIFICATION.md   Version 1.2
PROJECT_JSON.md                      Version 2
SPECIFICATION_STYLE_GUIDE.md         Version 1.0

---

# 1. Purpose

This document defines the Software Development Kit (SDK) used to develop
Importer plugins for Photo Manager.

It provides implementation guidance for developers creating Importers
that communicate with the Photo Manager Core.

It supplements the Core–Importer API Specification by describing the
expected structure, lifecycle, interfaces and implementation practices
of an Importer.

This includes guidance for Importer discovery, Capability Information,
activation, source interaction, project creation, asset registration,
asset acquisition, recovery and runtime communication.

This document does not redefine the behaviour specified by the
Core–Importer API Specification.

Where this document provides implementation guidance, the requirements
of the Core–Importer API Specification SHALL take precedence.
---

# 2. Scope

This specification applies to all Importers developed for the Photo
Manager system.

It defines:

- Importer architecture.
- Importer discovery and Capability Information.
- Importer activation and initialisation.
- Source interaction and workspace discovery.
- Importer lifecycle.
- SDK interfaces.
- Registration and asset acquisition behaviour.
- Recovery and runtime control.
- Recommended implementation practices.

This specification does not define:

- The Core API.
- The Importer API contract.
- Project JSON structures.
- Internal Core implementation.
- User interface design.
- Source-specific implementation details.

The requirements governing communication between the Core and an Importer
are defined by the Core–Importer API Specification.

Where this specification provides implementation guidance, that guidance
SHALL remain consistent with the Core–Importer API Specification.

---

# 3. Architecture Overview

The Photo Manager Importer SDK provides the framework used to implement
Importers that communicate with the Photo Manager Core and a specific
source system.

An Importer operates between the Core and its source system.

The Core owns the Photo Manager project, persistent project state,
application workflow and user-facing application behaviour.

The Importer owns communication with its source system, source-specific
interaction, source-specific authentication, source enumeration,
translation of source information into the canonical Photo Manager data
model and acquisition of source asset data.

A typical Importer interaction is illustrated below.

    +----------------------+
    |         Core         |
    |----------------------|
    | Project Management   |
    | Workflow             |
    | Persistent State     |
    | User Interface       |
    +----------+-----------+
               |
       Importer Interface
               |
    +----------v-----------+
    |       Importer       |
    |----------------------|
    | Discovery Information|
    | Initialisation       |
    | Source Interaction   |
    | Registration         |
    | Acquisition          |
    | Runtime Communication|
    +----------+-----------+
               |
               |
    +----------v-----------+
    |    Source System     |
    +----------------------+

The Importer lifecycle consists of the following conceptual stages:

    Discovery
        |
        v
    Capability Information
        |
        v
    Activation / Initialisation
        |
        v
    Source Interaction
        |
        v
    Project Creation
        |
        v
    Registration
        |
        v
    Acquisition
        |
        v
    Completion / Cancellation
        |
        v
    Shutdown

These stages describe the expected behaviour of an Importer. They do not
require a one-to-one correspondence with the internal classes, functions
or state representation used by a particular Importer.

### Discovery

During Discovery, the Core identifies available Importers and obtains
their static Capability Information.

Discovery SHALL NOT activate an Importer or establish communication with
its source system.

### Capability Information

Capability Information describes the Importer's identity, compatibility,
requirements and declared capabilities.

Capability Information SHALL be available without requiring source-system
authentication or source-system access.

### Activation and Initialisation

When the user selects an Importer for an import operation, the Core
activates the Importer.

The Importer initialises its source-specific runtime environment and
prepares to interact with its source system.

### Source Interaction

The Importer performs any source-specific interaction required to prepare
the import.

This MAY include authentication, source or workspace selection,
source-specific configuration and other user interaction required by the
source system.

The Importer gathers the information required to create the Photo
Manager project.

### Project Creation

Once sufficient information has been obtained, the Importer invokes
CORE-001 Create Project.

The Core creates the project and returns a Project Context.

The Importer SHALL retain the Project Context for subsequent operations
associated with the project.

### Registration

The Importer drives the Registration Phase.

The Importer enumerates the selected source and submits each asset to the
Core using CORE-002 Register Asset.

When all assets have been successfully submitted, the Importer reports
Registration completion using CORE-004 Communications.

### Acquisition

The Core drives the Acquisition Phase.

The Core requests individual assets from the Importer using the
`ACQUIRE_ASSET` control operation.

The Importer acquires the requested asset from the source system and
returns its Asset Data to the Core.

The Core determines the acquisition sequence, records the persistent
acquisition state and determines whether further acquisition attempts are
required.

### Recovery

The Core owns persistent recovery information.

If Registration is interrupted, the Core MAY instruct the Importer to
resume Registration from the Registration Checkpoint.

The Core SHALL supply the source information required to establish or
restore source communication as part of the `RESUME_REGISTRATION`
operation.

If Acquisition is interrupted, the Core MAY request individual assets
again using `ACQUIRE_ASSET`.

The Core SHALL supply the source information required to establish or
restore source communication as part of each `ACQUIRE_ASSET` operation.

The Importer SHALL NOT rely on persistent project-specific state to
determine recovery positions.

### Completion and Cancellation

The Core determines when the import operation has completed.

The Core MAY terminate an active import operation by issuing the
`CANCEL` control operation.

The Importer SHALL release source-specific resources when the import
operation ends.

### Implementation Independence

The SDK defines the interfaces and implementation guidance required for
an Importer to participate in the Photo Manager import architecture.

The internal implementation of an Importer is implementation dependent.

An Importer MAY use any internal architecture, classes, modules,
processes or source-specific libraries provided that its externally
observable behaviour complies with the Core–Importer API Specification and
this SDK Specification.

---

# 4. Terminology

Terminology used throughout this document is defined by
SPECIFICATION_STYLE_GUIDE.md and the Core–Importer API Specification.

Terms defined by the Core–Importer API Specification SHALL have the same
meaning when used in this document.

The following terms are used by the Importer SDK to describe
implementation concepts:

**Importer Instance** – A runtime instance of an Importer activated by the
Core for an import operation.

**Source Connection** – The runtime connection or authenticated session
used by an Importer to communicate with its source system.

**Capability Information** – The Importer Capability Information declared
by an Importer and made available to the Core during Importer Discovery.

**Source Interaction** – The source-specific portion of Importer
Interaction performed by an Importer to authenticate, select or configure
the source and obtain the information required to prepare an import
operation.

Additional terminology specific to an Importer implementation MAY be
introduced where necessary, provided that it does not conflict with
terminology defined by the Core–Importer API Specification.

---

# 5. Design Principles

The Importer SDK has been designed according to the following principles.

- Importers communicate with a specific source system.
- Importers translate source-specific information into the canonical
  Photo Manager data model.
- Importers acquire source asset data; the Core owns persistent project
  storage.
- The Core owns the Photo Manager project and all persistent
  project-specific state.
- Importers SHALL communicate with the Core exclusively through the
  interfaces defined by the Core–Importer API Specification.
- Importers SHALL NOT modify `project.json` or other Core-owned persistent
  project files directly.
- Source-specific behaviour SHALL remain within the Importer.
- The Core SHALL NOT require knowledge of the internal structure or
  protocol of an Importer's source system.
- Importer Discovery SHALL be separate from Importer Activation.
- Importer Discovery SHALL NOT establish connections to source systems,
  perform authentication or enumerate source content.
- Capability Information SHALL describe the Importer's static
  characteristics and declared capabilities.
- Capability Information SHALL be available without requiring access to
  the source system.
- Runtime source state SHALL be established during Importer Activation
  and Source Interaction rather than being inferred from Capability
  Information.
- The Importer SHALL drive the Registration Phase.
- The Core SHALL drive the Acquisition Phase.
- Acquisition SHALL be performed one asset at a time at the direction of
  the Core.
- The Core SHALL own persistent registration and acquisition recovery
  state.
- The Importer SHALL NOT maintain persistent project-specific recovery
  state.
- The Importer SHALL maintain stable Source Order for Registration
  RESUME processing.
- The Core SHALL determine acquisition sequence and retry policy.
- A repeated acquisition request for the same asset SHALL be treated as
  a new acquisition attempt.
- Importers MAY maintain persistent source-specific configuration and
  authentication information independently of Photo Manager projects.
- Importers MAY maintain temporary runtime state required to communicate
  with a source system.
- Importers SHALL be capable of re-establishing source communication
  when required after an interruption.
- The SDK SHALL provide a stable foundation for future Importers.
- The SDK SHALL support future extension through additional interfaces,
  services and helper libraries.

The Importer SDK provides implementation guidance only.

Where an SDK implementation choice is not defined by this specification,
the Importer developer MAY choose an appropriate implementation provided
that the resulting Importer complies with the Core–Importer API
Specification.

---

# 6. Importer Responsibilities

The Importer is responsible for communicating with its source system and
translating source-specific information into the canonical Photo Manager
data model.

The Importer SHALL operate through the interfaces defined by the
Core–Importer API Specification and SHALL NOT access or modify Core-owned
persistent project state directly.

The Importer SHALL:

- Provide the interfaces required for discovery and Capability
  Information.
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
- Retain the Project Context returned by the Core.
- Enumerate assets in the selected source.
- Translate source-specific information into the canonical Asset
  Information model.
- Register assets with the Core using CORE-002 Register Asset.
- Maintain stable Source Order for Registration.
- Report Registration completion using CORE-004 Communications.
- Respond to Core-directed Registration recovery operations.
- Respond to Core-directed asset acquisition requests.
- Acquire requested asset data from the source system.
- Return acquired Asset Data to the Core through the `ACQUIRE_ASSET`
  operation.
- Report runtime status, warnings, errors and user-action requirements
  using CORE-004 Communications.
- Re-establish source communication when required during a recovery or
  acquisition operation.
- Register any source-specific user interface with the Core using
  CORE-004 UI-REGISTRATION when required.

The Importer SHALL NOT:

- Modify `project.json` directly.
- Modify other Core-owned persistent project files directly.
- Create or assign persistent Photo Manager project identifiers.
- Maintain persistent project-specific recovery state.
- Determine the Core's Registration Checkpoint.
- Determine the Core's acquisition sequence.
- Determine the Core's retry policy.
- Acquire assets that have not been requested by the Core.
- Mark an asset as successfully acquired without successfully returning
  its Asset Data to the Core.
- Determine overall Acquisition completion.
- Assume ownership of Core-managed project state.

### 6.1 Source System Responsibilities

The Importer owns communication with its source system.

This includes all source-specific behaviour required to obtain source
information and asset data.

The Importer SHALL manage source-specific:

- authentication;
- connections and sessions;
- workspace or source selection;
- source enumeration;
- source-specific metadata extraction;
- asset acquisition; and
- source-specific error handling.

The Core SHALL NOT require knowledge of the internal structure or
protocol of the source system.

The Importer MAY maintain persistent source-specific configuration,
authentication information and other source state that is independent of
a Photo Manager project.

The Importer SHALL NOT store Photo Manager project recovery information
as part of such source-specific state.

### 6.2 Project Creation

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

The Importer SHALL retain the Project Context for the duration of the
import operation.

The Importer SHALL supply the Project Context with subsequent Core
Service requests that require identification of the target project.

### 6.3 Registration

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

### 6.4 Acquisition

The Core controls the Acquisition Phase.

The Importer SHALL respond to individual `ACQUIRE_ASSET` requests issued
by the Core.

For each acquisition request, the Importer SHALL:

- Determine whether the required source connection is available.
- Use the supplied source information, where required, to establish or
  restore source communication.
- Identify the requested source asset using the supplied `asset_id`.
- Acquire the corresponding binary Asset Data from the source.
- Return the Asset Data to the Core as the result of the
  `ACQUIRE_ASSET` operation.
- Report any acquisition failure using the operation Result and
  CORE-004 Communications where appropriate.

The source information supplied with an `ACQUIRE_ASSET` request SHALL
include:

- `source`;
- `source_id`; and
- `source_title`.

The Importer SHALL process only the asset requested by the Core.

The Importer SHALL NOT determine which registered asset is requested
next.

The Importer SHALL NOT determine when Acquisition is complete.

A repeated `ACQUIRE_ASSET` request for the same `asset_id` SHALL be
treated as a new acquisition attempt.

### 6.5 Recovery

The Importer SHALL support recovery operations initiated by the Core.

For Registration recovery, the Importer SHALL:

- Receive the Project Context supplied by the Core.
- Receive the Registration Checkpoint supplied by the Core.
- Receive the source information supplied by the Core.
- Re-establish source communication if required.
- Re-enumerate the source in stable Source Order.
- Continue Registration from the position specified by the Core.
- Return the Project Context with subsequent CORE-002 requests.

The source information supplied for Registration recovery SHALL include:

- `source`;
- `source_id`; and
- `source_title`.

For Acquisition recovery, the Importer SHALL:

- Receive the Project Context supplied by the Core.
- Receive the source information supplied by the Core.
- Receive an `ACQUIRE_ASSET` request identifying the asset to be
  acquired.
- Re-establish source communication if required.
- Acquire that asset from the source.
- Return the Project Context with the resulting Asset Data.

The source information supplied for Acquisition recovery SHALL include:

- `source`;
- `source_id`; and
- `source_title`.

The Importer SHALL NOT rely on persistent project-specific state to
determine where a Registration or Acquisition operation should resume.

The Core is the authoritative owner of persistent recovery information.

### 6.6 Runtime Communication

The Importer SHALL use CORE-004 Communications to report runtime
conditions to the Core.

This includes:

- normal status;
- progress information;
- user actions required;
- warnings;
- errors; and
- Registration completion.

The Importer SHALL provide sufficient information for the Core to
identify the affected operation and, where applicable, the affected
asset.

The Importer SHALL NOT use runtime messages as a substitute for the
defined Core Services or Importer Services.

### 6.7 Resource Management

The Importer SHALL manage all source-specific runtime resources required
during an import operation.

This MAY include:

- network connections;
- authenticated sessions;
- temporary files;
- source-specific processes;
- source-specific caches; and
- other resources required by the source implementation.

The Importer SHALL release source-specific resources when they are no
longer required.

The Importer SHALL NOT assume that the Core will retain or restore
source-specific runtime state between separate import sessions.

The Importer MAY retain persistent source-specific configuration or
authentication information where appropriate, but such information SHALL
remain independent of Photo Manager project state.

---

# 7. Importer Lifecycle

An Importer progresses through a sequence of conceptual stages during an
import operation.

The exact internal implementation of these stages is implementation
dependent.

The behaviour observable by the Core SHALL comply with the
Core–Importer API Specification.

The lifecycle of an Importer is illustrated below.

    Discovery
        |
        v
    Capability Information
        |
        v
    Activation / Initialisation
        |
        v
    Source Interaction
        |
        v
    Project Creation
        |
        v
    Registration
        |
        v
    Acquisition
        |
        v
    Completion / Cancellation
        |
        v
    Shutdown

The stages above describe the normal progression of an Importer. They do
not require a one-to-one correspondence with the internal state
representation of the Importer or the Core.

---

## 7.1 Discovery

During Discovery, the Core identifies available Importer
implementations.

Discovery SHALL NOT require the Importer to establish communication
with its source system.

Discovery SHALL NOT:

- authenticate with the source system;
- enumerate source content;
- select a source workspace;
- acquire asset data; or
- modify a Photo Manager project.

The Core MAY reject an Importer during Discovery if the Importer does
not satisfy the structural or compatibility requirements defined by the
Core.

Successful Discovery does not establish that the Importer can
successfully communicate with its source system.

---

## 7.2 Capability Information

During Discovery, the Core MAY obtain the Importer's static Capability
Information.

Capability Information SHALL describe the Importer's declared identity,
compatibility, requirements and capabilities.

Capability Information SHALL be available without requiring access to
the source system.

The Importer SHALL NOT use Capability Information to represent transient
runtime conditions such as authentication state, source availability or
selected workspace.

Runtime source conditions SHALL be established during Source Interaction.

---

## 7.3 Activation and Initialisation

When the user selects an Importer for an import operation, the Core
activates the Importer.

The Importer SHALL initialise its runtime environment.

Initialisation MAY include:

- loading source-specific configuration;
- restoring source-specific authentication information;
- preparing source-specific libraries or resources;
- validating the runtime environment; and
- preparing temporary runtime state required during the import
  operation.

Initialisation SHALL NOT require the Importer to establish a source
connection unless required by the Importer's implementation or the
subsequent source interaction.

The Importer SHALL be capable of establishing source communication when
required by the import operation.

---

## 7.4 Source Interaction

During Source Interaction, the Importer establishes communication with
the source system and obtains the information required to prepare the
import.

This MAY include:

- authentication;
- source or workspace discovery;
- source or workspace selection;
- source-specific configuration;
- source-specific user interaction; and
- determination of Initial Metadata Policies.

The Importer SHALL perform source-specific interaction.

The Core SHALL remain responsible for the overall application workflow
and SHALL determine how Importer status and user-action requirements are
presented to the user.

The Importer SHALL NOT commence project creation until sufficient
information has been obtained to invoke CORE-001 Create Project.

---

## 7.5 Project Creation

Once sufficient source and project information has been obtained, the
Importer SHALL invoke CORE-001 Create Project.

The Core SHALL create the project and return a Project Context.

The Importer SHALL retain the Project Context for the duration of the
import operation.

The Importer SHALL supply the Project Context with subsequent Core
Service requests that require identification of the target project.

The Importer SHALL NOT commence Registration until CORE-001 has
completed successfully.

---

## 7.6 Registration

The Importer drives the Registration Phase.

During Registration, the Importer SHALL:

- enumerate the selected source;
- maintain stable Source Order;
- identify each asset to be included in the project;
- construct the canonical Asset Information for each asset; and
- submit each asset to the Core using CORE-002 Register Asset.

The Importer SHALL continue Registration until all assets identified for
inclusion in the project have been successfully submitted to the Core.

The Importer SHALL then communicate Registration completion using
CORE-004 Communications.

The Importer SHALL NOT commence Acquisition merely because it has
completed its local Registration processing.

Acquisition SHALL commence only when requested by the Core.

---

## 7.7 Acquisition

The Core drives the Acquisition Phase.

The Core requests individual registered assets from the Importer using
the `ACQUIRE_ASSET` control operation.

For each request, the Importer SHALL:

- determine whether source communication is available;
- use the source information supplied with the request, where required,
  to establish or restore source communication;
- identify the requested source asset;
- acquire the corresponding Asset Data; and
- return the Asset Data to the Core as the result of the
  `ACQUIRE_ASSET` operation.

The source information supplied with an `ACQUIRE_ASSET` request SHALL
include:

- `source`;
- `source_id`; and
- `source_title`.

The Importer SHALL process only the asset requested by the Core.

The Importer SHALL NOT determine the acquisition sequence.

The Importer SHALL NOT determine overall Acquisition completion.

If acquisition of an asset fails, the Importer SHALL report the failure
through the operation Result and, where appropriate, CORE-004
Communications.

The Core MAY subsequently issue another `ACQUIRE_ASSET` request for the
same asset.

---

## 7.8 Recovery

An import operation MAY be interrupted during Registration or
Acquisition.

The Core owns persistent recovery information and determines the
appropriate recovery operation.

If Registration is incomplete, the Core MAY issue
`RESUME_REGISTRATION`.

The `RESUME_REGISTRATION` operation SHALL provide the Importer with:

- the Project Context;
- the Registration Checkpoint; and
- the source information required to establish or restore source
  communication.

The source information supplied for `RESUME_REGISTRATION` SHALL include:

- `source`;
- `source_id`; and
- `source_title`.

The Importer SHALL re-establish source communication if required and
continue Registration from the Registration Checkpoint supplied by the
Core.

If Acquisition is incomplete, the Core SHALL determine which registered
assets require acquisition and MAY issue `ACQUIRE_ASSET` requests for
those assets.

Each `ACQUIRE_ASSET` request SHALL provide the Importer with:

- the Project Context;
- the requested `asset_id`; and
- the source information required to establish or restore source
  communication.

The source information supplied for `ACQUIRE_ASSET` SHALL include:

- `source`;
- `source_id`; and
- `source_title`.

The Importer SHALL NOT require persistent project-specific state to
perform either recovery operation.

---

## 7.9 Completion

The Core determines when the import operation has completed.

Registration completion is established when the Importer has completed
source enumeration and has communicated Registration completion to the
Core.

Acquisition completion is determined by the Core from the persistent
acquisition state of the registered assets.

The Importer SHALL NOT independently declare overall import completion
to the Core.

When the Core determines that the import operation is complete, the
Importer SHALL perform the required shutdown processing.

---

## 7.10 Cancellation

The Core MAY issue the `CANCEL` control operation at any appropriate
point during an active import operation.

Upon receiving `CANCEL`, the Importer SHALL terminate source-specific
processing at the next safe interruption point.

The Importer SHALL release source-specific resources associated with the
current import operation.

The Importer SHALL NOT modify persistent project state as part of
cancellation.

The Core SHALL remain responsible for the resulting persistent project
state.

---

## 7.11 Shutdown

Upon completion or cancellation of an import operation, the Importer
SHALL perform an orderly shutdown.

Shutdown SHALL include:

- releasing resources associated with the current import operation;
- closing source connections that are no longer required; and
- releasing temporary runtime state associated with the project.

The Importer SHALL release source-specific resources that it owns.

Source-specific user interfaces registered with the Core using
CORE-004 UI-REGISTRATION SHALL NOT be treated as Importer-owned UI
resources for lifecycle management. Their lifecycle SHALL be managed by
the Photo Manager window-management infrastructure.

The Importer MAY retain persistent source-specific configuration,
authentication information and other source state that is independent
of the Photo Manager project.

The Importer SHALL NOT retain persistent project-specific recovery
state.

The Importer SHALL be capable of being activated for a subsequent import
operation after shutdown.

=====================================================
PART II – SDK Interface
=====================================================

# 8. Importer Interface

Every Importer SHALL implement the interfaces required by the Importer
SDK.

These interfaces provide the implementation framework through which the
Core discovers, activates and interacts with an Importer.

The SDK interfaces SHALL comply with the requirements of the
Core–Importer API Specification.

The implementation of these interfaces is language and platform
independent.

The Core SHALL interact with an Importer only through the interfaces
defined by the applicable API and SDK specifications.

The internal implementation of an Importer is outside the scope of this
specification.

## 8.1 Capability Information

Every Importer SHALL provide the Capability Information required for
Importer Discovery.

The Capability Information interface SHALL allow the Core to obtain
static information about the Importer without activating it or
establishing communication with the source system.

The Capability Information SHALL conform to the structure defined by the
Core–Importer API Specification.

The Importer SHALL NOT perform source-specific authentication, source
enumeration or asset acquisition as a consequence of a Capability
Information request.

Capability Information SHALL remain independent of the runtime state of
the Importer and its source system.

## 8.2 Initialisation

The Importer SHALL provide an initialisation interface that prepares the
Importer for activation.

Initialisation MAY include:

- Loading source-specific configuration.
- Restoring source-specific authentication information.
- Loading source-specific libraries or resources.
- Validating the runtime environment.
- Preparing temporary resources required during an import operation.

Initialisation SHALL NOT require source communication unless required by
the Importer's implementation.

The Importer SHALL be capable of establishing source communication when
required by Source Interaction or a subsequent control operation.

The Importer SHALL report unrecoverable initialisation errors to the Core
using the communications interface defined by the Core–Importer API
Specification.

Successful initialisation SHALL prepare the Importer to perform Source
Interaction or other operations required by the Core.

## 8.3 Configuration

The Importer MAY provide source-specific configuration options.

Configuration enables an Importer to customise its interaction with a
particular source system.

Typical configuration items include:

- Source-specific authentication information.
- Source-specific preferences.
- Selection of source-specific metadata.
- Rules used when translating source information into the canonical
  Photo Manager data model.
- Temporary storage locations.
- Performance-related options.

The Core SHALL NOT interpret or modify Importer-specific configuration.

The Importer SHALL apply its configuration consistently throughout an
import operation.

Source-specific configuration MAY be retained between import operations
provided that it does not contain persistent Photo Manager project
state.

## 8.4 Source Interaction

The Importer SHALL provide the source-specific interaction required to
prepare an import operation.

Source Interaction MAY include:

- Establishing communication with the source system.
- Authenticating the user.
- Selecting a source workspace or collection.
- Gathering source-specific configuration.
- Discovering source information.
- Determining Initial Metadata Policies.
- Presenting source-specific user interfaces.

The Importer SHALL obtain the information required to invoke CORE-001
Create Project.

The Core SHALL remain responsible for the overall application workflow.

The Importer MAY present source-specific user interaction, but SHALL
report conditions requiring Core or user attention using the mechanisms
defined by the Core–Importer API Specification.

## 8.5 Project Creation

Once sufficient information has been obtained from the source
interaction, the Importer SHALL invoke CORE-001 Create Project.

The Importer SHALL supply the project information and Initial Metadata
Policies required by the Core API.

The Importer SHALL wait for successful completion of CORE-001 before
commencing Registration.

The Core SHALL return a Project Context following successful project
creation.

The Importer SHALL retain the Project Context for the duration of the
import operation.

The Importer SHALL supply the Project Context with subsequent Core
Service requests that require identification of the target project.

## 8.6 Registration Interface

The Importer SHALL provide the implementation required to perform the
Registration Phase.

The Importer SHALL:

- Enumerate the selected source.
- Maintain stable Source Order.
- Identify each asset to be included in the project.
- Construct the canonical Asset Information.
- Invoke CORE-002 Register Asset for each asset.
- Communicate Registration completion using CORE-004.

The Importer SHALL NOT indicate Registration completion through the
final CORE-002 request.

Registration completion SHALL be communicated using the mechanism
defined by the Core–Importer API Specification.

The Importer SHALL NOT commence Acquisition merely because its local
Registration processing has completed.

## 8.7 Acquisition Interface

The Importer SHALL provide the implementation required to respond to
Core-directed `ACQUIRE_ASSET` operations.

The Core SHALL determine which registered asset is to be acquired.

For each `ACQUIRE_ASSET` operation, the Importer SHALL:

- Identify the requested source asset.
- Determine whether source communication is available.
- Use the source information supplied with the operation, where required,
  to establish or restore source communication.
- Acquire the requested Asset Data.
- Return the Asset Data to the Core as the result of the operation.

The source information supplied with an `ACQUIRE_ASSET` operation SHALL
include:

- `source`;
- `source_id`; and
- `source_title`.

The Importer SHALL process only the asset identified by the Core.

The Importer SHALL NOT determine the acquisition sequence.

The Importer SHALL NOT determine overall Acquisition completion.

A repeated `ACQUIRE_ASSET` request for the same asset SHALL constitute a
new acquisition attempt.

The Importer SHALL NOT maintain persistent project-specific acquisition
progress.

## 8.8 Recovery Interface

The Importer SHALL provide the implementation required to respond to
Core-directed recovery operations.

For Registration recovery, the Importer SHALL support
`RESUME_REGISTRATION`.

The `RESUME_REGISTRATION` operation SHALL provide the Importer with:

- the Project Context;
- the Registration Checkpoint; and
- the source information required to establish or restore source
  communication.

The source information supplied for `RESUME_REGISTRATION` SHALL include:

- `source`;
- `source_id`; and
- `source_title`.

The Importer SHALL use the Registration Checkpoint supplied by the Core
to determine where Registration is to resume.

The Importer SHALL re-enumerate the source in stable Source Order.

For Acquisition recovery, the Importer SHALL respond to
`ACQUIRE_ASSET` requests for assets whose acquisition has not reached a
terminal state.

Each `ACQUIRE_ASSET` request SHALL provide the Importer with:

- the Project Context;
- the requested `asset_id`; and
- the source information required to establish or restore source
  communication.

The source information supplied for `ACQUIRE_ASSET` SHALL include:

- `source`;
- `source_id`; and
- `source_title`.

The Importer SHALL NOT require persistent project-specific state to
perform recovery.

## 8.9 Control Interface

The Importer SHALL provide the control interface defined by
IMPORTER-001.

The supported control operations are:

- `RESUME_REGISTRATION`;
- `ACQUIRE_ASSET`; and
- `CANCEL`.

The Importer SHALL respond to each control operation according to the
requirements of the Core–Importer API Specification.

The Importer SHALL NOT infer Core control operations from its own
internal state.

The Core is the authoritative owner of project recovery state and
control decisions.

## 8.10 Communications Interface

The Importer SHALL provide the implementation required to communicate
runtime information to the Core using CORE-004.

The Importer MAY report:

- status;
- progress;
- user actions required;
- warnings;
- errors;
- Registration completion; and
- source-specific user interface registration.

When source-specific user interaction requires a user interface created
or launched by the Importer, the Importer SHALL register that user
interface with the Core using the `UI-REGISTRATION` message defined by
CORE-004.

The Importer SHALL provide sufficient information for the Core to
identify the affected operation and, where applicable, the affected
asset.

The Importer SHALL NOT use CORE-004 as a substitute for the defined Core
Services or Importer Services.

## 8.11 Shutdown

The Importer SHALL provide an orderly shutdown mechanism.

Shutdown SHALL:

- release resources associated with the current import operation;
- close source connections that are no longer required; and
- release temporary project-related runtime state.

Source-specific user interfaces registered with the Core using
`UI-REGISTRATION` SHALL NOT be treated as Importer-owned UI resources for
lifecycle management. Their lifecycle SHALL be managed by the Photo
Manager window-management infrastructure.

The Importer MAY retain source-specific configuration and authentication
information for future import operations.

The Importer SHALL NOT retain persistent Photo Manager project state.

Following shutdown, the Importer SHALL be capable of being activated for
a subsequent import operation.

---

# 9. Source Connection and Reconnection

An Importer is responsible for establishing and maintaining communication
with its source system as required by the current import operation.

The Importer SHALL NOT assume that a source connection remains available
for the lifetime of an Importer instance.

A source connection MAY be unavailable because:

- the Importer has just been activated;
- the application has been restarted;
- the source session has expired;
- the source connection has been lost;
- the source system is temporarily unavailable; or
- the Importer has released the connection following a previous
  operation.

The Importer SHALL be capable of establishing or restoring source
communication when required.

## 9.1 Establishing Source Communication

The Importer MAY establish source communication during Source Interaction
when required to authenticate the user, discover available workspaces or
select the source to be imported.

The Importer MAY also establish source communication later when required
by Registration, Acquisition or Recovery.

The mechanism used to communicate with the source system is
source-specific and is outside the scope of this specification.

The Importer SHALL manage all source-specific authentication,
connections, sessions and related resources.

## 9.2 Source Information

The Core SHALL supply source information with each control operation that
may require the Importer to establish or restore source communication.

The source information consists of:

- `source`;
- `source_id`; and
- `source_title`.

For `RESUME_REGISTRATION`, the Core SHALL supply the source information
required to establish or restore source communication.

For `ACQUIRE_ASSET`, the Core SHALL supply the source information required
to establish or restore source communication.

The Importer SHALL use the supplied source information only for the
operation for which it was provided.

The Importer SHALL treat the supplied source information according to
the requirements of the source implementation.

The Core SHALL NOT be required to interpret the meaning of `source_id`.

The Importer SHALL NOT modify the Project Context while establishing
source communication.

## 9.3 Source Authentication

The Importer SHALL perform source-specific authentication where required
by the source system.

Authentication MAY require user interaction.

The Importer MAY retain source-specific authentication information for
future import operations where permitted by the source system and the
application environment.

Authentication information SHALL remain source-specific.

Authentication information SHALL NOT be stored as Photo Manager
project-specific state unless explicitly required by another
specification.

If authentication is required before an operation can continue, the
Importer SHALL report the condition to the Core using the mechanisms
defined by the Core–Importer API Specification.

## 9.4 Connection During Registration

During Registration, the Importer SHALL maintain sufficient source
communication to enumerate the source and submit assets to the Core.

If source communication is interrupted, the Importer SHALL attempt to
restore communication where possible using source-specific information
and runtime state available to the Importer.

If Registration is interrupted and the Core initiates recovery using
`RESUME_REGISTRATION`, the Core SHALL supply the source information
required to establish or restore source communication.

Following successful restoration, the Importer SHALL continue Registration
according to the Registration Checkpoint supplied by the Core.

The Importer SHALL NOT create or maintain its own persistent Registration
Checkpoint.

## 9.5 Connection During Acquisition

During Acquisition, the Core may issue an `ACQUIRE_ASSET` request when
the Importer does not have an active source connection.

The Importer SHALL establish or restore source communication before
attempting to acquire the requested asset.

The `ACQUIRE_ASSET` request SHALL provide the source information required
to establish or restore source communication.

The source information supplied with the request SHALL include:

- `source`;
- `source_id`; and
- `source_title`.

Once source communication has been established, the Importer SHALL
continue the `ACQUIRE_ASSET` operation.

The Importer SHALL NOT substitute another asset while establishing
source communication.

## 9.6 Connection Failure

If the Importer cannot establish or restore source communication, the
Importer SHALL return a failed operation Result and SHALL report
appropriate diagnostic information to the Core.

Where user intervention is required, the Importer SHOULD report an
`ACTION_REQUIRED` condition using CORE-004.

Where the condition prevents the requested operation from completing,
the Importer SHALL report an appropriate error condition.

The Importer SHALL NOT report successful completion of an operation until
the required source interaction has completed successfully.

## 9.7 Connection Release

The Importer MAY release a source connection when it is no longer
required.

An Importer SHALL NOT assume that maintaining a persistent connection is
necessary between individual operations.

The Importer SHALL be capable of re-establishing source communication
when subsequently required.

Source connections and sessions are runtime resources owned by the
Importer and SHALL NOT be treated as persistent Photo Manager project
state.

---

# 10. Error Handling and Diagnostics

An Importer SHALL detect, classify and report conditions that prevent or
may affect successful completion of an import operation.

The Importer SHALL provide sufficient information for the Core to
determine an appropriate workflow response.

The Core–Importer API Specification defines the formal Result states and
CORE-004 message types used for communication of these conditions.

This section provides implementation guidance for producing useful
diagnostic information.

## 10.1 Error Classification

Importer errors SHOULD be classified according to the nature of the
condition.

Typical classifications include:

- Authentication failure.
- Source connection failure.
- Source availability failure.
- Source permission failure.
- Source selection failure.
- Source enumeration failure.
- Asset acquisition failure.
- Invalid or unexpected source data.
- Local resource failure.
- Importer implementation failure.

An Importer MAY define additional source-specific classifications where
useful.

Source-specific classifications SHOULD remain within the Importer and
SHOULD NOT require the Core to understand source-specific implementation
details.

## 10.2 Operation Results

An Importer SHALL use the Result associated with the current operation to
indicate whether that operation completed successfully.

The Importer SHALL NOT use CORE-004 as a substitute for an operation
Result.

For IMPORTER-001 operations, the Result SHALL comply with the
requirements defined by the Core–Importer API Specification.

The defined Result values are:

- `COMPLETED` indicates successful completion of the requested operation.
- `FAILED` indicates that the requested operation could not be completed.

An Importer SHALL NOT return `COMPLETED` when the requested operation has
failed.

When an operation returns `FAILED`, the Importer SHOULD provide
appropriate diagnostic information using CORE-004 where useful.

## 10.3 CORE-004 Communications

The Importer SHALL use CORE-004 Communications to report runtime
conditions where appropriate.

The Importer MAY report:

- normal status;
- progress information;
- user actions required;
- warnings; and
- errors.

CORE-004 messages SHALL provide sufficient information for the Core to
identify the affected operation and, where applicable, the affected
asset.

The Importer SHALL NOT assume how the Core displays or records these
messages.

## 10.4 Error Information

An error report SHOULD provide, where applicable:

- a classification of the error;
- a concise human-readable description;
- the operation that was affected;
- the affected asset, where applicable;
- relevant source-specific information;
- technical diagnostic information; and
- known recovery information.

The human-readable description SHOULD explain the condition in terms
that are useful to the user or developer.

Technical diagnostic information SHOULD provide sufficient detail to
assist troubleshooting without requiring the Core to understand the
internal implementation of the Importer.

## 10.5 User Action Required

When an operation cannot continue without user interaction, the Importer
SHOULD report an `ACTION_REQUIRED` condition using CORE-004.

Examples include:

- authentication is required;
- authentication has expired;
- a source workspace must be selected;
- a source permission must be granted;
- source-specific configuration is required; or
- a source-specific decision is required from the user.

The Importer SHOULD provide sufficient information for the Core to
present useful guidance to the user.

The Importer SHALL NOT assume that the Core understands the internal
details of the source-specific operation.

## 10.6 Warnings

The Importer SHOULD use `WARNING` when a condition does not prevent the
current operation from continuing.

Examples include:

- optional source metadata could not be obtained;
- a non-critical source item could not be interpreted;
- source information is incomplete; or
- an individual condition has been encountered but processing can
  continue.

A warning SHALL NOT be used to indicate successful acquisition of an
asset that was not successfully acquired.

The Core determines whether warnings are displayed, recorded or retained
in application diagnostics.

## 10.7 Asset Acquisition Errors

If an individual asset cannot be acquired, the Importer SHALL report
the acquisition failure through the Result of the corresponding
`ACQUIRE_ASSET` operation.

The Importer MAY additionally report the failure using CORE-004
Communications.

The Importer SHALL identify the affected `asset_id` where appropriate.

The Importer SHALL NOT silently substitute another asset.

The Importer SHALL NOT determine whether the asset should be retried.

The Core determines whether another `ACQUIRE_ASSET` operation should be
issued for the same asset.

## 10.8 Registration Errors

If an asset cannot be registered successfully, the Importer SHALL NOT
report Registration Completion.

The Importer SHOULD report the condition using an appropriate operation
Result and CORE-004 message.

The Importer SHALL preserve the stable Source Order required for later
Registration recovery.

The Core remains the authoritative owner of the Registration Checkpoint
and determines when Registration may be resumed.

## 10.9 Unexpected Exceptions

The Importer implementation SHOULD catch and handle expected
source-specific exceptions at the appropriate level.

Unexpected exceptions SHALL NOT be silently ignored.

Where an unexpected exception prevents an operation from completing, the
Importer SHALL return a failed Result and SHOULD provide diagnostic
information sufficient to identify the failure.

The Importer SHOULD avoid exposing internal stack traces or other
implementation details directly to the user.

Detailed technical information MAY be recorded in application diagnostics
or logs according to the application's logging policy.

## 10.10 Diagnostic Logging

Importers SHOULD provide useful diagnostic information for significant
source operations and failures.

Diagnostic information MAY include:

- Importer identifier;
- operation being performed;
- Project Context, subject to application logging policy;
- asset identifier, where applicable;
- source identifier, subject to security and privacy requirements;
- error classification;
- exception information;
- source-specific diagnostic information; and
- recovery information.

Sensitive authentication information, credentials, access tokens and
other secrets SHALL NOT be written to diagnostic logs.

The Importer SHALL NOT rely on diagnostic logs as persistent project
recovery state.

Persistent recovery state remains the responsibility of the Core.

---

# 11. Resource Management

The Importer is responsible for managing all resources required to
communicate with its source system and perform an import operation.

Resources MAY include:

- Network connections.
- Authenticated sessions.
- Browser instances or browser profiles.
- Temporary files.
- Temporary directories.
- Source-specific processes.
- Source-specific caches.
- Memory or other runtime resources.
- Source-specific user interfaces.

The Importer SHALL manage these resources so that they do not
unnecessarily persist beyond the operation for which they are required.

## 11.1 Resource Ownership

Source-specific runtime resources are owned and managed by the Importer,
except where another Photo Manager component is explicitly responsible
for a resource through an interface defined by the applicable
specification.

The Core SHALL NOT be required to manage source-specific resources.

The Importer SHALL NOT require the Core to understand the internal
lifecycle of source-specific resources.

Source-specific user interfaces registered with the Core using
CORE-004 UI-REGISTRATION are an explicit exception to Importer-owned
resource lifecycle management. The Importer is responsible for creating
or launching such interfaces and registering them with the Core, but
their application-level lifecycle SHALL be managed by the Photo Manager
window-management infrastructure.

Photo Manager project state SHALL remain owned by the Core and SHALL NOT
be represented as Importer-managed runtime resources.

## 11.2 Resource Initialisation

The Importer SHALL initialise resources when they are required by the
current operation.

The Importer SHOULD avoid establishing expensive source connections or
allocating resources before they are required.

Resources that are not required during Importer Discovery SHALL NOT be
initialised as a consequence of discovery.

In particular, Importer Discovery SHALL NOT establish source-system
connections, authenticate users or enumerate source content.

## 11.3 Resource Lifetime

The lifetime of a resource SHOULD be limited to the period during which
the resource is required.

An Importer MAY retain source-specific configuration or authentication
information between import operations where appropriate.

Runtime connections, temporary files, temporary processes and other
operation-specific resources SHOULD NOT be retained unnecessarily after
the operation has completed.

The Importer SHALL NOT rely on an active source connection remaining
available between separate import operations.

## 11.4 Source Connections

The Importer SHALL manage source connections and authenticated sessions.

An Importer MAY maintain a source connection across multiple operations
within the same active import operation where this is appropriate.

The Importer SHALL be capable of re-establishing source communication
when a connection is unavailable.

Source connection state SHALL NOT be treated as persistent Photo Manager
project state.

If source communication is required during a recovery or acquisition
operation and no suitable connection exists, the Importer SHALL use the
source information supplied by the Core with the applicable control
operation to establish or restore source communication.

## 11.5 Temporary Files and Storage

The Importer MAY use temporary files or directories when required by the
source implementation.

Temporary storage SHOULD be located in an appropriate application
temporary area rather than within the Photo Manager project workspace
unless explicitly required by the Core API.

Temporary files SHOULD be removed when they are no longer required.

The Importer SHALL NOT use temporary storage as a substitute for
Core-owned persistent project state.

If an Importer must retain source-specific information between sessions,
that information SHALL remain separate from the Photo Manager project
unless explicitly defined by another specification.

## 11.6 External Processes

An Importer MAY launch source-specific external processes where required
by its implementation.

The Importer SHALL remain responsible for the lifecycle of such
processes unless the process, or a user interface provided by the
process, has been registered with the Core using CORE-004
UI-REGISTRATION.

External processes that remain Importer-owned SHOULD be terminated when
they are no longer required.

Where a source-specific external process provides a user interface that
has been registered with the Core using UI-REGISTRATION, the Importer
SHALL NOT terminate that interface solely as part of its normal resource
cleanup. The lifecycle of the registered user interface SHALL be managed
by the Photo Manager window-management infrastructure.

The Importer SHALL handle abnormal termination of source-specific
processes and SHALL report conditions that prevent the current operation
from completing.

The Importer SHALL NOT assume that an external process remains available
after an application restart.

## 11.7 Resource Failure

If a required resource cannot be created, opened or maintained, the
Importer SHALL report the resulting condition through the mechanisms
defined by the Core–Importer API Specification.

The Importer SHALL NOT report successful completion of an operation when
a required resource failure has prevented the operation from completing.

Where the resource failure can be resolved through user interaction, the
Importer SHOULD report an `ACTION_REQUIRED` condition where appropriate.

Where the failure prevents the operation from continuing, the Importer
SHALL return an appropriate failed Result.

## 11.8 Cancellation and Shutdown

The Importer SHALL release resources associated with the current import
operation when the operation is cancelled or completed.

Following `CANCEL`, the Importer SHALL release source-specific resources
at the next safe interruption point.

Shutdown SHALL release, as appropriate:

- source connections;
- authenticated sessions that are no longer required;
- temporary files;
- temporary directories;
- source-specific processes that remain under Importer ownership; and
- temporary caches.

Source-specific user interfaces registered with the Core using
CORE-004 UI-REGISTRATION SHALL NOT be released or terminated by the
Importer as part of normal cancellation or shutdown processing. Their
lifecycle SHALL be managed by the Photo Manager window-management
infrastructure.

The Importer MAY retain persistent source-specific configuration and
authentication information intended for future import operations.

The Importer SHALL NOT retain persistent project-specific recovery state.

## 11.9 Resource Cleanup After Failure

The Importer SHOULD ensure that resources are released even when an
operation terminates because of an error or unexpected exception.

Resource cleanup SHALL NOT depend solely on the normal successful
completion path.

An Importer SHOULD use implementation mechanisms that ensure cleanup is
performed when an operation exits abnormally.

The Importer SHALL avoid leaving orphaned source-specific processes,
temporary resources or active connections that remain under Importer
ownership after termination of an import operation.

Source-specific user interfaces registered with the Core using
CORE-004 UI-REGISTRATION SHALL NOT be treated as orphaned Importer
resources. Their lifecycle remains the responsibility of the Photo
Manager window-management infrastructure.

## 11.10 Security and Sensitive Resources

The Importer SHALL protect credentials, authentication tokens and other
sensitive source-specific information.

Sensitive information SHALL NOT be written to diagnostic logs.

Temporary files containing sensitive source information SHOULD be
protected appropriately and removed when no longer required.

The Importer SHALL NOT expose source credentials or authentication
information through the Core API unless explicitly required by the
applicable specification.

Source-specific security requirements remain the responsibility of the
Importer and the source implementation.

---

# 12. Implementation Requirements

The following requirements apply to Importer implementations.

- Source-specific behaviour SHALL remain within the Importer.
- Importers SHALL NOT depend on Core internal implementation details.
- Importers SHALL NOT access or modify `project.json` directly.
- Importers SHALL treat Project Context as an opaque Core-issued value.
- Importers SHALL maintain stable Source Order for Registration recovery.
- Importers SHALL use stable source identifiers for registered assets.
- Importers SHALL declare the Core API Version they support through
  Capability Information.
- Importers SHALL implement all mandatory interfaces and behaviours
  required by the supported Core API Version.
- Importers SHALL protect credentials, authentication tokens and other
  sensitive source information.
- Importers SHALL release source-specific resources when they are no
  longer required.
- Importers SHALL register source-specific user interfaces with the Core
  using CORE-004 UI-REGISTRATION when required.
- Importers SHALL be capable of recovering from loss of source
  connectivity where required by the Core–Importer API.
- Importers SHALL NOT rely on persistent project-specific state being
  retained by the Importer between import sessions.

The Importer Developer's Handbook provides additional implementation
guidance, recommended practices, examples and testing guidance.
