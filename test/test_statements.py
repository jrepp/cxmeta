import unittest

from cxmeta.pipeline.source_module import Module
from cxmeta.pipeline.cxx_processor import CxxProcessor
from cxmeta.pipeline.stream import Line, InputBuffer, InputDirectory
from cxmeta.config.project import Project


static_statment = r"""

static int foobaz = 42;

"""

enum_statement = r"""
typedef enum
{
E_A_VALUE = 1,
E_B_VALUE = 0x2,
} TestEnum;
"""


struct_statement = r"""
typedef struct
{
    int field_a;
    char* field_b;
} TestStruct;
"""


func_decl = r"""TestStruct* API_WRAPPER(test_struct_init) (
    TestStruct* v,
    int a,
    char* b);"""


func_defn = r"""
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
TestStruct* RANDOM_MACRO API_WRAPPER(define_a_func)(TestStruct* foo, int a) {
    if (foo != NULL) {
        printf("%d\n", foo->field_a);
    }
    return NULL;
}
"""

func_nested = r"""
void nested_func() {
    do { if (canwe) { for(auto &v : items} { \
        if(v.legit) { v.baz(); } } } } while(getting_there);
}
"""


class TestStatements(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Project(config={'debug': False})
        self.module = Module(self.project, InputDirectory('.'))

    def test_file_level(self):
        proc = CxxProcessor(self.project,
                            self.module,
                            InputBuffer(self.test_file_level.__name__, static_statment))
        proc.process()

    def test_enum(self):
        proc = CxxProcessor(self.project,
                            self.module,
                            InputBuffer(self.test_enum.__name__, enum_statement))
        proc.process()

    def test_struct(self):
        proc = CxxProcessor(self.project,
                            self.module,
                            InputBuffer(self.test_struct.__name__, struct_statement))
        proc.process()

    def test_function_decl(self):
        proc = CxxProcessor(self.project,
                            self.module,
                            InputBuffer(self.test_function_decl.__name__, func_decl))
        proc.process()

    def test_function_defn(self):
        proc = CxxProcessor(self.project,
                            self.module,
                            InputBuffer(self.test_function_defn.__name__, func_defn))
        proc.process()

    def test_function_defn_egyptian(self):
        proc = CxxProcessor(self.project,
                            self.module,
                            InputBuffer(self.test_function_defn_egyptian.__name__, func_defn_egyptian))
        proc.process()

    def test_function_nested(self):
        proc = CxxProcessor(self.project,
                            self.module,
                            InputBuffer(self.test_function_nested.__name__, func_nested))
        proc.process()


if __name__ == '__main__':
    unittest.main()
