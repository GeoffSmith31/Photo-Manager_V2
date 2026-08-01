# Photo Manager Project JSON Specification

Version: 2 (Draft)

Status: Draft

Last Updated: 2026-07-28

Normative References
    PM-STYLE  STYLE_GUIDE.md  Version 1.0

Informative References
    None.

## Key Outcomes

This revision introduces the following significant changes:

- Added `retry_count` to support automatic and user-initiated download retries.
- Added `registration_status` to the Project Object to track asset registration.
- Added `download_status` to the Project Object to track the initial download phase.
- Removed `is_last` from the Photo Object.
- Clarified the separation between asset registration and asset download.
---

## 1. Purpose

This document defines the structure, semantics and lifecycle of the
`project.json` file used by Photo Manager V2.

The `project.json` file is the authoritative description of a Photo
Manager project. It records project configuration, metadata policies,
workflow state and photo metadata independently of the original source
from which the project was created.

This specification is intentionally source-agnostic. It defines the
persistent data model used by the Core and does not describe the
implementation details of individual importers.

Normative Language

The key words MUST, MUST NOT, SHALL, SHALL NOT, SHOULD, SHOULD NOT 
and MAY in this specification are to be interpreted as described 
in RFC 2119.

---

## 1. Scope

This specification defines the structure and semantics of the Photo Manager
Project JSON file.

The Project JSON file is the authoritative representation of a Photo Manager
project and defines the data required to describe the project, imported
assets, metadata and processing state.

This specification supports a two-phase import model consisting of:

- Asset registration.
- Asset download.

The Project JSON file is implementation-independent and does not define user
interface behaviour, importer implementation details or Core API interfaces.

Normative behaviour for the Core API and Importer SDK is defined in their
respective specifications.

---

## 3. Design Goals

The `project.json` schema has been designed to satisfy the following
goals.

- Source independent.
- Human readable.
- Easily extensible.
- Backwards compatible wherever practical.
- Portable between operating systems.
- Independent of implementation language.
- Stable across future versions.

The schema should evolve by extending existing structures where
possible rather than replacing them.

## 4. Architectural Principles

The following principles define the philosophy underpinning the
Photo Manager V2 architecture. They provide the rationale for the
`project.json` schema and SHALL be considered normative for all
Core, Importer and Metadata Provider implementations.

### AP-001 The Core Owns the Project

Once a project has been created, the Photo Manager Core owns the
project and its associated `project.json` file.

The Core SHALL be solely responsible for:

- Creating projects.
- Maintaining `project.json`.
- Validating project data.
- Managing workflow state.
- Persisting user modifications.

No external component SHALL modify `project.json` directly.

---

### AP-002 Importers Provide Facts

Importers SHALL provide factual information obtained from the source
system.

Importers SHALL NOT implement project workflow, metadata propagation,
retry logic or validation.

Examples of importer-supplied facts include:

- source identifiers
- asset identifiers
- source grouping identifiers
- filenames
- GPS coordinates
- timestamps
- source metadata

---

### AP-003 Metadata Providers Suggest Values

Metadata Providers generate candidate metadata values.

Examples include:

- Reverse Geocoder
- Artificial Intelligence
- OCR
- Future Metadata Providers

Metadata Providers SHALL NOT modify user-owned metadata directly.

The Core SHALL determine which suggested values are accepted in
accordance with the Project Metadata Policies.

---

### AP-004 Users Own Editable Metadata

User-editable metadata belongs to the project owner.

Once modified by the user, editable metadata SHALL become the
authoritative value for that asset.

Automatic metadata generation SHALL NOT overwrite user-edited
values unless explicitly requested by the user.

---

### AP-005 Project Metadata Policies Control Behaviour

Project Metadata Policies determine:

- metadata propagation
- metadata provider priority
- default metadata values

These policies belong to the project and SHALL be stored within
`project.json`.

Importer recommendations are used only during workspace creation.

Once the project has been created, the user owns the Project Metadata
Policies.

---

### AP-006 Derived Fields are Core Managed

Fields derived from other project data SHALL be generated and
maintained exclusively by the Core.

Importers SHALL NOT calculate or modify derived fields.

Examples include:

- location_key

---

### AP-007 Preserve Compatibility

Existing schema fields and values SHOULD be preserved wherever
practical.

Existing fields MAY be assigned broader semantic meaning provided
backwards compatibility is maintained.

Schema evolution SHOULD favour extension rather than replacement.

## 5. Schema Rules

The following rules define the structure and interpretation of the
`project.json` schema.

### SR-001 Timestamp Format

All timestamps SHALL be stored using the ISO 8601 date/time format in
Coordinated Universal Time (UTC).

UTC timestamps SHALL include the trailing `Z` timezone designator.

Example:

```json
"created_at": "2026-07-27T13:42:18.315Z"
```

---

