# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


import os
import sys
from datetime import date
sys.path.insert(0, os.path.abspath("../src"))
import curses_fzf

first_release_year = "2026"
now_year = str(date.today().year)
copyright_year = first_release_year
if first_release_year != now_year:
    copyright_year = f"{first_release_year}-{now_year}"

project = 'curses-fzf'
author = 'Heiko Finzel'
copyright = f'{copyright_year}, {author}'
release = curses_fzf.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',  # mardown support
    'sphinx.ext.autodoc',  # read docstrings from code
    'sphinx.ext.autodoc.typehints',  # show type hints in the description of the function, not in the signature
    'sphinx.ext.napoleon',  # support for Google and NumPy style docstrings
    'sphinx.ext.viewcode',  # add links to highlighted source code of documented Python objects
    'sphinx.ext.inheritance_diagram',  # graphviz diagrams for class inheritance
    'sphinx.ext.graphviz',  # graphviz diagrams for class inheritance
]

autodoc_preserve_defaults = True

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
