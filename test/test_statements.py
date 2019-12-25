import unittest

from cxmeta.pipeline.source_module import Module
from cxmeta.pipeline.cxx_processor import tokenize_cxx_identifiers
from cxmeta.pipeline.combiner import Combiner
from cxmeta.pipeline.stream import InputBuffer, InputDirectory
from cxmeta.config.project import Project


static_statment = r"""

static int foobaz = 42;

"""

typedef_enum_statement = r"""
// A typed enum
typedef enum
{
E_A_VALUE = 1,
E_B_VALUE = 0x2,
} TestEnum;
"""

enum_statment = r"""
// A bare enum
enum
{
    E_A_VALUE = 1,
    E_B_VALUE = 2,
};
"""

typedef_struct_statement = r"""
// A typedef'ed struct
typedef struct
{
    int field_a;
    char* field_b;
} TestStruct;
"""


struct_statement = r"""
// A simple undecorated struct
struct
{
    int field_a;
    char* field_b;
};
"""

func_decl = r"""
// A decorated wrapped function declaration statement
TestStruct* API_WRAPPER(test_struct_init) (
    TestStruct* v,
    int a,
    char* b);"""


func_type_decl = r"""
// A typed function
typedef (void*)(my_function_type(int arg, void* param2);"""


typed_int = r"""
// A typed int
typedef int MyInt;
"""


func_defn = r"""
// This is a decorated function split across a few lines
TestStruct*
API_WRAPPER_DEFN(test_struct_init)
(
TestStruct* v,
int a,
char* b)
{
    int i;
    for (i = 0; i < 42; ++i) {
        printf("%d\n", i);
    }
    return NULL;
}
"""

func_defn_egyptian = r"""
// This is a decorated function with some involved parameters
TestStruct* RANDOM_MACRO API_WRAPPER(define_a_func)(TestStruct* foo, int a) {
    if (foo != NULL) {
        printf("%d\n", foo->field_a);
    }
    return NULL;
}
"""

func_nested = r"""
// This is a function with nested content
void nested_func() {
    do { if (canwe) { for(auto &v : items} { \
        if(v.legit) { v.baz(); } } } } while(getting_there);
}
"""


class TestStatements(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Project(config={"debug": False})
        self.module = Module(self.project, InputDirectory("."))

    def process(self, name, content):
        return Combiner(
            self.project, self.module, InputBuffer(name, content)
        ).process()

    def test_file_level(self):
        self.process(self.test_file_level.__name__, static_statment)

    def test_typedef_enum(self):
        proc = self.process(
            self.test_typedef_enum.__name__, typedef_enum_statement
        )
        self.assert_classification(proc, r"enum")

    def test_enum(self):
        proc = self.process(self.test_enum.__name__, enum_statment)
        self.assert_classification(proc, r"enum")

    def test_typedef_struct(self):
        proc = self.process(
            self.test_typedef_struct.__name__, struct_statement
        )
        self.assert_classification(proc, r"struct")

    def test_struct(self):
        proc = self.process(self.test_struct.__name__, struct_statement)
        self.assert_classification(proc, r"struct")

    def test_typedef_int(self):
        proc = self.process(self.test_typedef_int.__name__, typed_int)
        self.assert_classification(proc, r"typedef")

    def test_function_decl(self):
        proc = self.process(self.test_function_decl.__name__, func_decl)
        self.assert_classification(proc, r"function")

    def test_function_defn(self):
        proc = self.process(self.test_function_defn.__name__, func_defn)
        self.assert_classification(proc, r"function")

    def test_function_defn_egyptian(self):
        proc = self.process(
            self.test_function_defn_egyptian.__name__, func_defn_egyptian
        )
        self.assert_classification(proc, r"function")

    def test_function_nested(self):
        proc = self.process(self.test_function_nested.__name__, func_nested)
        self.assert_classification(proc, r"function")

    def test_tokenize_function_atom(self):
        atom = "void some_function("
        self.assertListEqual(
            tokenize_cxx_identifiers(atom), ["void", "some_function"]
        )

    def assert_classification(self, proc, type_str: str):
        def classify_check():
            for chunk in proc.stream().read():
                if type_str in chunk.types:
                    return True
            return False

        self.assertTrue(classify_check())


if __name__ == "__main__":
    unittest.main()
