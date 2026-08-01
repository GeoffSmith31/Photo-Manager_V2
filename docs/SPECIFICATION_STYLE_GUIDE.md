# Photo Manager V2
# Specification Style Guide

**Document Version:** 1.0 Draft

---

# 1. Purpose

This document defines the writing conventions used throughout the Photo
Manager V2 technical specifications.

The purpose of this guide is to ensure all specifications present
information consistently, making them easier to read, maintain and
implement.

All technical specifications SHOULD conform to this guide.

---

# 2. General Principles

Documentation SHALL:

- Be clear.
- Be concise.
- Be technically accurate.
- Be implementation independent where practical.
- Describe data and interfaces rather than algorithms.

Documentation SHOULD:

- Use consistent terminology.
- Avoid ambiguity.
- Minimise repetition.
- Preserve backward compatibility where appropriate.

---

# 3. Terminology

The following terms SHALL be used consistently throughout the
documentation.

| Preferred | Notes |
|-----------|-------|
| Core | The Photo Manager Core application. |
| Importer | A plug-in responsible for importing assets from an external source. |
| Metadata Provider | A component that supplies candidate metadata values. |
| User | The owner of editable metadata. |
| Asset | A managed photograph or image. |
| Project | A Photo Manager project. |
| Workspace | The project workspace described by the Workspace Object. |
| Photo Object | A single asset record within the `photos` array. |
| Project Metadata Policies | Project-wide metadata behaviour configuration. |

Avoid source-specific terminology unless discussing a specific Importer.

---

# 4. Capitalisation

Always capitalise:

- Core
- Importer
- Metadata Provider
- Project
- Workspace
- Photo Object

Do not capitalise:

- project.json
- workspace object
- photo object
- metadata field

---

# 5. Normative Language

The following words SHALL be used in accordance with RFC 2119.

- SHALL
- SHALL NOT
- SHOULD
- SHOULD NOT
- MAY
- MUST
- MUST NOT

These words SHALL always appear in upper case.

---

# 6. Field References

JSON field names SHALL be written using inline code formatting.

Example:

`event`

`location_key`

`moment_id`

---

# 7. Object References

JSON object names SHALL be written using inline code formatting.

Example:

`workspace`

`photos`

`metadata_policies`

---

# 8. Filenames

Filenames SHALL be written using inline code formatting.

Example:

`project.json`

`PROJECT_JSON.md`

---

# 9. Section Structure

Major objects SHOULD follow the same structure.

Example:

Overview

Responsibilities

Ownership

Object Overview

Field Definitions

---

# 10. Field Definitions

Every field definition SHALL use the following structure.

| Property | Value |
|----------|-------|
| Purpose | |
| Owner | |
| Mutable | |
| Mandatory | |
| Data Type | |
| Valid Values | |
| Used By | |
| Notes | |

Properties SHALL appear in this order.

---

# 11. Field Ordering

Field definitions SHALL appear in the same order as the corresponding
Object Overview.

The Object Overview SHALL match the ordering used by `project.json`.

---

# 12. Examples

JSON examples SHALL:

- Be syntactically correct.
- Be internally consistent.
- Illustrate recommended usage.
- Avoid unnecessary complexity.

---

# 13. Dates and Times

Timestamp fields SHALL use ISO 8601 UTC format.

Example:

`2026-07-27T08:45:13.127Z`

---

# 14. Ownership

Ownership describes which component is permitted to modify a field.

Ownership SHALL NOT be confused with the source of information used to
populate that field.

Example:

The Importer supplies `is_last`.

The Core owns `is_last`.

---

# 15. Writing Style

Specifications SHOULD:

- Use active voice.
- Prefer short sentences.
- Describe purpose before implementation.
- State facts rather than opinions.
- Avoid implementation-specific algorithms unless required.

Specifications SHOULD NOT:

- Describe user interface behaviour.
- Describe implementation algorithms.
- Duplicate information unnecessarily.
- Introduce undocumented terminology.

---

# 16. Design Philosophy

Specifications should document:

- What information is stored.
- What the information means.
- Who owns the information.
- Any constraints placed upon the information.

Specifications should not document:

- How the application implements the feature.
- User interface behaviour.
- Internal algorithms.
- Performance optimisations.

These topics belong in implementation or architecture documents.

# 17. Preserve Existing Field Names

Existing field names SHOULD be retained wherever practical.

Where the meaning of a field evolves, preference SHOULD be given to
broadening its documented semantics rather than introducing a new field
or renaming an existing one.

Examples include:

- `moment_id`
- `year`
- `source`

This approach improves backward compatibility and reduces migration
requirements.

# 18. Section Number Stability

Section numbers form part of the public interface of the specification.

Once a specification reaches Version 1.0, section numbering SHALL remain
stable across subsequent revisions wherever practical.

Where a section becomes obsolete, its section number SHALL be retained.

The obsolete section SHOULD be replaced with an appropriate note such as:

> This section is intentionally left blank.  

If a section becomes redundant during drafting, retain the section number and explain why it is intentionally blank.

or

> This section has been deprecated.

Future specifications SHALL NOT renumber subsequent sections solely to
remove obsolete material.

This policy preserves stable references between specifications,
implementation documentation and external documents.

# 19. Specification Dependencies

Each specification SHALL identify the versions of all related
specifications upon which it depends.

Cross-references SHALL include both the document name and the applicable
document version.

Example:

PROJECT_JSON.md Version 1.0

CORE_API_SPECIFICATION.md Version 1.0

IMPORTER_SDK_SPECIFICATION.md Version 1.0

SPECIFICATION_STYLE_GUIDE.md Version 1.0

Implementations SHALL identify the specification versions with which they
are compliant.
