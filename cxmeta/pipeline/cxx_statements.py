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

    def __init__(self, source):
        self.source = source
        self.match = re.compile(r'\(|\)|\{|\}|^#|\\$|\;')
        self.block_level = 0
        self.in_decl = False
        self.line_num = 0
        self.seq = 0
        self.data = Stream(source + '-data')
        self.markers = Stream(source + '-markers')

    def process_line(self, line):
        matches = []
        pos = 0
        self.line_num += 1
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

    def emit(self, pos, capture):
        print('[{}:{}#{}] "{}"'.format(self.data.name, self.line_num, pos, capture))
        self.data.append(self.seq, pos, capture)
        self.seq += 1

    def emit_marker(self, pos, marker):
        print('[{}:{}#{}] {}'.format(self.markers.name, self.line_num, pos, marker))
        self.markers.append(self.seq, pos, marker)
        self.seq += 1
