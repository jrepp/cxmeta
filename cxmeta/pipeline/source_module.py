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
        self.files = list()

    def __str__(self):
        return '[Module] <name: {}, full_path: {}'.format(
            self.name, self.source.full_path)

    def process(self):
        if self.debug_files:
            print("# Processing module {}".format(self.name))
        # Look for a header / README.md
        for input_file in self.source.read():
            _, ext = os.path.splitext(input_file.full_path)
            if ext in ('.c', '.h'):
                if self.debug_files:
                    print("## [{}] processing path {}".format(self.name, input_file.full_path))
                file_proc = Combiner(self.project, self, input_file)
                file_proc.process()
                self.files.append(file_proc)
            else:
                if self.debug_files:
                    print("## [{}] ignoring path {}".format(self.name, input_file.full_path))
        return self


# Convert the directory name of the path into the modulename
def module_name(source_path):
    path_parts = os.path.split(source_path)
    if not path_parts[-1]:
        name = os.path.basename(path_parts[0])
    else:
        name = os.path.basename(path_parts[-1])
    return name
