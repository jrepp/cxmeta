import unittest

from cxmeta.pipeline.source_module import module_name, Module


class TestBasics(unittest.TestCase):
    def test_module_name(self):
        self.assertTrue(module_name('/a/basic/path/to/module') == 'module')
        self.assertTrue(module_name('/another/path/to/a/directoryasmodule/') == 'directoryasmodule')

    def test_construct_module(self):
        self.assertTrue(Module('name').name == 'name')

if __name__ == '__main__':
    unittest.main()
