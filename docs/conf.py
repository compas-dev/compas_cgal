# -*- coding: utf-8 -*-

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = "1.0"

from sphinx.ext.napoleon.docstring import NumpyDocstring

import sphinx_compas_theme

# -- General configuration ------------------------------------------------

project = "COMPAS CGAL"
copyright = "2017, Block Research Group - ETH Zurich"
author = "Tom Van Mele"
release = "0.1.0"

version = ".".join(release.split(".")[0:2])

master_doc = "index"
source_suffix = [".rst", ]
templates_path = ["_templates"]
exclude_patterns = []

pygments_style = "sphinx"
show_authors = True
add_module_names = True
language = None


# -- Extension configuration ------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "matplotlib.sphinxext.plot_directive",
]

# autodoc options

autodoc_mock_imports = ["Rhino", "System", "scriptcontext", "rhinoscriptsyntax", "clr", "bpy"]

autodoc_default_options = {
    "undoc-members": True,
    "show-inheritance": True,
}

autodoc_member_order = "groupwise"

autoclass_content = "class"

# autosummary options

autosummary_generate = True
autosummary_mock_imports = ["Rhino", "System", "scriptcontext", "rhinoscriptsyntax", "clr", "bpy"]

# napoleon options

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = False
napoleon_use_rtype = False


# first, we define new methods for any new sections and add them to the class
def parse_keys_section(self, section):
    return self._format_fields("Keys", self._consume_fields())


NumpyDocstring._parse_keys_section = parse_keys_section


def parse_attributes_section(self, section):
    return self._format_fields("Attributes", self._consume_fields())


NumpyDocstring._parse_attributes_section = parse_attributes_section


def parse_class_attributes_section(self, section):
    return self._format_fields("Class Attributes", self._consume_fields())


NumpyDocstring._parse_class_attributes_section = parse_class_attributes_section


# we now patch the parse method to guarantee that the the above methods are
# assigned to the _section dict
def patched_parse(self):
    self._sections["keys"] = self._parse_keys_section
    self._sections["class attributes"] = self._parse_class_attributes_section
    self._unpatched_parse()


NumpyDocstring._unpatched_parse = NumpyDocstring._parse
NumpyDocstring._parse = patched_parse

# plot options

# plot_include_source
# plot_pre_code
# plot_basedir
# plot_formats
# plot_rcparams
# plot_apply_rcparams
# plot_working_directory
# plot_template

plot_html_show_source_link = False
plot_html_show_formats = False

# intersphinx options

intersphinx_mapping = {
    "python": ("https://docs.python.org/", None),
    "compas": ("https://compas-dev.github.io/compas", "https://compas-dev.github.io/compas/objects.inv"),
}


# -- Options for HTML output ----------------------------------------------

html_theme = "compaspkg"
html_theme_path = sphinx_compas_theme.get_html_theme_path()
html_theme_options = {
    "package_name": "compas_cgal",
    "package_title": project,
    "package_version": release,
    "package_author": "Tom Van Mele",
    "package_description": "COMPAS package for working with CGAL",
    "package_repo": "https://github.com/BlockResearchGroup/compas_cgal",
    "package_docs": "https://blockresearchgroup.github.io/compas_cgal"
}
html_context = {}
html_static_path = []
html_extra_path = [".nojekyll"]
html_last_updated_fmt = ""
html_copy_source = False
html_show_sourcelink = False
html_add_permalinks = ""
html_experimental_html5_writer = True
html_compact_lists = True
