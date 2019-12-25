import unittest

from cxmeta.pipeline.gfm_exporter import GfmExporter
from cxmeta.config.project import Project


class TestGfmExporter(unittest.TestCase):
    def test_simple(self):
        GfmExporter(Project())


if __name__ == "__main__":
    unittest.main()
