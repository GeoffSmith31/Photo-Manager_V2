# Photo Manager – Technical Documentation

This directory contains the technical specifications, design documentation and developer guidance for Photo Manager.

The documents are intended for developers maintaining Photo Manager and developers creating standalone Importers that produce projects for use with Photo Manager.

## Project Format

### Photo Manager Project JSON Reference

**Document Version:** 1.0
**Project JSON Schema:** Version 2

The authoritative specification for the structure and contents of `project.json`. It defines the required fields, data types, permitted values and constraints for Photo Manager projects.

- [Read or download the PDF](Photo-Manager_Project-JSON-Reference.pdf)
- [Download the editable ODT document](Photo-Manager_Project-JSON-Reference.odt)

## Importer Development

### Importer Developer's Handbook

**Document Version:** 1.0
**Status:** In preparation

Practical guidance for developers creating standalone Importers for Photo Manager. The Handbook covers project structure, asset acquisition, project data construction, validation, publication and integration with Photo Manager.

- [Download the editable ODT document](Importer_Developers_Handbook.odt)
- [Download the PDF](Importer-Developers-Handbook-v1.0.pdf)

The PDF edition will be published when the Handbook is complete.

## Application Design

### Photo Manager Core Design Specification

**Document Version:** 1.3
**Status:** Draft

Describes the internal architecture and design of the Photo Manager Application. It provides useful context for developers, including the responsibilities of the Project Manager, project discovery, loading and validation.

[Read the Core Design Specification](CORE_DESIGN_SPECIFICATION_V1.3.md)

### Architecture Decision Register

Records significant architectural decisions made during the development of Photo Manager.

[Read the Architecture Decision Register](ARCHITECTURE_DECISION_REGISTER.md)

### Core Design Notes

Working notes associated with the design and development of Photo Manager.

[Read the Core Design Notes](CORE_DESIGN_NOTES.txt)

## Supporting Documentation

### Specification Style Guide

Defines the conventions used when preparing technical specifications for Photo Manager.

[Read the Specification Style Guide](SPECIFICATION_STYLE_GUIDE.md)

### Propagation

Supporting documentation describing the metadata propagation behaviour used by Photo Manager.

[Download the Propagation document](Propagation.odt)

---

**Document status and version control**

Document versions and status are identified within each document. Where requirements for the project data format are concerned, the applicable Photo Manager Project JSON Reference is authoritative.

This documentation evolves alongside Photo Manager. Developers should ensure that they consult the versions applicable to the Photo Manager release they are targeting.