### SR-002 Schema Version

Every project SHALL contain a schema version number.

The schema version SHALL be used by the Core to determine compatibility
with future releases.

---

### SR-003 Field Ownership

Every field defined within this specification has a single owner.

Ownership determines which component is permitted to modify the field.

The recognised field owners are:

- Core
- Importer
- User
- Metadata Provider (via the Core)

Only the owning component SHALL modify a field.

---

### SR-004 Mutable and Immutable Fields

Every field SHALL be classified as either mutable or immutable.

Immutable fields are written once during project creation and SHALL NOT
be modified thereafter.

Mutable fields MAY be modified by their owning component during the
lifecycle of the project.

---

### SR-005 Mandatory and Optional Fields

Mandatory fields SHALL exist in every valid project.

Optional fields MAY be omitted when the corresponding information is
unavailable.

Importers SHALL NOT invent values solely to satisfy optional fields.

---

### SR-006 Derived Fields

Derived fields are generated by the Core from other project data.

Derived fields SHALL NOT be supplied or modified by importers.

---

### SR-007 User Metadata

User-editable metadata SHALL be initialised in accordance with the
Project Metadata Policies.

Once modified by the user, these values become authoritative and SHALL
NOT be automatically overwritten.

---

### SR-008 Project Metadata Policies

Project Metadata Policies SHALL be stored as part of the project.

These policies determine:

- Metadata propagation.
- Metadata provider priority.
- Default values.

Importer recommendations SHALL only be used during workspace creation.

---

### SR-009 Source Independence

The schema SHALL remain independent of any particular importer.

Field names inherited from earlier implementations MAY be retained for
compatibility, however their documented semantics SHALL remain
source-agnostic.

---

### SR-010 Forward Compatibility

The Core SHOULD ignore unknown fields when reading a project file,
provided the schema version is recognised.

This permits future schema extensions without breaking compatibility
with existing projects.

### 5.1 Terminology

The following terms are used throughout this specification.

| Term | Definition |
|------|------------|
| **Asset** | A single photograph or other media item represented within a Photo Manager project. |
| **Asset Download** | The process by which an Importer acquires the binary data for a previously registered asset and supplies it to the Core for persistent storage. |
| **Asset Registration** | The process by which an Importer discovers an asset and supplies its metadata to the Core, creating the corresponding Photo Object within the project. |
| **Core** | The Photo Manager application responsible for creating, managing and maintaining projects. |
| **Derived Field** | A field whose value is calculated by the Core from other project data rather than being supplied directly by the Importer or User. |
| **Download Phase** | The stage of an import during which the Importer transfers the binary data for registered assets to the Core. |
| **Group** | A logical collection of related assets within a project. The interpretation of a group is determined by the Importer (e.g. Journi Moment, filesystem folder, album). Groups are identified by `moment_id`. |
| **Importer** | A software component that acquires assets and source metadata from an external source and presents them to the Core using the Importer SDK. |
| **Metadata Policy** | A project-level rule that determines how metadata is propagated, prioritised and initialised within a project. |
| **Metadata Provider** | A software component that generates candidate metadata values for an asset (e.g. Reverse Geocoder, AI, OCR). Metadata Providers suggest values but do not directly modify user-owned metadata. |
| **Project** | The complete persistent representation of a Photo Manager import, including registered assets, metadata, configuration and processing state. |
| **Project Metadata** | Configuration information associated with the project as a whole, rather than an individual asset. |
| **Registration Phase** | The stage of an import during which the Importer discovers assets and registers their metadata with the Core. |
| **Source** | The external system or repository from which assets are imported (e.g. Journi, filesystem, Komoot). |
| **Source Metadata** | Information obtained directly from the Source and supplied to the Core by an Importer. |
| **User Metadata** | Metadata that is owned and maintained by the user, either entered manually or accepted from a Metadata Provider. Once edited by the user, it becomes the authoritative value. |
| **Workspace** | The directory structure and persistent files associated with a Photo Manager project, including `project.json` and imported assets. |

## 6. Overall Schema Structure

A Photo Manager project is represented by a single `project.json` file.

The schema is organised into three primary objects.

- **workspace** – Project-wide configuration and immutable source information.
- **metadata_policies** – Project-level rules governing metadata propagation and metadata provider priority.
- **photos** – An array containing one record for each managed asset.

The overall structure is shown below.

```json
{
    "workspace": {
        ...
    },

    "metadata_policies": {
        ...
    },

    "photos": [
        {
            ...
        }
    ]
}
```

The relationship between these objects is illustrated below.

```text
                    project.json
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   workspace     metadata_policies      photos[]
                                            │
                                            ▼
                                    photo record
```

### 6.1 Workspace

The **workspace** object contains information describing the project as
a whole.

The workspace stores project-wide configuration, source information and
persistent state that applies to the project rather than to individual
assets.

