## ADDED Requirements

### Requirement: Four-layer content directory structure
The documentation SHALL organize content into four directories under `docs/`: `tutorials/`, `notes/`, `examples/`, and `api/`, each with an `index.rst` file as the toctree entry point.

#### Scenario: Directory structure exists
- **WHEN** developer inspects the `docs/` directory
- **THEN** the subdirectories `tutorials/`, `notes/`, `examples/`, and `api/` exist, each containing an `index.rst`

### Requirement: Root documentation index
The `docs/index.rst` SHALL serve as the top-level toctree entry that links to the four content layer index pages (tutorials, notes, examples, api).

#### Scenario: Navigate from root to content layers
- **WHEN** developer opens the built documentation homepage
- **THEN** the page displays navigation links to Tutorials, Notes, Examples, and API Reference sections

### Requirement: Placeholder content in each layer
Each content layer's `index.rst` SHALL contain a descriptive title and placeholder text indicating the layer's purpose, ready for future content to be added.

#### Scenario: Tutorials index shows purpose
- **WHEN** developer opens the Tutorials section in built documentation
- **THEN** the page displays a title "Tutorials" and placeholder text describing the section's intended purpose

#### Scenario: Notes index shows purpose
- **WHEN** developer opens the Notes section in built documentation
- **THEN** the page displays a title "Notes" and placeholder text describing design philosophy and internal mechanics documentation

### Requirement: API Reference autodoc entry
The `docs/api/` directory SHALL contain an `pyleaf.rst` file with an `.. automodule:: pyleaf` directive that serves as the autodoc entry point for generating API documentation from Python docstrings.

#### Scenario: API page reflects current module state
- **WHEN** the `pyleaf` Python package has modules with docstrings
- **THEN** the built API Reference page lists those modules and their documented members