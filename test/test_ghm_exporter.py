import unittest

from cxmeta.pipeline.gfm_exporter import GfmExporter
from cxmeta.config.project import Project
from cxmeta.config.config_loader import ConfigLoader


class TestGfmExporter(unittest.TestCase):
    def test_simple(self):
        GfmExporter(Project(config=ConfigLoader().default_config()))


if __name__ == "__main__":
    unittest.main()
