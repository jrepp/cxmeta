import unittest


from cxmeta.pipeline.combiner import Combiner


simple_combine = r"""
// non-attached

// ..class:: mxfunction
void my_function(int foo);

// non-attached 2
"""


class TestCombiner(unittest.TestCase):
    def test_combine(self):
        combiner = Combiner(self.test_combine.__name__).process_lines(simple_combine)
        combiner.combine()
        for atom in combiner.stream().read():
            chunk = atom.data
            print(chunk)


if __name__ == '__main__':
    unittest.main()