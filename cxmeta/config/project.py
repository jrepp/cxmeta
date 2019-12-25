import os
from cxmeta.pipeline.gfm_exporter import GfmExporter
from cxmeta.pipeline.source_module import Module
from cxmeta.pipeline.stream import InputDirectory, InputFile
from . import random_name


class Status(object):
    def __init__(self, success, msg, props):
        self.success = success
        self.msg = msg
        self.props = props

    def __str__(self):
        ret = {"success": self.success, "message": self.msg}
        ret.update(self.props)
        return str(ret)


class SingleFile(InputDirectory):
    def __init__(self, full_path):
        InputDirectory.__init__(self, full_path)

    def read(self):
        assert os.path.isfile(self.full_path)
        yield InputFile(self.full_path)


class Project(object):
    def __init__(self, name=None, config=dict()):
        self.name = name or config.get("name", "project-" + random_name())
        self.config = config
        self.full_path = config.get("full_path", ".")
        assert self.full_path is not None
        assert os.path.exists(self.full_path)
        self.output_path = config.get(
            "output_path", os.path.join(self.full_path, "_output")
        )
        self.newline = config.get("newline", "\n")
        self.style = None

    def process(self):
        module = self.load_module()
        self.export(module)
        return Status(
            True,
            "project_complete",
            {
                "project_name": self.name,
                "full_path": self.full_path,
                "is_dir": os.path.isdir(self.full_path),
            },
        )
        return Status(False, "file_error")

    def load_module(self):
        if os.path.isdir(self.full_path):
            input_files = InputDirectory(self.full_path)
        elif os.path.isfile(self.full_path):
            input_files = SingleFile(self.full_path)
        module = Module(self, input_files)
        module.process()
        return module

    def export(self, module):
        exporter = GfmExporter(self)
        exporter.export_module(module)
