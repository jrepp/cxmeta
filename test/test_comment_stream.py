import unittest
import logging

#
# All comment blocks should be preceded with a rST class directive
# http://docutils.sourceforge.net/docs/ref/rst/directives.html#class
#
# The content following the class should conform to the rules of that
# class. See cxtypes.*
#

from cxmeta.pipeline.cxx_comments import CommentProcessor

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


class TestCommentStream(unittest.TestCase):
    def test_empty(self):
        proc = CommentProcessor('empty')
        comments, data = proc.process_lines(r'')
        self.assertTrue(comments.is_empty())
        self.assertTrue(data.is_empty())

    def test_multi_line_embedded(self):
        proc = CommentProcessor('multiline_function_c_style')
        comments, data = proc.process_lines(multiline_function_c_style)

        self.assertEqual(next(data.read()).data, r'')

        i = comments.read()
        self.assertEqual(next(i).data, ' ..class:: mxfunction')
        self.assertEqual(next(i).data, ' *')
        self.assertEqual(next(i).data, ' *  ')
        self.assertEqual(next(i).data, ' embedded string comment')

    def test_compact(self):
        compact_tag = r'/*..class:: type*/'
        streams = CommentProcessor('compact_tag').process_line(compact_tag)
        comments, data = streams
        first = next(comments.read()).data
        self.assertEqual(first, r'..class:: type')

    def test_two_lines(self):
        two_lines = r"""//// blah
// blah2
"""
        streams = CommentProcessor('two_lines').process_lines(two_lines)
        comments, data = streams
        i = comments.read()
        self.assertEqual(next(i).data, ' blah')
        self.assertEqual(next(i).data, ' blah2')
        self.assertTrue(data.is_empty())


if __name__ == '__main__':
    logging.basicConfig(filename='comment-proc.log', level=logging.DEBUG)
    unittest.main()