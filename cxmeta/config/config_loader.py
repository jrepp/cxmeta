import os
import pyaml
import logging

from cxmeta.pipeline.source_module import module_name

CONFIG_NAME = ".cxmeta.yml"


log = logging.getLogger("ConfigLoader")

valid_settings = {
    # General documentation settings
    "project_header": "Relative path to a file to \
include as the project header",
    #
    # Debug settings
    #
    "debug": "Enable all debug output",
    "debug_matches": "Enable regex matching debug",
    "debug_atoms": "Enable atom generation debug",
    "debug_chunks": "Enable chunk/combiner debug",
    "debug_files": "Enable file system debug",
    "debug_export": "Enable export debugging",
    #
    # File handling settings
    #
    "output_directory": "Local output directory, will be relative to project root",
    "output_path": "Full path to output, will override project root",
    "separate_source_files": "Separate source files into different outputs",
    "include_paths": "Whitelist of paths while processing modules",
}


class ConfigLoader(object):
    def __init__(self, full_path):
        self.full_path = full_path
        self.doc = None
        self.load()

    def __str__(self):
        str(self.doc)

    def load(self):
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
        }

    def search_path(self, path, depth=0):
        if depth > 5:
            return None

        abspath = os.path.abspath(path)
        file_path = os.path.join(abspath, CONFIG_NAME)
        if os.path.exists(file_path):
            with open(file_path, "r") as input_stream:
                doc = pyaml.safe_load(input_stream)
                doc["full_path"] = os.path.dirname(file_path)
                return doc
        else:
            # recurse up one directory
            parent = os.path.dirname(path)
            self.search_path(parent, depth + 1)
        return None