Typical information includes:

- schema version
- importer identification
- source identification
- project identifiers
- workspace configuration
- project metadata
- registration status
- download status

The Core owns the workspace object after successful project creation and
is responsible for maintaining its contents throughout the lifecycle of
the project.

---

### 6.2 Metadata Policies

The **metadata_policies** object defines how metadata is propagated and
resolved throughout the project.

Typical policies include:

- propagation rules
- metadata provider priority
- default values

Metadata Policies are initialised using recommendations supplied by the
Importer during workspace creation.

Once the project has been created, the user owns the Metadata Policies.

---

### 6.3 Photos

The **photos** array contains one record for every managed asset within
the project.

Each photo record contains four categories of information.

- Source metadata
- Core-managed workflow data
- User metadata
- Derived metadata

Each photo record is independent and SHALL completely describe the
current state of that asset.

The structure of the photo object is defined in Section 9.

## 7. Workspace Object

The **workspace** object contains information describing the project as
a whole.

It records the origin of the project, identifies the Importer used to
create it, defines the workspace in which the project is stored,
contains project-wide metadata and maintains the persistent state of the
project.

The workspace object is created by the Core during workspace creation.

Once created, ownership of individual fields is determined by the
definitions contained within this specification.

The workspace object SHALL contain exactly one instance within every
valid `project.json` file.

### 7.1 Responsibilities

The workspace object is responsible for storing:

- Project identification.
- Schema version information.
- Importer identification.
- Source identification.
- Workspace configuration.
- Project metadata.
- Project lifecycle state.

The workspace object SHALL NOT contain information specific to
individual assets.

Asset-specific metadata, processing state and binary asset references
SHALL be stored within the `photos` array.

Such information SHALL be stored within the `photos` array.

### 7.2 Ownership

The workspace object is initially created by the Core using information
supplied by the Importer.

Following workspace creation, the Core is responsible for maintaining
the integrity of the workspace object in accordance with this
specification.

Following project creation:

- Core-owned fields SHALL only be modified by the Core.
- User-owned fields MAY be modified by the user.
- Importer-owned fields SHALL remain immutable.

### 7.3 Workspace Object Overview

The current workspace object contains the following fields.

| Field | Owner | Mutable |
|--------|-------|----------|
| schema | Core | No |
| importer | Importer | No |
| source | Importer | No |
| source_id | Importer | No |
| source_title | Importer | No |
| registration_status | Core | Yes |
| download_status | Core | Yes |
| event | User | Yes |
| image_folder | Core | No |
| created_at | Core | No |

### 7.4 Workspace Field Definitions

The following sections define every field contained within the
`workspace` object.

Unless otherwise specified, all fields SHALL conform to the Schema Rules
defined in Section 5.

---

#### 7.4.1 `schema`

| Property | Value |
|----------|-------|
| **Purpose** | Identifies the version of the `project.json` schema. |
| **Owner** | Core |
| **Mutable** | No |
| **Mandatory** | Yes |
| **Data Type** | Integer |
| **Valid Values** | Positive integer. |
| **Used By** | Core |
| **Notes** | Used by the Core to determine compatibility with future schema versions. |

---

#### 7.4.2 `importer`

| Property | Value |
|----------|-------|
| **Purpose** | Identifies the Importer that created the project. |
| **Owner** | Importer |
| **Mutable** | No |
| **Mandatory** | Yes |
| **Data Type** | String |
| **Valid Values** | Any non-empty importer identifier recognised by the Core. |
| **Used By** | Core |
| **Notes** | Identifies the Importer responsible for creating the project. Enables the Core to select the correct Importer when resuming interrupted imports or performing other source-specific operations. |

---

#### 7.4.3 `source`

| Property | Value |
|----------|-------|
| **Purpose** | Identifies the external source from which the project was created. |
| **Owner** | Importer |
| **Mutable** | No |
| **Mandatory** | Yes |
| **Data Type** | String |
| **Valid Values** | Importer-defined string. |
| **Used By** | Core, Importer |
| **Notes** | The interpretation of this value is defined by the Importer. Examples include Journi, Filesystem and Komoot. The Core treats this value as an opaque identifier. |

---

#### 7.4.4 `source_id`

| Property | Value |
|----------|-------|
| **Purpose** | Identifies the source object from which the project was created. |
| **Owner** | Importer |
| **Mutable** | No |
| **Mandatory** | Yes |
| **Data Type** | String |
| **Valid Values** | Importer-defined identifier. |
| **Used By** | Core, Importer |
| **Notes** | Used primarily to resume interrupted imports or reconnect to the original source. The interpretation of this value is defined solely by the Importer. |

---

#### 7.4.5 `source_title`

