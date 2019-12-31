import os
import yaml
import logging
from typing import Any, Optional, Tuple, Mapping

from cxmeta.pipeline.source_module import module_name
from cxmeta.style.registry import DEFAULT_STYLE

CONFIG_NAME = ".cxmeta.yaml"
MAX_RECURSION = 3

VALID_SETTINGS: Mapping[str, Tuple[Any, str]] = {
    #
    # Debug settings
    #
    "debug": (False, "Enable all debug output"),
    "debug_matches": (False, "Enable regex matching debug"),
    "debug_atoms": (False, "Enable atom generation debug"),
    "debug_chunks": (False, "Enable chunk/combiner debug"),
    "debug_files": (False, "Enable file system debug"),
    "debug_export": (False, "Enable export debugging"),
    #
    # File handling settings
    #
    # General documentation settings
    "project_header": (None, "Relative path to the project header"),
    "output_directory": (
        None,
        "Local output directory, relative to project root",
    ),
    "output_path": (None, "Full path to output, will override project root"),
    "separate_source_files": (
        False,
        "Separate source files into different outputs",
    ),
    "include_paths": (list(), "Whitelist of paths while processing modules"),
    "include_extensions": ([".h"], "Extensions to parse"),
    "output_file_name": ("README.md", "Name of the project output file"),
    "publish_single_file": (
        True,
        "Include all files in the project output file",
    ),
    "style": (DEFAULT_STYLE, "Style to use for export"),
}

REQUIRED = {
    "include_extensions",
    "style",
    "publish_single_file",
    "output_file_name",
}


def get_default(name: str) -> Optional[Any]:
    setting = VALID_SETTINGS.get(name)
    if setting is not None:
        return setting[0]
    return None


class ConfigLoader(object):
    def __init__(self, full_path="."):
        self.full_path = full_path
        self.doc = None
        self.load()

    def load(self):
        log = logging.getLogger("cxmeta")
        self.doc = self.search_path(self.full_path)
        if self.doc is None:
            log.warning(
                "no config file {} found in {}".format(
                    CONFIG_NAME, self.full_path
                )
            )
            self.doc = self.default_config()
        return self.doc

    def default_config(self):
        return {
            "full_path": self.full_path,
            "name": module_name(self.full_path),
            "publish_single_file": get_default("publish_single_file"),
            "output_file_name": get_default("output_file_name"),
            "include_extensions": get_default("include_extensions"),
            "style": DEFAULT_STYLE,
        }

    @staticmethod
    def update_with_defaults(doc):
        """Update the config document with missing required defaults"""
        for name in REQUIRED:
            doc.setdefault(name, get_default(name))

    def search_path(self, path, depth=0):
        if depth > MAX_RECURSION:
            return None
        abspath = os.path.abspath(path)
        file_path = os.path.join(abspath, CONFIG_NAME)
        if os.path.exists(file_path):
            with open(file_path, "r") as input_stream:
                doc = yaml.safe_load(input_stream)
                doc["full_path"] = os.path.dirname(file_path)
                ConfigLoader.update_with_defaults(doc)
                return doc
        else:
            # recurse up one directory
            parent = os.path.dirname(path)
            self.search_path(parent, depth + 1)
        return None
