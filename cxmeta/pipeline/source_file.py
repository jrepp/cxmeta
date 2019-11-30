
import re
import sys

from contextlib import contextmanager

from pycparser import c_parser, c_ast, parse_file

# A visitor with some state information (the funcname it's looking for)
class FuncCallVisitor(c_ast.NodeVisitor):
    """
    When passed to a pycparser ast this will visit funcions in the AST
    """
    def __init__(self, out, receiver):
        self.out = out
        self.receiver = receiver

    def visit_FuncCall(self, node):
        self.out.print('{} called at {}'.format(
            self.funcname, node.name.coord))

        # Visit args in case they contain more func calls.
        if node.args:
            self.visit(node.args)


class CodeBlockStream(object):
    """
    Given a stream of lines this matcher will produce a stream of blocks
    of code and their surround decorations.
    e.g.:
        a b c() { } x y z; 
    """

class CommentStream(object):
    """
    Given a stream of lines this matcher will produce a stream of comment 
    blocks.
    
        This handles C and C++ coments 
    """
    def __init__(self, target):
        self.patterns = [ 
            ("Section start", re.compile(r'^//\w~?#'), target.start_section),
            ("Comment line", re.compile(r'^//\w+?'), target.comment_content),
            ("Code section marker", re.compile(r'^// ~~~~'), self.toggle_code_section)
        ]
        self.in_code_section = False

    def toggle_code_section(self, line):
        if not self.in_code_section:
            self.emit_line_nosub('```c')
            self.emit_empty()
        else:
            self.emit_line_nosub('```')
            self.emit_empty()
        self.in_code_section = not self.in_code_section

    def process_line(self, line):
        for patterns in self.matchers:
            desc, expr, func = expr
            m = expr.match(line)
            func(line)
        

class FileProcessor(object):
    def __init__(self, module, filename):
        self.module = module
        self.in_code_section = False
        self.out = sys.stdout
        self.filename = filename
        
    def start_section(self, line):
        self.out.write("\n{}".format(line[3:]))

    def emit_line(self, line):
        self.out.write("{}".format(line[3:]))

    def emit_line_nosub(self, line):
        self.out.write(line)

    def emit_empty(self):
        self.out.write("\n")

    def process_line(self, line):
        self.regex_ 

    def process_regex(self):
        print("[{}] processing {}".format(self.module.name, self.filename))
        with open(self.filename, 'r') as f:
            map(self.regex_proc.process_line, f.readlines())
        self.out.flush()

    def process_functions(self):
        ast = parse_file(self.filename, use_cpp=True)
        v = FuncCallVisitor(self)
        v.visit(ast)  