| Property | Value |
|----------|-------|
| **Purpose** | Stores the human-readable title associated with `source_id`. |
| **Owner** | Importer |
| **Mutable** | No |
| **Mandatory** | Yes |
| **Data Type** | String |
| **Valid Values** | Any non-empty string supplied by the Importer. |
| **Used By** | User Interface |
| **Notes** | Intended for display purposes only. If the source does not provide a descriptive title, the Importer SHOULD use a suitable alternative, such as the `source_id`. |

---

#### 7.4.6 `registration_status`

| Property | Value |
|----------|-------|
| **Purpose** | Indicates the current state of asset registration for the project. |
| **Owner** | Core |
| **Mutable** | Yes |
| **Mandatory** | Yes |
| **Data Type** | String |
| **Valid Values** | `NOT_STARTED`, `IN_PROGRESS`, `COMPLETE` |
| **Used By** | Core, Importer, User Interface |
| **Notes** | Updated by the Core as assets are registered. The value SHALL transition from `NOT_STARTED` to `IN_PROGRESS` when the first asset is registered and to `COMPLETE` when the final `Register Asset` request is received with `is_registration_complete = true`. |

---

#### 7.4.7 `download_status`

| Property | Value |
|----------|-------|
| **Purpose** | Indicates the current state of the initial asset download phase for the project. |
| **Owner** | Core |
| **Mutable** | Yes |
| **Mandatory** | Yes |
| **Data Type** | String |
| **Valid Values** | `NOT_STARTED`, `IN_PROGRESS`, `COMPLETE` |
| **Used By** | Core, Importer, User Interface |
| **Notes** | Updated by the Core as asset data is successfully stored. The value SHALL transition from `NOT_STARTED` to `IN_PROGRESS` when the first asset is successfully stored and to `COMPLETE` when the final `Store Asset Data` request is received with `is_download_complete = true`. Completion of the download phase does not imply that every registered asset was downloaded successfully. |

---

#### 7.4.8 `event`

| Property | Value |
|----------|-------|
| **Purpose** | Stores the default event name for the project. |
| **Owner** | User |
| **Mutable** | Yes |
| **Mandatory** | Yes |
| **Data Type** | String |
| **Valid Values** | Any UTF-8 string. |
| **Used By** | Core, Editor |
| **Notes** | Used to initialise the `event` field for newly imported assets in accordance with the Project Metadata Policies. Individual photo records may subsequently contain different event values. |

---

#### 7.4.9 `image_folder`

| Property | Value |
|----------|-------|
| **Purpose** | Identifies the directory used by the Core to store project assets. |
| **Owner** | Core |
| **Mutable** | No |
| **Mandatory** | Yes |
| **Data Type** | String |
| **Valid Values** | Valid filesystem directory name. |
| **Used By** | Core |
| **Notes** | Created and validated by the Core during workspace creation. The Core SHALL ensure that the value is valid for the host filesystem and unique within the configured root directory. Importers SHALL NOT create or modify this value. |

---

#### 7.4.10 `created_at`

| Property | Value |
|----------|-------|
| **Purpose** | Records the date and time at which the project was created. |
| **Owner** | Core |
| **Mutable** | No |
| **Mandatory** | Yes |
| **Data Type** | ISO 8601 UTC Timestamp |
| **Valid Values** | `YYYY-MM-DDTHH:MM:SS.sssZ` |
| **Used By** | Core |
| **Notes** | Recorded once when the project is created. The value SHALL remain unchanged throughout the lifetime of the project. |

## 8. Metadata Policies Object

The `metadata_policies` object defines the rules governing the
initialisation, propagation and prioritisation of metadata within a
Photo Manager project.

Metadata Policies are project-wide configuration settings.

They determine how editable metadata is initialised for newly imported
assets and how candidate values supplied by Metadata Providers are
prioritised.

Metadata Policies are created by the Core during project creation using
recommendations supplied by the selected Importer.

Following project creation, Metadata Policies become part of the project
configuration and may be modified by the user.

---

### 8.1 Responsibilities

The `metadata_policies` object is responsible for defining:

- Metadata propagation.
- Provider priority.
- Default values.

Metadata Policies SHALL NOT contain photo-specific metadata.

---

### 8.2 Ownership

Metadata Policies are initially recommended by the Importer.

The Core stores the accepted policies within `project.json`.

Following project creation, Metadata Policies are owned by the user.

Importers SHALL NOT modify Metadata Policies after workspace creation.

---

### 8.3 Policy Categories

Each Metadata Policy consists of one or more of the following
components.

#### Propagation Policy

Defines how user-entered metadata is propagated to other assets within
the project.

Supported propagation modes are:

| Value | Description |
|--------|-------------|
| `event` | Apply the value to every asset within the project. |
| `group` | Apply the value only to assets sharing the same `moment_id`. |
| `location` | Apply the value only to assets sharing the same `location_key`. |
| `none` | Do not automatically propagate the value. |

