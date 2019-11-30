import unittest

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
multiline_function_c_style = """
/******* ..class:: mxfunction
 *
 *  // embedded string comment
 * 
 * # Section header
 *
 * Some standard paragraph
 **/
"""

multiline_function_cxx_style = """
"""

multiline_meta_c_style = """
/** ..class:: cxmeta
 * 
 *
 */
"""

mutiline_meta_cxx_style = """
/////// 
//
//
//
"""

singleline_tag = """
//..class:: mxtype
//
"""
class TestCommentStream(unittest.TestCase):
    def test_parse_comments(self):
        pass


if __name__ == '__main__':
    unittest.main()
