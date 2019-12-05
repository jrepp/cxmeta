import os
import yaml
import logging


log = logging.getLogger('ConfigLoader')


class ConfigLoader(object):
    def __init__(self, path):
        self.path = path
        self.doc = None
        self.load()

    def __str__(self):
        str(self.doc)

    def load(self):
        self.doc = self.search_path(self.path)
        if self.doc is None:
            log.warn('no config file .cxmeta found in {}'.format(self.path))
        return self.doc

    def search_path(self, path):
        abspath = os.path.abspath(path)
        full_path = os.path.join(abspath, '.cxmeta')
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                doc = yaml.safe_load(f)
                return doc
        else:
            # recurse up one directory
            return self.search_path(os.path.dirname(path))
        return None