The propagation modes define the scope over which user-entered metadata
is automatically applied. The Core determines the affected assets using
the appropriate project identifiers. For example, `group` uses
`moment_id`, while `location` uses `location_key`.

---

#### Provider Priority

Defines the order in which Metadata Providers are consulted when
initialising editable metadata.

The Core SHALL evaluate providers in the order specified by the policy.

The first provider returning a valid value SHALL be used.

---

#### Default Value

Defines the value assigned when no Metadata Provider supplies a valid
result.

The default value is specific to the metadata field.

Examples include:

- `"Unknown"`
- `""` (empty string)

---

### 8.4 Example

The example below illustrates a possible Metadata Policy object.

```json
"metadata_policies":
{
    "location":
    {
        "propagate": "location",

        "priority":
        [
            "user",
            "geocoder",
            "ai"
        ],

        "default": "Unknown"
    },

    "event":
    {
        "propagate": "event",

        "priority":
        [
            "user"
        ],

        "default": ""
    }
}
```

### 8.5 Metadata Policy Definitions

The following sections define the Metadata Policies currently supported
by Photo Manager.

Additional policies MAY be introduced in future schema versions without
affecting existing implementations.

---

#### 8.5.1 `event`

| Property | Value |
|----------|-------|
| **Purpose** | Defines how the `event` metadata field is initialised and propagated. |
| **Owner** | User |
| **Mutable** | Yes |
| **Mandatory** | Yes |
| **Data Type** | Object |
| **Valid Values** | See Sections 8.3 and 8.4. |
| **Used By** | Core, Editor |
| **Notes** | The Importer recommends the initial policy during workspace creation. The user may subsequently modify the policy at any time. |

---

#### 8.5.2 `year`

| Property | Value |
|----------|-------|
| **Purpose** | Defines how the `year` metadata field is initialised and propagated. |
| **Owner** | User |
| **Mutable** | Yes |
| **Mandatory** | Yes |
| **Data Type** | Object |
| **Valid Values** | See Sections 8.3 and 8.4. |
| **Used By** | Core, Editor |
| **Notes** | The `year` field represents a temporal reference. It is not restricted to calendar years and may contain any user-defined time reference appropriate to the project. |

---

#### 8.5.3 `location`

| Property | Value |
|----------|-------|
| **Purpose** | Defines how the `location` metadata field is initialised and propagated. |
| **Owner** | User |
| **Mutable** | Yes |
| **Mandatory** | Yes |
| **Data Type** | Object |
| **Valid Values** | See Sections 8.3 and 8.4. |
| **Used By** | Core, Editor |
| **Notes** | The `location` policy commonly uses the `location` propagation mode, allowing user edits to be applied to all assets sharing the same `location_key`. |

---

#### 8.5.4 `info`

| Property | Value |
|----------|-------|
| **Purpose** | Defines how the `info` metadata field is initialised and propagated. |
| **Owner** | User |
| **Mutable** | Yes |
| **Mandatory** | Yes |
| **Data Type** | Object |
| **Valid Values** | See Sections 8.3 and 8.4. |
| **Used By** | Core, Editor |
| **Notes** | Supports user-entered descriptions, inherited values and future Metadata Provider suggestions, such as AI-generated captions. |

## 9. Photo Object

The `photos` array contains one object for every asset managed by the
project.

Each object represents the complete persistent state of a single asset
throughout its lifecycle, from asset registration through asset
download and subsequent metadata editing.

The Photo Object is the primary working record used by the Core.

It combines source metadata supplied by the Importer, asset workflow
information maintained by the Core, derived metadata generated by the
Core and editable metadata owned by the user.

Each Photo Object SHALL describe one asset only.

No information relating to another asset SHALL be stored within the
object.

---

### 9.1 Responsibilities

The Photo Object is responsible for storing:

- Source metadata.
- Asset workflow state.
- Derived metadata.
- User metadata.
- References to the associated binary asset.

The Photo Object SHALL NOT contain project-wide configuration.

Workspace-wide information SHALL be stored within the `workspace`
object.

Workspace-wide editing behaviour SHALL be stored within the
`metadata_policies` object.

---

### 9.2 Ownership

Individual fields within the Photo Object have different owners.

Ownership determines which component is permitted to modify each field.

The recognised owners are:

- Importer
- Core
- User

Metadata Providers do not directly modify Photo Objects.

Instead, Metadata Providers return candidate values to the Core, which
updates user metadata in accordance with the Project Metadata Policies.

---

### 9.3 Photo Object Overview

The current Photo Object contains the following fields.

