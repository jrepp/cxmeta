import unittest
import logging

#
# All comment blocks should be preceded with a rST class directive
# http://docutils.sourceforge.net/docs/ref/rst/directives.html#class
#
# The content following the class should conform to the rules of that
# class. See cxtypes.*
#

from cxmeta.pipeline.cxx_processor import CxxProcessor
from cxmeta.pipeline.source_module import Module
from cxmeta.pipeline.stream import Line, InputBuffer, InputDirectory, Atom
from cxmeta.config.project import Project

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
    def setUp(self) -> None:
        self.project = Project()
        self.module = Module('test-comments', InputDirectory('.'))

    def test_empty(self):
        comments = CxxProcessor(self.project,
                                self.module,
                                InputBuffer(self.test_empty.__name__, ''))
        # The stream has one newline and that's it
        i = comments.process().stream().read()
        atom = next(i)
        self.assertEqual(type(atom), Atom)
        self.assertEqual(atom.data['type'], 'newline')

    def test_before_and_after_empty(self):
        comments = CxxProcessor(self.project,
                                self.module,
                                InputBuffer(self.test_before_and_after_empty.__name__,
                                    r'  /**/  '))
        comments.process()
        i = comments.stream().read()
        self.assertEqual(next_content(i), r'  ')
        self.assertEqual(next_content(i), r'  ')

    def test_multi_line_embedded(self):
        proc = CxxProcessor(self.project,
                            self.module,
                            InputBuffer('multiline_function_c_style',
                                        multiline_function_c_style))
        comments = proc.process().stream()
        i = comments.read()
        self.assertEqual(next_content(i), ' ..class:: mxfunction')
        self.assertEqual(next_content(i), ' *')
        self.assertEqual(next_content(i), ' *  //')
        self.assertEqual(next_content(i), ' embedded string comment')

    def test_compact(self):
        compact_tag = r'/*..class:: type*/'
        line = Line(1, compact_tag)
        comments = CxxProcessor(self.project,
                                self.module,
                                InputBuffer('compact_tag', compact_tag))
        stream = comments.process().stream()
        first = next_content(stream.read())
        self.assertEqual(first, r'..class:: type')

    def test_two_lines(self):
        two_lines = r"""//// blah
// blah2
"""
        comments = CxxProcessor(self.project,
                                self.module,
                                InputBuffer('two_lines', two_lines))
        stream = comments.process().stream()
        i = stream.read()
        self.assertEqual(next_content(i), ' blah')
        self.assertEqual(next_content(i), ' blah2')


if __name__ == '__main__':
    logging.basicConfig(filename='comment-proc.log', level=logging.DEBUG)
    unittest.main()
