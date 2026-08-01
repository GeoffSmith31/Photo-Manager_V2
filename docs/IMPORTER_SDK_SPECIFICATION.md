# Photo Manager V2
# Importer SDK Specification

Document Status: Draft

Document Version: 1.0

Defines:

    Importer SDK Version 1

Normative References:

CORE_IMPORTER_API_SPECIFICATION.md   Version 1
PROJECT_JSON.md                      Version 2
SPECIFICATION_STYLE_GUIDE.md         Version 1.0

---

# 1. Purpose

This document defines the Software Development Kit (SDK) used to develop
Importer plugins for Photo Manager.

It provides implementation guidance for developers creating Importers
that communicate with the Photo Manager Core.

This document supplements the Core–Importer API Specification by
describing the expected structure, lifecycle and implementation of an
Importer.

It does not redefine the behaviour specified by the
CORE_IMPORTER_API_SPECIFICATION.md.

---

# 2. Scope

This specification applies to all Importers developed for Photo Manager.

It defines:

- Importer architecture.
- Importer lifecycle.
- Plugin structure.
- SDK interfaces.
- Recommended implementation practices.

This specification does not define:

- The Core API.
- Project JSON structures.
- Internal Core implementation.
- User interface design.

---

# 3. Architecture Overview

This section has been intentionally left blank.

---

# 4. Terminology

Terminology used throughout this document is defined by
SPECIFICATION_STYLE_GUIDE.md.

Additional terminology specific to the Importer SDK MAY be introduced in
future versions of this specification.

---

# 5. Design Principles

The Importer SDK has been designed according to the following
principles.

- Importers communicate with a single source system.
- Importers translate source-specific information into the canonical
  Photo Manager data model.
- Importers acquire assets; the Core owns persistent storage.
- Importers SHALL communicate with the Core exclusively through the
  Core–Importer API.
- Importers SHALL NOT modify `project.json` directly.
- Source-specific behaviour SHALL remain within the Importer.
- The SDK SHALL provide a stable foundation for future Importers.

The Importer SDK has been designed to support future extension through
additional SDK services and helper libraries.

# 6. Importer Responsibilities

The Importer is responsible for:

- Communicating with a single source system.
- Acquiring information from the source system.
- Translating source-specific information into the canonical Photo
  Manager data model.
- Creating and maintaining source-specific state required to communicate
  with the source system.
- Registering projects and assets using the Core–Importer API.
- Acquiring asset data from the source system.
- Reporting runtime status and operational events to the Core.
- Responding to commands issued by the Core.
- Managing any source-specific user interfaces required during an import
  operation.
- Releasing all source-specific resources upon completion or
  cancellation.

The Importer SHALL communicate with the Core exclusively through the
interfaces defined by CORE_IMPORTER_API_SPECIFICATION.md.

The Importer SHALL NOT directly modify `project.json`.

The Importer SHALL communicate with the Core exclusively through the
interfaces defined by CORE_IMPORTER_API_SPECIFICATION.md.

The Importer MAY maintain persistent source-specific configuration,
authentication information and other source state independent of any
Photo Manager project.

The Importer SHALL NOT directly modify `project.json`.

The Importer SHALL NOT maintain persistent project state.

The Importer SHALL NOT bypass validation or other services provided by
the Core.

# 7. Importer Lifecycle

An Importer progresses through a sequence of well-defined phases during
an import operation.

The exact internal implementation of these phases is implementation
dependent.

The behaviour observable by the Core SHALL comply with the
CORE_IMPORTER_API_SPECIFICATION.md.

A typical Importer lifecycle is illustrated below.

```text
                 Initialise
                      │
                      ▼
            Connect to Source
                      │
                      ▼
      Authenticate (if required)
                      │
                      ▼
      Select Source Content
      (if required)
                      │
                      ▼
     CORE-001 Create Project
                      │
                      ▼
        Enumerate Assets
                      │
                      ▼
 Register Assets (CORE-002)
                      │
                      ▼
         Wait for RESUME
                      │
                      ▼
         Acquire Assets
                      │
                      ▼
      Import Complete
                      │
                      ▼
           Shutdown
```

The Importer SHALL remain responsive to commands received through
IMPORTER-001 throughout the import operation.

The Importer MAY present source-specific user interfaces where required
to authenticate with, or obtain information from, the source system.

The Importer SHALL release all source-specific resources before
terminating.

=====================================================
PART II – SDK Interface
=====================================================

# 8. Importer Interface

Every Importer SHALL implement the interfaces defined by the Importer
SDK.

These interfaces define the interaction between the Core and an
Importer throughout the import lifecycle.

The implementation of these interfaces is language and platform
independent.

The Core SHALL interact with an Importer exclusively through these
interfaces.

The internal implementation of an Importer is outside the scope of this
specification.

## 8.1 Initialisation

The Importer SHALL provide an initialisation interface that prepares the
Importer for operation.

Initialisation MAY include:

