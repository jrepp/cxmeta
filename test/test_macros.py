import unittest

from cxmeta.pipeline.source_module import Module
from cxmeta.pipeline.cxx_processor import CxxProcessor
from cxmeta.config.project import Project
from cxmeta.pipeline.stream import InputBuffer, InputDirectory


macro_stmt = r"""#define API_WRAPPER(name) __declsepc(dllexport)"""

macro_cont_stmt = r"""
#define MY_CONTINUED_MACRO(expr) \
  if (expr) { \
    printf("%s is true!\n", #expr); \
  }
"""


class TestMacros(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Project()
        self.module = Module('test', InputDirectory('.'))

    def test_macro(self):
        # Not technically part of C or a statement but important to parse
        # for meta extraction process
        proc = CxxProcessor(self.project,
                            self.module,
                            InputBuffer(
                                self.test_macro.__name__, macro_stmt))
        proc.process()

    def test_macro_cont(self):
        proc = CxxProcessor(self.project,
                            self.module,
                            InputBuffer(
                                self.test_macro_cont.__name__, macro_cont_stmt))
        proc.process()


if __name__ == '__main__':
    unittest.main()