| Field | Type | Owner | Mutable |
|-------|------|-------|----------|
| guid | String | Importer | No |
| moment_id | String | Importer | No |
| lat | Float | Importer | No |
| lng | Float | Importer | No |
| file | String | Core | No |
| downloaded | Boolean | Core | Yes |
| retry_count | Integer | Core | Yes |
| status | String | Core | Yes |
| exif_written | Boolean | Core | Yes |
| last_updated | Timestamp | Core | Yes |
| location_key | String | Core | No |
| geo_location | String | Core | Yes |
| event | String | User | Yes |
| year | String | User | Yes |
| location | String | User | Yes |
| info | String | User | Yes |

### 9.4 Photo Field Definitions

The following sections define every field contained within the Photo
Object.

Unless otherwise specified, all fields SHALL conform to the Schema Rules
defined in Section 5.

---

#### 9.4.1 `guid`

| Property | Value |
|----------|-------|
| **Purpose** | Identifies the asset within the originating source. |
| **Owner** | Importer |
| **Mutable** | No |
| **Mandatory** | Yes |
| **Data Type** | String |
| **Valid Values** | Importer-defined identifier. |
| **Used By** | Importer, Core |
| **Notes** | The `guid` uniquely identifies the asset within the originating source. The interpretation of the value is defined solely by the Importer. In some sources the `guid` may identify the original image, while in others it may identify a group of related image files representing different resolutions of the same asset. The Core treats this value as an opaque identifier and SHALL NOT attempt to interpret its format or meaning. |

---

#### 9.4.2 `moment_id`

| Property | Value |
|----------|-------|
| **Purpose** | Identifies the logical group to which the asset belongs within the originating source. |
| **Owner** | Importer |
| **Mutable** | No |
| **Mandatory** | Yes |
| **Data Type** | String |
| **Valid Values** | Importer-defined identifier. |
| **Used By** | Importer, Core |
| **Notes** | The `moment_id` identifies a logical grouping of related assets within the originating source. The interpretation of the grouping is defined by the Importer and is treated as an opaque identifier by the Core. Examples include a Journi Moment, a filesystem folder, a Komoot Highlight or any other importer-defined grouping. The Core uses `moment_id` when applying Project Metadata Policies that operate on groups of assets. Importers that do not naturally group assets SHALL assign all assets within the project to a single group. |

---

#### 9.4.3 `lat`

| Property | Value |
|----------|-------|
| **Purpose** | Stores the latitude associated with the asset. |
| **Owner** | Importer |
| **Mutable** | No |
| **Mandatory** | No |
| **Data Type** | Float |
| **Valid Values** | Decimal latitude in degrees. |
| **Used By** | Core |
| **Notes** | This field is optional because not all import sources provide geographic coordinates. When present, the value is supplied by the Importer and SHALL be preserved by the Core without modification. |

---

#### 9.4.4 `lng`

| Property | Value |
|----------|-------|
| **Purpose** | Stores the longitude associated with the asset. |
| **Owner** | Importer |
| **Mutable** | No |
| **Mandatory** | No |
| **Data Type** | Float |
| **Valid Values** | Decimal longitude in degrees. |
| **Used By** | Core |
| **Notes** | This field is optional because not all import sources provide geographic coordinates. When present, the value is supplied by the Importer and SHALL be preserved by the Core without modification. |

---

#### 9.4.5 `file`

| Property | Value |
|----------|-------|
| **Purpose** | Identifies the filename under which the asset is stored within the project workspace. |
| **Owner** | Core |
| **Mutable** | No |
| **Mandatory** | Yes |
| **Data Type** | String |
| **Valid Values** | Valid filename for the host filesystem. |
| **Used By** | Core |
| **Notes** | The Importer may recommend a filename when registering an asset with the Core. The Core SHALL validate the filename, ensure it is unique within the project and store the asset using the validated filename. The filename recorded in `project.json` SHALL be the actual filename used within the project workspace. |

---

#### 9.4.6 `downloaded`

| Property | Value |
|----------|-------|
| **Purpose** | Indicates whether the asset has been successfully downloaded and stored within the project workspace. |
| **Owner** | Core |
| **Mutable** | Yes |
| **Mandatory** | Yes |
| **Data Type** | Boolean |
| **Valid Values** | `true`, `false` |
| **Used By** | Core |
| **Notes** | Initially set to `false` when the Photo Object is created. The Core SHALL set this field to `true` only after the asset has been successfully written to the project workspace. This field records only the download state of the asset and SHALL NOT be used to indicate processing or editing status. |

---

#### 9.4.7 `retry_count`

| Property | Value |
|----------|-------|
| **Purpose** | Records the number of retry attempts made for this asset following the initial download failure. |
| **Owner** | Core |
| **Mutable** | Yes |
| **Mandatory** | Yes |
| **Data Type** | Integer |
| **Valid Values** | Integer ≥ 0 |
| **Used By** | Core |
| **Notes** | Initialised to `0` when the Photo Object is created. Incremented by the Core after each unsuccessful retry attempt. This field records retry history only. The interpretation of this value is defined by the Core implementation. |

