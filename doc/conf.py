import sys
import os


sys.path.insert(0, os.path.abspath('../src'))

extensions = ["sphinx_tabs.tabs"]

templates_path = ["_templates"]

source_suffix = ".rst"

master_doc = "index"

# General information about the project.
project = u"BREWasm"
copyright = u"Contributors to the BREWasm project"

version = release = "0.0"

exclude_patterns = ["_build"]

pygments_style = "sphinx"

html_theme = "sphinx_rtd_theme"

htmlhelp_basename = "BREWasmdoc"

man_pages = [("index", "BREWasm", "BREWasm Documentation", ["BREWasm"], 1)]
