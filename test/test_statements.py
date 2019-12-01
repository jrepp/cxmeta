import unittest

from cxmeta.pipeline.cxx_statements import StatementProcessor

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
    do { if (canwe) { for(auto &v : items} { if(v.legit) { v.baz(); } } } } while(getting_there);
}
"""

macro_stmt = r"""#define API_WRAPPER(name) __declsepc(dllexport)"""

macro_cont_stmt = r"""
#define MY_CONTINUED_MACRO(expr) \
  if (expr) { \
    printf("%s is true!\n", #expr); \
  }
"""

class TestStatements(unittest.TestCase):
    def test_file_level(self):
        proc = StatementProcessor(self.test_file_level.__name__)
        proc.process_lines(static_statment)

    def test_enum(self):
        proc = StatementProcessor(self.test_enum.__name__)
        proc.process_lines(enum_statement)

    def test_struct(self):
        proc = StatementProcessor(self.test_struct.__name__)
        proc.process_lines(struct_statement)

    def test_function_decl(self):
        proc = StatementProcessor(self.test_function_decl.__name__)
        proc.process_lines(func_decl)

    def test_function_defn(self):
        proc = StatementProcessor(self.test_function_defn.__name__)
        proc.process_lines(func_defn)

    def test_function_defn_egyptian(self):
        proc = StatementProcessor(self.test_function_defn_egyptian.__name__)
        proc.process_lines(func_defn_egyptian)

    def test_function_nested(self):
        proc = StatementProcessor(self.test_function_nested.__name__)
        proc.process_lines(func_nested)

    def test_macro(self):
        # Not technically part of C or a statement but important to parse
        # for meta extraction process
        proc = StatementProcessor(self.test_macro.__name__)
        proc.process_lines(macro_stmt)

    def test_macro_cont(self):
        proc = StatementProcessor(self.test_macro_cont.__name__)
        proc.process_lines(macro_cont_stmt)


if __name__ == '__main__':
    unittest.main()