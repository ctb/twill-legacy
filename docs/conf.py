"""Configuration file for the Sphinx documentation builder.

This file only contains a selection of the most common options.
For a full list see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

# -- Path setup --------------------------------------------------------------

import os
import sys

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"
    )
)

# -- Project information -----------------------------------------------------


def project_version():
    """Fetch version from pyproject.toml file."""
    # this also works when the package is not installed
    with open("../pyproject.toml") as toml_file:
        for line in toml_file:
            if line.startswith("version ="):
                version = line.split("=")[1].strip().strip('"')
                return version
    raise Exception("Cannot determine project version")


project = "twill"
author = "C. Titus Brown, Ben R. Taylor, Christoph Zwerschke et al"
copyright = "2023, " + author

# The full version, including alpha/beta/rc tags
version = release = project_version()

language = "en"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = []

# Add any paths that contain templates here, relative to this directory.
# templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages. See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']
