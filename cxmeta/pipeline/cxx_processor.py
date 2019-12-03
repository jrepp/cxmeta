import re

from .line_processor import LineProcessor
from .stream import Stream


# Expression to find all parsable tokens in a line of C++
REGEXP = r'\(|\)|\{|\}|^#|\\$|\;|(\/{2,})|(/\*{2,}/)|(/\*{1,})|(\*{1,}/)'


class Processor(LineProcessor):
    # Stream markers
    BLOCK_START = r'block-start'
    BLOCK_END = r'block-end'
    STMT_END = r'stmt-end'
    EXPR_GROUP_START = r'expr-group-start'
    EXPR_GROUP_END = r'expr-group-end'
    MACRO_START = r'macro-start'
    LINE_CONT = r'line-cont'
    CONTENT = r'content'
    NEWLINE = r'newline'

    def __init__(self, source):
        self.source = source
        self.match = re.compile(REGEXP)
        self.block_level = 0
        self.in_decl = False
        self.line_num = 0
        self.stream_data = Stream(source)
        self.in_ml_comment = False
        self.in_comment = False

    def stream(self):
        return self.stream_data

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
        self.evaluate_matches(line, matches)
        return self

    def evaluate_matches(self, line, matches):
        if len(matches) == 0:
            self.emit(0, line)
            self.emit_marker(len(line), Processor.NEWLINE)
            return

        pos = 0

        def capture_including(p):
            return line[pos:p]

        def capture_upto(p):
            return line[pos:p]

        def capture_remaining(p):
            return line[p:]

        for i, m in enumerate(matches):
            assert(m is not None)

            token = line[m.start():m.end()]
            in_comment = self.in_comment | self.in_ml_comment
            # print("match: '{}' pos: {}, comment?: {}".format(
            #   token, token_pos, in_comment))
            if not in_comment:
                if token == '{':
                    self.emit(pos, capture_including(m.end()))
                    self.block_level += 1
                    if self.block_level == 1:
                        self.emit_marker(m.start(), Processor.BLOCK_START)
                elif token == '}':
                    self.emit(pos, capture_including(m.end()))
                    self.block_level -= 1
                    if self.block_level == 0:
                        self.emit_marker(m.start(), Processor.BLOCK_END)
                elif token == ';':
                    self.emit(pos, capture_including(m.end()))
                    self.emit_marker(m.start(), Processor.STMT_END)
                elif token == '(':
                    self.emit(pos, capture_including(m.end()))
                    self.emit_marker(m.start(), Processor.EXPR_GROUP_START)
                elif token == ')':
                    self.emit(pos, capture_including(m.end()))
                    self.emit_marker(m.start(), Processor.EXPR_GROUP_END)
                elif token.startswith('/*'):
                    assert (self.in_ml_comment is False)
                    # emit content up to the comment marker
                    self.emit(pos, capture_upto(m.start()))
                    self.in_ml_comment = True
                elif token.startswith('//'):
                    self.emit(pos, capture_upto(m.start()))
                    self.in_comment = True
            elif token.endswith('*/'):
                assert (self.in_ml_comment is True)
                self.emit(pos, capture_upto(m.start()))
                self.in_ml_comment = False
            elif token == '\\':  # only matches at end of line
                self.emit(pos, capture_including(m.end()))
                self.emit_marker(m.start(), Processor.LINE_CONT)
            elif token == '#':  # only matches at beginning of line
                self.emit(pos, capture_including(m.end()))
                self.emit_marker(m.start(), Processor.MACRO_START)
            else:
                self.emit(pos, capture_including(m.end()))
            pos = m.end()

        # write the remainder of the line if any
        capture = capture_remaining(pos)
        self.emit(pos, capture)
        self.emit_marker(pos + len(capture), Processor.NEWLINE)

        # line level comments always end when the line is finished
        self.in_comment = False

    def emit(self, pos, capture):
        if not capture:
            return
        is_comment = self.in_ml_comment | self.in_comment
        print('[{}:{}#{}] "{}" comment?: {}'.format(
            self.stream_data.name, self.line_num, pos, capture, is_comment))
        self.stream_data.append(
            self.line_num,
            pos,
            {r'type': Processor.CONTENT,
             r'comment': is_comment,
             r'content': capture})

    def emit_marker(self, pos, marker):
        is_comment = self.in_ml_comment | self.in_comment
        print('[{}:{}#{}] {} comment?: {}'.format(
            self.stream_data.name, self.line_num, pos, marker, is_comment))
        self.stream_data.append(
            self.line_num,
            pos,
            {'type': marker, 'comment': is_comment})