---

#### 9.4.8 `status`

| Property | Value |
|----------|-------|
| **Purpose** | Records the current workflow state of the asset within the project. |
| **Owner** | Core |
| **Mutable** | Yes |
| **Mandatory** | Yes |
| **Data Type** | String |
| **Valid Values** | Core-defined workflow state, including `pending`, `downloaded` and `complete`. |
| **Used By** | Core |
| **Notes** | The Core defines the workflow states used by the application. Additional workflow states MAY be introduced in future schema versions without affecting the interpretation of this field. |

#### 9.4.9 `exif_written`

| Property | Value |
|----------|-------|
| **Purpose** | Indicates whether the asset's editable metadata has been successfully written to its EXIF data. |
| **Owner** | Core |
| **Mutable** | Yes |
| **Mandatory** | Yes |
| **Data Type** | Boolean |
| **Valid Values** | `true`, `false` |
| **Used By** | Core |
| **Notes** | Initialised to `false` when the Photo Object is created. The Core SHALL set this field to `true` only after successfully writing the asset's metadata to the image file. If EXIF writing fails, this field SHALL remain `false`. Any associated error information is outside the scope of this schema and SHOULD be recorded by the Core using an appropriate logging mechanism. |

---

#### 9.4.10 `last_updated`

| Property | Value |
|----------|-------|
| **Purpose** | Records the date and time the Photo Object was last modified. |
| **Owner** | Core |
| **Mutable** | Yes |
| **Mandatory** | Yes |
| **Data Type** | ISO 8601 UTC Timestamp |
| **Valid Values** | `YYYY-MM-DDTHH:MM:SS.sssZ` |
| **Used By** | Core |
| **Notes** | The Core SHALL update this field whenever any field within the Photo Object is modified. The timestamp SHALL be recorded in Coordinated Universal Time (UTC) and SHALL include the trailing `Z` timezone designator. |

---

#### 9.4.11 `location_key`

| Property | Value |
|----------|-------|
| **Purpose** | Identifies a logical geographic location shared by one or more assets within the project. |
| **Owner** | Core |
| **Mutable** | No |
| **Mandatory** | No |
| **Data Type** | String |
| **Valid Values** | Core-generated identifier. |
| **Used By** | Core |
| **Notes** | This field is derived by the Core from the asset's geographic coordinates. Assets determined to represent the same location SHALL be assigned the same `location_key`. The format and generation of this identifier are implementation-defined and are outside the scope of this specification. This field is optional because it cannot be generated when geographic coordinates are unavailable. |

---

#### 9.4.12 `geo_location`

| Property | Value |
|----------|-------|
| **Purpose** | Stores the suggested geographic description associated with the asset. |
| **Owner** | Core |
| **Mutable** | Yes |
| **Mandatory** | No |
| **Data Type** | String |
| **Valid Values** | Any UTF-8 string. |
| **Used By** | Core, Editor |
| **Notes** | This field contains the best geographic description available from the configured Metadata Providers. Sources may include reverse geocoding, artificial intelligence or future Metadata Providers. The value is intended to assist the user when assigning the final `location` metadata and SHOULD NOT be considered authoritative. The user MAY modify or replace this value at any time. |

---

#### 9.4.13 `event`

| Property | Value |
|----------|-------|
| **Purpose** | Stores the user-defined event associated with the asset. |
| **Owner** | User |
| **Mutable** | Yes |
| **Mandatory** | Yes |
| **Data Type** | String |
| **Valid Values** | Any UTF-8 string. |
| **Used By** | Core, Editor |
| **Notes** | This field is initialised in accordance with the Project Metadata Policies. Once modified by the user, it becomes the authoritative event associated with the asset. Individual assets within the same project MAY contain different event values. |

---

#### 9.4.14 `year`

| Property | Value |
|----------|-------|
| **Purpose** | Stores the user-defined temporal reference associated with the asset. |
| **Owner** | User |
| **Mutable** | Yes |
| **Mandatory** | Yes |
| **Data Type** | String |
| **Valid Values** | Any UTF-8 string. |
| **Used By** | Core, Editor |
| **Notes** | This field is initialised in accordance with the Project Metadata Policies. Once modified by the user, it becomes the authoritative temporal reference associated with the asset. Although the field is named `year` for compatibility with earlier schema versions, it MAY contain any user-defined temporal reference appropriate to the project. |

---

#### 9.4.15 `location`

| Property | Value |
|----------|-------|
| **Purpose** | Stores the user-defined geographic location associated with the asset. |
| **Owner** | User |
| **Mutable** | Yes |
| **Mandatory** | Yes |
| **Data Type** | String |
| **Valid Values** | Any UTF-8 string. |
| **Used By** | Core, Editor |
| **Notes** | This field is initialised in accordance with the Project Metadata Policies. Initial values MAY be supplied by one or more Metadata Providers. Once modified by the user, this field becomes the authoritative geographic location associated with the asset. |

