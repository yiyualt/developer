import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "LangChain"
author = "Pyleaf"
version = "0.0.1"
release = "0.0.1"
copyright = "2025, Pyleaf"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_book_theme"
html_theme_options = {
    "repository_url": "https://github.com/langchain-ai/langchain",
    "path_to_docs": "docs",
    "use_repository_button": False,
    "use_edit_page_button": False,
    "use_issues_button": False,
    "navigation_with_keys": True,
    "show_toc_level": 2,
    "toc_title": "Table of Contents",
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

typehints_use_rtype = True