import os
from cxmeta.pipeline.source_file import FileProcessor


class Module(object):
    def __init__(self, path):
        self.name = module_name(path)
        self.path = path

    def process(self, debug=False):
        if debug:
            print("# [{}] processing path {}".format(self.name, self.path))
        # Look for a header / README.md
        for filename in os.listdir(self.path):
            _, ext = os.path.splitext(filename)
            if ext in ('.c', '.h'):
                file_proc = FileProcessor(self, os.path.join(self.path, filename))
                file_proc.process(debug)


# Convert the directory name of the path into the modulename
def module_name(source_path):
    path_parts = os.path.split(source_path)
    if not path_parts[-1]:
        name = os.path.basename(path_parts[0])
    else:
        name = os.path.basename(path_parts[-1])
    return name
