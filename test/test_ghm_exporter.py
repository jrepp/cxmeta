import unittest

from cxmeta.pipeline.gfm_exporter import GhmExporter
from cxmeta.pipeline.stream import InputFile, OutputFile, Chunk
from cxmeta.config.project import Project


class TestGfmExporter(unittest.TestCase):
    def test_has_content(self):
        self.assertEqual(True, True)

    def test_stream_type(self):
        export = GfmExporter(Project(), 'source-name')
        self.assertTrue(export.in_type(), Chunk)
        self.assertTrue(export.out_type(), OutputFile)


if __name__ == '__main__':
    unittest.main()
