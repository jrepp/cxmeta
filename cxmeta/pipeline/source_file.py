import sys
from cxmeta.pipeline.cxx_processor import Processor


class FileProcessor(object):
    def __init__(self, module, filename):
        self.module = module
        self.in_code_section = False
        self.out = sys.stdout
        self.filename = filename

    def process(self, debug=False):
        if debug:
            print("[{}] processing {}".format(self.module.name, self.filename))
        with open(self.filename, 'r') as f:
            proc = Processor(self.filename)
            map(proc.process_line, f.readlines())
        self.out.flush()
