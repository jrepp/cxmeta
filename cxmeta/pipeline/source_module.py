import os

from cxmeta.pipeline.stream import Processor, InputFile, InputDirectory
from cxmeta.pipeline.combiner import Combiner


class Module(Processor):
    def __init__(self, project, source):
        Processor.__init__(self, project, source, InputDirectory, InputFile)
        self.project = project
        self.source = source
        self.name = module_name(source.full_path)
        self.debug_files = project.config.get('debug_files')
        self.include_paths = project.config.get('include_paths')
        self.files = list()

    def __str__(self):
        return '[Module] <name: {}, full_path: {}'.format(
            self.name, self.source.full_path)

    def process(self):
        if self.debug_files:
            print("# Processing module {}".format(self.name))
        # Look for a header / README.md
        for input_file in self.source.read():
            if os.path.isdir(input_file.full_path) and \
                    self.allowed_sub_path(input_file.full_path):
                # Create a new module to handle the sub-module
                sub_module = Module(self.project,
                                    InputDirectory(input_file.full_path))
                if self.debug_files:
                    print("# Allowed sub-module {}".format(sub_module))
                sub_module.process()
                continue

            _, ext = os.path.splitext(input_file.full_path)
            if ext in ('.c', '.h'):
                if self.debug_files:
                    print("## [{}] processing path {}".format(
                        self.name, input_file.full_path))
                file_proc = Combiner(self.project, self, input_file)
                file_proc.process()
                self.files.append(file_proc)
            else:
                if self.debug_files:
                    print("## [{}] ignoring path {}".format(
                        self.name, input_file.full_path))
        return self

    def allowed_sub_path(self, full_path):
        # TODO: assume input_file is a child of module path
        #  this could be a mistake
        for include in self.include_paths:
            if full_path.endswith(include):
                return True
        return False


# Convert the directory name of the path into the module name
def module_name(source_path):
    path_parts = os.path.split(source_path)
    if not path_parts[-1]:
        name = os.path.basename(path_parts[0])
    else:
        name = os.path.basename(path_parts[-1])
    return name
