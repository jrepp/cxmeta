import os
import yaml
import logging

from cxmeta.pipeline.source_module import module_name

log = logging.getLogger('ConfigLoader')

valid_settings = {
    #
    # Debug settings
    #
    'debug': 'Enable all debug output',
    'debug_matches': 'Enable regex matching debug',
    'debug_atoms': 'Enable atom generation debug',
    'debug_chunks': 'Enable chunk/combiner debug',
    'debug_files': 'Enable file system debug',
    'debug_export': 'Enable export debugging',

    #
    # File handling settings
    #
    'separate_source_files':
        'Separate source files into different outputs'
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
            log.warning('no config file .cxmeta found in {}'.format(self.full_path))
            self.doc = self.default_config()
        return self.doc

    def default_config(self):
        return {'full_path': self.full_path,
                'name': module_name(self.full_path)}

    def search_path(self, path, depth=0):
        if depth > 5:
            return None

        abspath = os.path.abspath(path)
        file_path = os.path.join(abspath, '.cxmeta')
        if os.path.exists(file_path):
            with open(file_path, 'r') as input_stream:
                doc = yaml.safe_load(input_stream)
                doc['full_path'] = os.path.dirname(file_path)
                return doc
        else:
            # recurse up one directory
            parent = os.path.dirname(path)
        return None

