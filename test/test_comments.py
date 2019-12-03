import unittest
import logging

#
# All comment blocks should be preceded with a rST class directive
# http://docutils.sourceforge.net/docs/ref/rst/directives.html#class
#
# The content following the class should conform to the rules of that
# class. See cxtypes.*
#

from cxmeta.pipeline.cxx_processor import Processor
from cxmeta.pipeline import source_module, source_file


# Use as many * characters as you want
multiline_function_c_style = r"""
/******* ..class:: mxfunction
 *
 *  // embedded string comment
 * 
 * # Section header
 *
 * Some standard paragraph
 **/
"""


def next_content(i):
    while True:
        atom = next(i)
        content = atom.data.get('content')
        if content:
            return content


class TestComments(unittest.TestCase):
    def test_empty(self):
        comments = Processor(self.test_empty.__name__).process_lines(r'').stream()
        self.assertTrue(comments.is_empty())

    def test_before_and_after_empty(self):
        comments = Processor(self.test_before_and_after_empty.__name__).process_lines(r'  /**/  ').stream()
        i = comments.read()
        self.assertEqual(next_content(i), r'  ')
        self.assertEqual(next_content(i), r'  ')

    def test_multi_line_embedded(self):
        proc = Processor('multiline_function_c_style')
        comments = proc.process_lines(multiline_function_c_style).stream()
        i = comments.read()
        self.assertEqual(next_content(i), ' ..class:: mxfunction')
        self.assertEqual(next_content(i), ' *')
        self.assertEqual(next_content(i), ' *  //')
        self.assertEqual(next_content(i), ' embedded string comment')

    def test_compact(self):
        compact_tag = r'/*..class:: type*/'
        comments = Processor('compact_tag').process_line(compact_tag).stream()
        first = next_content(comments.read())
        self.assertEqual(first, r'..class:: type')

    def test_two_lines(self):
        two_lines = r"""//// blah
// blah2
"""
        comments = Processor('two_lines').process_lines(two_lines).stream()
        i = comments.read()
        self.assertEqual(next_content(i), ' blah')
        self.assertEqual(next_content(i), ' blah2')


if __name__ == '__main__':
    logging.basicConfig(filename='comment-proc.log', level=logging.DEBUG)
    unittest.main()
