# Journi-Downloader

## Overview

Journi-Downloader is a desktop application for downloading photographs from Journi travel journals and building a permanent, searchable local photo archive.

The application downloads media directly from Journi, organises it into a project, and allows the user to review and enrich each photograph with meaningful metadata before writing that information into the image itself.

The goal is to create a self-contained photo collection that remains useful long after the original Journi journal is no longer available.

---

## Current Features

* Authenticate with Journi using a browser session.
* Import a Journi trip into a project.
* Download photographs from Journi.
* Resume interrupted downloads safely.
* Skip files that have already been downloaded.
* Maintain project progress in a single `project.json` file.
* Review and edit photo metadata.
* Write metadata directly into each image's EXIF information.
* Cache reverse geocoding results to improve performance.

---

## Project Philosophy

The project is guided by a number of core principles.

* `project.json` is the single source of truth for all project state.
* Download operations must be safe to resume at any time.
* User changes are written to the project as they are made, allowing interrupted work to be resumed safely.
* The backend is independent of the user interface.
* The user interface can evolve without requiring major backend changes.
* Simplicity and maintainability are preferred over unnecessary complexity.

---

## Current User Interface

The application currently provides a web-based user interface.

The web UI communicates with a backend that manages project creation, downloading, metadata processing and project state. The backend has been designed to remain independent of the user interface so that future enhancements can be made without significant architectural changes.

---

## Documentation

Additional project documentation is located in the `docs/` directory.

| Document         | Purpose                                   |
| ---------------- | ----------------------------------------- |
| START_HERE.md    | Quick start guide                         |
| PROJECT_GUIDE.md | Architecture and developer guide          |
| CURRENT_STATE.md | Current implementation status             |
| TODO.md          | Outstanding development tasks             |
| ROADMAP.md       | Planned future development                |
| DECISIONS.md     | Architectural decisions                   |
| SESSION_LOG.md   | Development history                       |
| PARKING_LOT.md   | Deferred ideas                            |
| AI_NOTES.md      | Notes relating to AI-assisted development |

---

## Current Status

Journi-Downloader is under active development.

The core backend architecture is now in place and is accessed through a web-based user interface. Development is currently focused on expanding functionality, refining the user workflow and completing the remaining project features.

---

## Requirements

* Python 3.11 or later
* Playwright
* Valid Journi account
* Internet connection during download operations

---

## Getting Started

1. Read `START_HERE.md`.
2. Review `PROJECT_GUIDE.md` for an overview of the architecture.
3. Check `CURRENT_STATE.md` to understand the current implementation.
4. Review `TODO.md` for planned development work.

---

## Project Status

This project is being developed incrementally, with an emphasis on maintainability, recoverability and clear documentation.

New functionality is introduced through small, well-tested changes while keeping the project documentation synchronised with the implementation.

