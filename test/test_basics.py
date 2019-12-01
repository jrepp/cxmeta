import unittest

from cxmeta.pipeline.source_module import module_name, Module
from cxmeta.pipeline.stream import Stream


class TestBasics(unittest.TestCase):
    def test_module_name(self):
        self.assertTrue(module_name('/a/basic/path/to/module') == 'module')
        self.assertTrue(module_name('/another/path/to/a/directoryasmodule/') == 'directoryasmodule')

    def test_construct_module(self):
        self.assertTrue(Module('name').name == 'name')

    def test_stream(self):
        s = Stream('source-name')
        s.append(1, )

if __name__ == '__main__':
    unittest.main()
