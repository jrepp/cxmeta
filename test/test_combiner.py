import unittest


from cxmeta.pipeline.source_module import Module
from cxmeta.pipeline.combiner import Combiner
from cxmeta.config.project import Project
from cxmeta.pipeline.stream import InputBuffer, Chunk, InputDirectory

simple_combine = r"""
// non-attached

// Comment for my_function
void my_function(int foo);

// non-attached 2
"""

two_chunks = r"""
// Comment for function_one
void function_one();

// Comment for function_two
void function_two();
"""

three_blocks = r"""
// Function one
void function_one() {
    for (int i = 0; i < 10; ++i) {
        printf(%d\n", i);
    }
}

// Function two
void function_two()
{
    for (int i = 0; i < 10; ++i)
    {
        printf("%d\n", i);
    }
}

// Function three
void function_three () {}
"""

inline_comments = r"""
// An enum with embedded comments
typedef enum {
    VALUE_A = 1, /* Value A */
    VALUE_B = 2, /* Value B */
    VALUE_C = 3, /* Value C */
} Embedded;"""

inline_cxx_comments = r"""
// An enum with embedded comments
typedef enum {
    VALUE_A = 1, // Value A
    VALUE_B = 2, // Value B
    VALUE_C = 3, // Value C
} Embedded;"""

all_on_one_line = r"""/* An inline type definition */ \
enum { VALUE_A = 1 /* Value A */, \VALUE_B = 2 /* Value B */, \
VALUE_C = 3 /* Value C */ };"""

fold_lines = r"""
// comment one
// comment two
//
//
//
// comment three
void some_function();
"""


class TestCombiner(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Project()
        self.module = Module(self.project, InputDirectory("."))

    def process(self, name: str, buffer: str) -> Combiner:
        return Combiner(
            self.project, self.module, InputBuffer(name, buffer)
        ).process()

    def test_combine(self):
        combiner = self.process(self.test_combine.__name__, simple_combine)
        self.assertEqual(len(combiner.stream_data.content), 1)
        for chunk in combiner.stream().read():
            self.assertTrue(isinstance(chunk, Chunk))

    def test_combine_two(self):
        combiner = self.process(self.test_combine_two.__name__, two_chunks)
        self.assertEqual(2, len(combiner.stream_data.content))
        for chunk in combiner.stream().read():
            self.assertTrue(isinstance(chunk, Chunk))
            self.assertTrue(chunk.line_num > 0)
            self.assertTrue(len(chunk.code) > 0)
            self.assertTrue(len(chunk.docs) > 0)

    def test_combine_three_styles(self):
        # self.project.config['debug_chunks'] = True
        # self.project.config['debug_atoms'] = True
        # self.project.config['debug_matches'] = True
        combiner = self.process(
            self.test_combine_three_styles.__name__, three_blocks
        )
        self.assertEqual(3, len(combiner.stream_data.content))
        for chunk in combiner.stream().read():
            self.assertTrue(isinstance(chunk, Chunk))

    def test_inline_comments(self):
        self.project.config["debug_atoms"] = True
        # Three different flavors of inline comment
        combiner = self.process("inline_comments", inline_comments)
        self.check_inline_combiner(combiner)
        combiner = self.process("all_on_one_line", all_on_one_line)
        self.check_inline_combiner(combiner)
        combiner = self.process("inline_cxx_comments", inline_cxx_comments)
        self.check_inline_combiner(combiner)

    def check_inline_combiner(self, combiner):
        # Verify that one chunk is produced that has the enumeration and
        # comments about enumerated elements preserved in the statement text
        self.assertEqual(1, len(combiner.stream_data.content))
        for chunk in combiner.stream().read():
            self.assertTrue(isinstance(chunk, Chunk))
            self.assertIn("enum", chunk.types)
            self.assertTrue("".join(chunk.code).index("VALUE_B") > 0)
            self.assertTrue("".join(chunk.code).index("Value B") > 0)

    def test_fold_newlines(self):
        combiner = self.process(self.test_fold_newlines.__name__, fold_lines)
        chunk = next(combiner.stream_data.read())
        self.assertEqual(
            chunk.docs,
            [
                r"comment one",
                "\n",
                r"comment two",
                "\n\n",
                r"comment three",
                "\n",
            ],
        )


if __name__ == "__main__":
    unittest.main()
