import unittest

from cxmeta.pipeline.source_module import module_name, Module
from cxmeta.pipeline.combiner import Combiner
from cxmeta.pipeline.stream import (
    Stream,
    Processor,
    Atom,
    InputDirectory,
    InputFile,
)
from cxmeta.config.project import Project


class FakeStrProcessor(Processor):
    def __init__(self, project, source):
        Processor.__init__(self, project, source, str, str)


class FakeIntProcessor(Processor):
    def __init__(self, project, source):
        Processor.__init__(self, project, source, str, int)


class FakeInputFile(InputFile):
    def __init__(self, fake_full_path):
        self.full_path = fake_full_path

    def read(self):
        return ""


class FakeInputDirectory(InputDirectory):
    def read(self):
        for x in ("/a/x.c", "/b/y.c", "/c/z.c"):
            yield FakeInputFile(x)


class TestBasics(unittest.TestCase):
    def test_module_name(self):
        self.assertTrue(module_name("/a/basic/path/to/module") == "module")
        self.assertTrue(
            module_name("/a/p/to/a/directoryasmodule/") == "directoryasmodule"
        )

    def test_module(self):
        project = Project()
        project.config["debug_files"] = True
        module = Module(project, FakeInputDirectory("/"))
        self.assertEqual(module.project, project)
        self.assertEqual(module.debug_files, True)
        module.process()

    def test_source_file(self):
        project = Project()
        module = Module(project, FakeInputDirectory("/"))
        combine = Combiner(project, module, FakeInputFile("foo.c"))
        self.assertEqual(combine.source.full_path, "foo.c")
        self.assertEqual(project.name, combine.project.name)

    def test_stream(self):
        s = Stream("source-name")
        s.append(Atom(1, 10, "test"))
        atom = next(s.read())
        self.assertIsNotNone(atom)
        self.assertEqual(atom.line_num, 1)
        self.assertEqual(atom.pos, 10)
        self.assertEqual(atom.data, "test")

    def test_processor_type(self):
        str_proc = FakeStrProcessor(Project(), "str-foo")
        int_proc = FakeIntProcessor(Project(), "int-foo")
        self.assertEqual(str_proc.in_type, str)
        self.assertEqual(int_proc.out_type, int)


if __name__ == "__main__":
    unittest.main()
