import unittest


from cxmeta.pipeline.combiner import Combiner


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
}

// ..class:: mxfunction
void function_two()
{
}

// ..class:: mxfunction
void function_three () {}
"""


class TestCombiner(unittest.TestCase):
    def test_combine(self):
        combiner = Combiner(self.test_combine.__name__).process_lines(simple_combine)
        combiner.combine()
        for atom in combiner.stream().read():
            chunk = atom.data
            print(chunk)

    def test_combine_two(self):
        combiner = Combiner(self.test_combine_two.__name__).process_lines(two_chunks)
        combiner.combine()
        for atom in combiner.stream().read():
            chunk = atom.data
            print(chunk)

    def test_combine_three_styles(self):
        combiner = Combiner(self.test_combine_three_styles.__name__).process_lines(three_blocks)
        combiner.combine()
        for atom in combiner.stream().read():
            chunk = atom.data
            print(chunk)


if __name__ == '__main__':
    unittest.main()