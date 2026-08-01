# ADR-001 – Project Workspace Model
Status

Accepted

Decision

Photo Manager SHALL support multiple project workspaces.

Only one project workspace MAY be active at any time.

Each project SHALL be stored in its own workspace directory.

Each workspace SHALL contain a standard project.json file that defines the persistent state of that project.

The Project Manager SHALL be responsible for creating, opening, closing and managing the active project workspace.

Rationale

Supporting multiple workspaces provides greater flexibility while preserving the simplicity of a single active project.

Typical use cases include:

Maintaining multiple independent photo collections.
Importing several Journi trips over time.
Archiving completed projects.
Backing up or moving individual projects.

Using a standard project.json filename within each workspace eliminates the need to rename project files while keeping each workspace self-contained.

Consequences
Startup no longer automatically resumes the previous project.
The user selects or creates a project before import or editing operations commence.
Resume processing occurs only after a project has been opened.
The Core–Importer API and Importer SDK require no modification.

# ADR-002 – Application Logging

The application maintains a single persistent diagnostic log.

Logging is controlled by configurable log levels.

In normal operation, only WARNING and ERROR messages are recorded.

During development or troubleshooting, INFO and DEBUG logging may be enabled.

Log entries identify the originating component and, where applicable, the active project.

# ADR-003 – Orchestrator-Centred Workflow

The Orchestrator coordinates all business operations between Core components.

Components SHALL NOT invoke business operations on other components directly.

Infrastructure services (such as logging) are configured during application startup and may be used directly by application components.

This separation prevents the Orchestrator from becoming an infrastructure bottleneck while ensuring it remains the single authority for application workflow and state transitions.
