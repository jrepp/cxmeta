import  re

from .line_processor import LineProcessor
from .stream import Stream


class StatementProcessor(LineProcessor):
    # Stream markers
    BLOCK_START = r'block-start'
    BLOCK_END = r'block-end'
    STMT_END = r'stmt-end'
    EXPR_GROUP_START = r'expr-group-start'
    EXPR_GROUP_END = r'expr-group-end'
    MACRO_START = r'macro-start'
    LINE_CONT = r'line-cont'
    CONTENT = r'content'

    def __init__(self, source):
        self.source = source
        self.match = re.compile(r'\(|\)|\{|\}|^#|\\$|\;')
        self.block_level = 0
        self.in_decl = False
        self.linenum = 0
        self.data = Stream(source + '-data')

    def stream(self):
        return self.data

    def process_line(self, line):
        matches = []
        pos = 0
        self.linenum += 1
        while True:
            match = self.match.search(line, pos)
            if match is None or match.start() == match.end():
                break
            matches.append(match)
            pos = match.end()
        return self.evaluate_matches(line, matches)

    def evaluate_matches(self, line, matches):
        if len(matches) == 0:
            self.emit(0, line)
            return
        pos = 0
        for m in matches:
            assert(m is not None)
            capture = line[pos:m.start()+1]
            token = line[m.start():m.end()]
            token_pos = m.start()
            if token is '{':
                self.emit(token_pos, capture)
                self.block_level += 1
                if self.block_level == 1:
                    self.emit_marker(token_pos, StatementProcessor.BLOCK_START)
            elif token is '}':
                self.emit(token_pos, capture)
                self.block_level -= 1
                if self.block_level == 0:
                    self.emit_marker(token_pos, StatementProcessor.BLOCK_END)
            elif token is ';':
                self.emit(token_pos, capture)
                self.emit_marker(token_pos, StatementProcessor.STMT_END)
            elif token is '(':
                self.emit(token_pos, capture)
                self.emit_marker(token_pos, StatementProcessor.EXPR_GROUP_START)
            elif token is ')':
                self.emit(token_pos, capture)
                self.emit_marker(token_pos, StatementProcessor.EXPR_GROUP_END)
            elif token is '\\':
                self.emit(token_pos, capture)
                self.emit_marker(token_pos, StatementProcessor.LINE_CONT)
            elif token is '#':
                self.emit(token_pos, capture)
                self.emit_marker(token_pos, StatementProcessor.MACRO_START)
            pos = m.end()
        return self

    def emit(self, pos, capture):
        print('[{}:{}#{}] "{}"'.format(self.data.name, self.linenum, pos, capture))
        self.data.append(self.linenum, pos, {'type': StatementProcessor.CONTENT, 'content': capture})

    def emit_marker(self, pos, marker):
        print('[{}:{}#{}] {}'.format(self.data.name, self.linenum, pos, marker))
        self.data.append(self.linenum, pos, {'type': marker})
