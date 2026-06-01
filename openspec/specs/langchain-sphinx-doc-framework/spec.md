## ADDED Requirements

### Requirement: Sphinx project initialization
The system SHALL provide a Sphinx documentation project under `docs/` directory that can be built locally with `make html` and previewed in a browser.

#### Scenario: Build documentation locally
- **WHEN** developer runs `make html` in the `docs/` directory
- **THEN** Sphinx generates HTML output in `docs/_build/html/` that can be opened in a browser

#### Scenario: Clean build output
- **WHEN** developer runs `make clean` in the `docs/` directory
- **THEN** the `docs/_build/` directory is removed

### Requirement: PyTorch-style Sphinx theme
The documentation SHALL use `sphinx-book-theme` as the Sphinx HTML theme, configured with left-sidebar navigation and chapter-based layout consistent with PyTorch documentation style.

#### Scenario: Theme renders with sidebar navigation
- **WHEN** documentation is built and viewed in a browser
- **THEN** the HTML page displays a left-sidebar with toctree navigation and a main content area with chapter-style layout

### Requirement: Sphinx extensions configuration
The Sphinx project SHALL be configured with the following extensions: `sphinx.ext.autodoc`, `sphinx.ext.napoleon`, `sphinx.ext.viewcode`, `sphinx.ext.intersphinx`, and `sphinx_autodoc_typehints`.

#### Scenario: Autodoc generates API pages from docstrings
- **WHEN** an `.rst` file contains `.. automodule:: pyleaf` directive
- **THEN** Sphinx generates an API Reference page from the module's Python docstrings

#### Scenario: Type hints appear in API documentation
- **WHEN** a Python function has type annotations in its signature
- **THEN** the generated API documentation includes those type annotations in the parameter descriptions

### Requirement: Python dependencies for doc build
The project SHALL include `sphinx`, `sphinx-book-theme`, and `sphinx-autodoc-typehints` as documented dependencies required for building docs.

#### Scenario: Install doc dependencies
- **WHEN** developer installs the project's doc-related dependencies
- **THEN** `sphinx`, `sphinx-book-theme`, and `sphinx-autodoc-typehints` are available in the Python environment