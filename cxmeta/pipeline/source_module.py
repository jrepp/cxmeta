import os

from cxmeta.pipeline.source_file import FileProcessor

class Module(object):
    def __init__(self, name):
        self.name = name
        self.defines = []
        self.includes = []

    def add_define(self, define_value):
        self.defines.append(define_value)

    def add_include(self, include_value):
        self.includes.append(include_value)

    def each_file(self, path):
        print("# [{}] processing path {}".format(self.name, path))
        # Look for a header / README.md
        for filename in os.listdir(path):
            _, ext = os.path.splitext(filename)
            if ext in ('.c', '.h'):
                file_proc = FileProcessor(self, os.path.join(path, filename))
                file_proc.process_regex()
                file_proc.process_functions()


# Convert the directory name of the path into the modulename 
def module_name(source_path):
    path_parts = os.path.split(source_path)
    if not path_parts[-1]:
        name = os.path.basename(path_parts[0])
    else:
        name = os.path.basename(path_parts[-1])
    return name