- Loading source-specific configuration.
- Restoring source-specific authentication information.
- Establishing communication with the source system.
- Validating the runtime environment.
- Preparing any source-specific resources required during the import
  operation.

The Importer SHALL report any unrecoverable initialisation errors to the
Core using the communications interface defined by
CORE_IMPORTER_API_SPECIFICATION.md.

Successful initialisation SHALL prepare the Importer to commence an
import operation.

## 8.2 Configuration

The Importer MAY provide source-specific configuration options.

Configuration enables an Importer to customise its interaction with a
particular source system.

Typical configuration items include:

- Source-specific authentication information.
- Source-specific preferences.
- Selection of source-specific metadata.
- Priority rules used when translating source information into the
  canonical Photo Manager data model.
- Temporary storage locations.
- Performance-related options.

The Core SHALL NOT interpret or modify Importer-specific configuration.

The Importer SHALL apply its configuration consistently throughout an
import operation.

## 8.3 Workspace Discovery

The Workspace Discovery phase identifies the source to be imported and
gathers the Workspace Information required to create a new Photo Manager
project.

During this phase the Importer MAY:

- Authenticate the user with the source system.
- Present any source-specific user interface required to select the
  source.
- Discover source-specific workspace information.
- Determine suggested Metadata Policies appropriate to the selected
  source.

Upon completion of Workspace Discovery, the Importer SHALL invoke
CORE-001 Create Project.

The Importer SHALL NOT commence asset registration until the Core has
successfully created the project and returned a valid Project Context.

## 8.4 Registration Phase

During the Registration Phase, the Importer enumerates every asset
contained within the selected source.

For each asset discovered, the Importer SHALL:

- Determine a stable source-specific `asset_id`.
- Determine the appropriate `group_id`.
- Determine the most authoritative available `asset_time` in accordance
  with the Importer's configuration.
- Extract any available geographic information.
- Derive any suggested user metadata supported by the source.
- Construct the canonical Asset Information defined by the Core API.
- Invoke CORE-002 Register Asset.

The Importer SHALL register every asset before commencing the Asset
Transfer Phase.

The final asset registration SHALL indicate completion of the
Registration Phase by setting
`is_registration_complete = true`.

Following completion of the Registration Phase, the Importer SHALL wait
for a RESUME command specifying the `ACQUISITION` phase before
transferring any Asset Data.

The Registration Phase MAY be resumed following interruption by
receiving:

    RESUME(REGISTRATION, last_successful_asset)

The Importer SHALL recommence registration with the asset immediately
following the last successfully registered asset.

## 8.5 Asset Transfer Phase

During the Asset Transfer Phase, the Importer acquires the binary data
associated with previously registered assets and transfers that data to
the Core.

The Asset Transfer Phase SHALL NOT commence until:

- the Registration Phase has completed successfully; and
- the Core has issued a
  `RESUME(ACQUISITION, last_successful_asset)` command.

Upon receipt of a RESUME command for the ACQUISITION phase, the
Importer SHALL commence transferring assets beginning with the asset
immediately following the last successfully transferred asset.

For each asset transferred, the Importer SHALL:

- Acquire the Asset Data from the source system.
- Construct the canonical Asset Data defined by the Core API.
- Invoke CORE-003 Transfer Asset.
- Report any STATUS, WARNING or ERROR conditions using CORE-004 as
  appropriate.

The final asset transfer SHALL indicate completion of the Acquisition
Phase by setting:

    is_download_complete = true

If the Asset Transfer Phase is interrupted, the Importer SHALL suspend
processing at the next safe interruption point.

The Asset Transfer Phase MAY subsequently be resumed by receiving:

    RESUME(ACQUISITION, last_successful_asset)

The Importer SHALL recommence transferring assets with the asset
immediately following the last successfully transferred asset.

If acquisition of an individual asset fails, the Importer SHOULD report
the failure to the Core using a WARNING message and continue processing
subsequent assets where possible.

The Core MAY subsequently request acquisition of the failed asset using
the IMPORTER-001 RETRY command.

## 8.6 Shutdown

Upon completion of an import operation, or following receipt of a
CANCEL command, the Importer SHALL perform an orderly shutdown.

During shutdown, the Importer SHALL:

- Release any resources associated with the current import operation.
- Close any active connections to the source system.
- Terminate any source-specific user interface that is no longer
  required.
- Return to the idle state ready to accept a subsequent import
  operation.

The Importer SHOULD preserve any source-specific configuration required
to simplify future import operations.

Examples include:

- Authentication tokens.
- Browser profiles.
- API session information.
- User preferences.
- Source-specific configuration.

The Importer SHALL NOT retain any project-specific state following
shutdown.

Project state is owned exclusively by the Core and is maintained within
the project workspace.

Following shutdown, the Importer SHALL be capable of commencing a new
import operation without requiring reinitialisation of the application.

If shutdown occurs before completion of an import operation, the
Importer SHALL ensure that the Core can subsequently resume the
operation using the appropriate RESUME command defined by
IMPORTER-001.
