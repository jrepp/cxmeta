import unittest
import yaml

from cxmeta.pipeline.builder import Builder


test_config = """
name: test-project
description: a test
main-page: foo.md
module-index: index.md
parser-combiner: cxx
ingest-meta: rst
export: gfm
"""

test_invalid_config = """
name: invalid
ingest-meta: unknown
"""


class TestBuildPipeline(unittest.TestCase):
    def test_empty(self):
        Builder().build_from_config(dict())

    def test_default(self):
        Builder().build_default()

    def test_load_config(self):
        doc = yaml.safe_load(test_config)
        project = Builder().build_from_config(doc)
        self.assertEqual(project.name, "test-project")

    def test_invalid(self):
        def does_raise():
            doc = yaml.safe_load(test_invalid_config)
            Builder().build_from_config(doc)

        # self.assertRaises(ModuleNotFoundError, does_raise)
        # TODO: implement this test again
        pass


if __name__ == "__main__":
    unittest.main()
