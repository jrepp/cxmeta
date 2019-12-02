import unittest

from cxmeta.pipeline.cxx_processor import Processor

macro_stmt = r"""#define API_WRAPPER(name) __declsepc(dllexport)"""

macro_cont_stmt = r"""
#define MY_CONTINUED_MACRO(expr) \
  if (expr) { \
    printf("%s is true!\n", #expr); \
  }
"""


class TestMacros(unittest.TestCase):
    def test_macro(self):
        # Not technically part of C or a statement but important to parse
        # for meta extraction process
        proc = Processor(self.test_macro.__name__)
        proc.process_lines(macro_stmt)

    def test_macro_cont(self):
        proc = Processor(self.test_macro_cont.__name__)
        proc.process_lines(macro_cont_stmt)


if __name__ == '__main__':
    unittest.main()
