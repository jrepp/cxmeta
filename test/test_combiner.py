import unittest


from cxmeta.pipeline.source_module import Module
from cxmeta.pipeline.combiner import Combiner
from cxmeta.config.project import Project
from cxmeta.pipeline.stream import InputBuffer, Chunk, InputDirectory

simple_combine = r"""
// non-attached

// ..class:: mxfunction
void my_function(int foo);

// non-attached 2
"""

two_chunks = r"""
// ..class:: mxfunction
void function_one();

// ..class:: mxfunction
void function_two();
"""

three_blocks = r"""
// ..class:: mxfunction
void function_one() {
    for (int i = 0; i < 10; ++i) {
        printf(%d\n", i);
    }
}

// ..class:: mxfunction
void function_two()
{
    for (int i = 0; i < 10; ++i)
    {
        printf("%d\n", i);
    }
}

// ..class:: mxfunction
void function_three () {}
"""


class TestCombiner(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Project()
        self.module = Module(self.project, InputDirectory('.'))

    def test_combine(self):
        combiner = Combiner(self.project,
                            self.module,
                            InputBuffer(self.test_combine.__name__, simple_combine))
        combiner.process()
        self.assertEqual(len(combiner.stream_data.content), 1)
        for chunk in combiner.stream().read():
            self.assertTrue(isinstance(chunk, Chunk))
            # print(chunk)

    def test_combine_two(self):
        # self.project.config['debug_chunks'] = True
        combiner = Combiner(self.project,
                            self.module,
                            InputBuffer(self.test_combine_two.__name__, two_chunks))
        combiner.process()
        self.assertEqual(len(combiner.stream_data.content), 2)
        for chunk in combiner.stream().read():
            self.assertTrue(isinstance(chunk, Chunk))
            self.assertTrue(chunk.line_num > 0)
            self.assertTrue(len(chunk.stmt) > 0)
            self.assertTrue(len(chunk.comment) > 0)
            self.assertTrue(len(chunk.class_name) > 0)
            # print(chunk)

    def test_combine_three_styles(self):
        self.project.config['debug_chunks'] = True
        self.project.config['debug_atoms'] = True
        self.project.config['debug_matches'] = True
        combiner = Combiner(self.project,
                            self.module,
                            InputBuffer(self.test_combine_three_styles.__name__, three_blocks))
        combiner.process()
        self.assertEqual(len(combiner.stream_data.content), 3)
        for chunk in combiner.stream().read():
            self.assertTrue(isinstance(chunk, Chunk))
            # print(chunk)


if __name__ == '__main__':
    unittest.main()