---

#### 9.4.16 `info`

| Property | Value |
|----------|-------|
| **Purpose** | Stores the user-defined descriptive information associated with the asset. |
| **Owner** | User |
| **Mutable** | Yes |
| **Mandatory** | Yes |
| **Data Type** | String |
| **Valid Values** | Any UTF-8 string. |
| **Used By** | Core, Editor |
| **Notes** | This field is initialised in accordance with the Project Metadata Policies. Initial values MAY be supplied by one or more Metadata Providers. Once modified by the user, this field becomes the authoritative description associated with the asset. |

## 10. Version Compatibility

The `schema` field identifies the version of the `project.json`
specification used by a project.

Implementations SHALL use this value to determine compatibility with the
stored project.

Future schema versions SHOULD preserve backward compatibility wherever
practical.

Where incompatibilities cannot be avoided, the Core SHOULD provide an
appropriate migration mechanism.

Importers SHALL NOT assume a particular schema version unless explicitly
supported.

## 11. Future Extensions

The `project.json` schema is intended to evolve over time.

Future versions MAY introduce:

- Additional Metadata Policies.
- Additional workflow states.
- Additional Photo Object fields.
- Additional Workspace fields.

New fields SHOULD be optional wherever practical to preserve backward
compatibility.

Existing field semantics SHOULD NOT be changed without incrementing the
schema version.

## 12. Change History

| Version | Date | Description |
|---------|------|-------------|
| 2.0 Draft | 2026-07-28 | Initial draft of the Photo Manager schema specification, including the two-phase import architecture, Workspace lifecycle state, and reorganised Photo Object structure. |

# Appendix A – Example `project.json`

The following example illustrates the structure of a typical
`project.json` file.

The example is provided for illustrative purposes only and does not
define additional requirements beyond those specified elsewhere in this
document.

```json
{
    "workspace":
    {
        "schema": 2,
        "importer": "journi",
        "source": "Journi",
        "source_id": "trip_123456789",
        "source_title": "European Holiday 2025",

        "registration_status": "COMPLETE",
        "download_status": "IN_PROGRESS",

        "event": "European Holiday",

        "image_folder": "European_Holiday",

        "created_at": "2026-07-27T08:45:13.127Z"
    },

    "metadata_policies":
    {
        "event":
        {
            "propagate": "event",
            "priority": ["user"],
            "default": ""
        },

        "year":
        {
            "propagate": "group",
            "priority": ["user", "importer"],
            "default": ""
        },

        "location":
        {
            "propagate": "location",
            "priority": ["user", "geocoder", "ai"],
            "default": "Unknown"
        },

        "info":
        {
            "propagate": "group",
            "priority": ["user", "ai"],
            "default": ""
        }
    },

    "photos":
    [
        {
            "guid": "2a17e58d",

            "moment_id": "moment_001",

            "lat": 48.85826,
            "lng": 2.29450,

            "file": "IMG0001.jpg",
            "downloaded": true,
            "retry_count": 0,
            "status": "complete",
            "exif_written": true,
            "last_updated": "2026-07-27T09:14:52.003Z",

            "location_key": "LOC00017",
            "geo_location": "Eiffel Tower, Paris, France",

            "event": "European Holiday",
            "year": "2025",
            "location": "Eiffel Tower",
            "info": "View from the south-east lawn."
        }
    ]
}
```
# Appendix B – Design Principles

The `project.json` schema has been designed in accordance with the
following principles.

## B.1 Separation of Responsibilities

Each field has a single owner.

The Importer supplies source metadata.

The Core manages project state.

The User owns editable metadata.

---

## B.2 Source Agnostic Design

The schema represents concepts rather than implementation details.

Fields such as `moment_id`, `guid` and `source_id` are defined by their
purpose rather than by any particular Importer.

---

## B.3 Immutable Source Metadata

Metadata obtained directly from the originating source is preserved.

The Core SHALL NOT modify source metadata after workspace creation.

---

## B.4 User Authority

Suggested metadata provided by Metadata Providers is advisory only.

Once modified by the user, editable metadata becomes authoritative.

---

## B.5 Core Ownership

The Core is responsible for maintaining all project workflow state,
including download progress, processing status and derived metadata.

---

## B.6 Extensibility

The schema is intended to support future Importers, Metadata Providers
and application features without requiring fundamental structural
changes.

---

## B.7 Backward Compatibility

Existing field names and semantics SHOULD be preserved wherever practical.

Where schema changes are required, compatibility SHOULD be maintained
through explicit schema versioning and migration.

---

## B.8 Data Before Behaviour

This specification defines the structure and meaning of stored data.

Algorithms, user interface behaviour and application workflows are
defined by the Core implementation and are outside the scope of this
document.

