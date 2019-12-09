import re

from cxmeta.pipeline.stream import Stream, Processor, InputFile, Atom, Chunk


# Expression to find all parsable tokens in a line of C++
REGEXP = r'\(|\)|\{|\}|^#.*$|\\$|\;|(\/{2,})|(/\*{2,}/)|(/\*{1,})|(\*{1,}/)'


class CxxProcessor(Processor):
    """
    cxx_processor.Processors emits atoms into the stream with the following
    structure:
        <line, pos, data: { type:, content: }>
        type - one of the stream markers listed at the top of this file
        content - the content of the processed content from the file

    Note that newlines are treated as an event and not content.

    """
    # Stream markers
    BLOCK_START = r'block_start'
    BLOCK_END = r'block_end'
    STMT_END = r'stmt_end'
    EXPR_GROUP_START = r'expr_group_start'
    EXPR_GROUP_END = r'expr_group_end'
    MACRO = r'macro'
    LINE_CONT = r'line_cont'
    CONTENT = r'content'
    NEWLINE = r'newline'

    def __init__(self, project, modules, source):
        Processor.__init__(self, project, source, InputFile, Chunk)
        self.match = re.compile(REGEXP)
        self.block_level = 0
        self.in_decl = False
        self.stream_data = Stream(self.source)
        self.in_ml_comment = False
        self.in_comment = False
        self.line_num = 0
        self.debug_atoms = project.config.get('debug_atoms', False)
        self.debug_matches = project.config.get('debug_matches', False)

    def stream(self):
        return self.stream_data

    def process(self):
        for line in self.source.read():
            self.each_line(line)
        return self

    def each_line(self, line):
        matches = []
        pos = 0
        while True:
            match = self.match.search(line.data, pos)
            if match is None or match.start() == match.end():
                break
            matches.append(match)
            pos = match.end()

        self.line_num = line.line_num
        self.evaluate_matches(line.data, matches)

        return self

    def evaluate_matches(self, line, matches):
        if len(matches) == 0:
            self.emit(0, line)
            self.emit_marker(line, CxxProcessor.NEWLINE)
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
            if self.debug_matches:
                print("match: '{}', comment?: {}".format(
                    token, in_comment))
            if not in_comment:
                if token == '{':
                    self.emit(pos, capture_including(m.end()))
                    self.block_level += 1
                    if self.block_level == 1:
                        self.emit_marker(m.start(), CxxProcessor.BLOCK_START)
                elif token == '}':
                    self.emit(pos, capture_including(m.end()))
                    self.block_level -= 1
                    if self.block_level == 0:
                        self.emit_marker(m.start(), CxxProcessor.BLOCK_END)
                elif token == ';':
                    self.emit(pos, capture_including(m.end()))
                    self.emit_marker(m.start(), CxxProcessor.STMT_END)
                elif token == '(':
                    self.emit(pos, capture_including(m.end()))
                    self.emit_marker(m.start(), CxxProcessor.EXPR_GROUP_START)
                elif token == ')':
                    self.emit(pos, capture_including(m.end()))
                    self.emit_marker(m.start(), CxxProcessor.EXPR_GROUP_END)
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
                self.emit_marker(m.start(), CxxProcessor.LINE_CONT)
            elif token == '#':  # only matches at beginning of line
                self.emit_marker(m.start(), CxxProcessor.MACRO_START)
                self.emit(pos, capture_including(m.end()))
            else:
                self.emit(pos, capture_including(m.end()))
            pos = m.end()

        # write the remainder of the line if any
        capture = capture_remaining(pos)
        self.emit(pos, capture)
        self.emit_marker(pos + len(capture), CxxProcessor.NEWLINE)

        # line level comments always end when the line is finished
        self.in_comment = False

    def emit(self, pos, capture):
        if not capture:
            return
        is_comment = self.in_ml_comment | self.in_comment
        if self.debug_atoms:
            print('[Content] [{}:{}#{}] "{}" comment?: {}'.format(
                self.stream_data.name, self.line_num, pos, capture, is_comment))
        self.stream_data.append(Atom(
            self.line_num,
            pos,
            {r'type': CxxProcessor.CONTENT,
             r'is_comment': is_comment,
             r'content': capture}))

    def emit_macro(self, pos, capture):
        if self.debug_atoms:
            print('[Macro] [{}:{}#{}] "{}" comment?: {}'.format(
                self.stream_data.name, self.line_num, pos, capture, is_comment))
        self.stream_data.append(Atom(
            self.line_num,
            pos,
            {r'type': CxxProcessor.MACRO,
             r'content': capture}))

    def emit_marker(self, pos, marker):
        is_comment = self.in_ml_comment | self.in_comment
        if self.debug_atoms:
            print('[Marker] [{}:{}#{}] {} comment?: {}'.format(
                self.stream_data.name, self.line_num, pos, marker, is_comment))
        self.stream_data.append(Atom(
            self.line_num,
            pos,
            {'type': marker, 'is_comment': is_comment}))


