import re

from cxmeta.pipeline.stream import (
    Stream,
    Processor,
    InputFile,
    Atom,
    Chunk,
    Line,
)

# Expression to find all parsable tokens in a line of C++
TOKEN_REGEXP = re.compile(
    r"\(|\)|\{|\}|^#.*$|\\$|\;|(\/{2,})|(/\*{2,}/)|(/\*{1,})|(\*{1,}/)"
)


# C identifier expression
IDENT_REGEXP = re.compile(r"[A-Za-z][\w:]*")


def is_cxx_type(content: str):
    """
    Returns true for content that declares a type
    """
    return content in ("enum", "struct", "class", "typedef")


def is_cxx_identifier(content: str):
    """
    Returns true for strings that are
    valid identifiers (e.g. function and type names)
    """
    m = IDENT_REGEXP.match(content)
    return m is not None and m.end() == len(content)


def tokenize_cxx_identifiers(content: str):
    """
    Returns a list of valid CXX identifier tokens
    such as function names
    """
    tokens = list()
    matches = IDENT_REGEXP.finditer(content)
    for i, match in enumerate(matches, start=1):
        tokens.append(match.group())
    return tokens


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
    BLOCK_START = r"block_start"
    BLOCK_END = r"block_end"
    STMT_END = r"stmt_end"
    EXPR_GROUP_START = r"expr_group_start"
    EXPR_GROUP_END = r"expr_group_end"
    MACRO = r"macro"
    LINE_CONT = r"line_cont"
    CONTENT = r"content"
    NEWLINE = r"newline"
    COMMENT_START = r"comment_start"
    COMMENT_END = r"comment_end"

    def __init__(self, project, modules, source):
        Processor.__init__(self, project, source, InputFile, Chunk)
        self.match = TOKEN_REGEXP
        self.in_decl: bool = False
        self.stream_data = Stream(self.source)
        self.in_ml_comment = False
        self.in_comment = False
        self.line_num: int = 0
        self.debug_atoms = project.config.get("debug_atoms", False)
        self.debug_matches = project.config.get("debug_matches", False)

    def stream(self):
        return self.stream_data

    def process(self):
        for line in self.source.read():
            self.each_line(line)
        return self

    def each_line(self, line: Line):
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
            self.emit_marker(len(line), CxxProcessor.NEWLINE)
            return

        pos = 0

        def capture_including(p):
            return line[pos:p]

        def capture_upto(p):
            return line[pos:p]

        def capture_remaining(p):
            return line[p:]

        for i, m in enumerate(matches):
            assert m is not None
            token = line[m.start() : m.end()]
            in_comment = self.in_comment | self.in_ml_comment
            if self.debug_matches:
                print("match: '{}', comment?: {}".format(token, in_comment))
            if not in_comment:
                if token == "{":
                    self.emit(pos, capture_including(m.end()))
                    self.emit_marker(m.start(), CxxProcessor.BLOCK_START)
                elif token == "}":
                    self.emit(pos, capture_including(m.end()))
                    self.emit_marker(m.start(), CxxProcessor.BLOCK_END)
                elif token == ";":
                    self.emit(pos, capture_including(m.end()))
                    self.emit_marker(m.start(), CxxProcessor.STMT_END)
                elif token == "(":
                    self.emit(pos, capture_including(m.end()))
                    self.emit_marker(m.start(), CxxProcessor.EXPR_GROUP_START)
                elif token == ")":
                    self.emit(pos, capture_including(m.end()))
                    self.emit_marker(m.start(), CxxProcessor.EXPR_GROUP_END)
                elif token.startswith("/*"):
                    assert self.in_ml_comment is False
                    # emit content up to the comment marker
                    self.emit(pos, capture_upto(m.start()))
                    self.in_ml_comment = True
                    self.emit_marker(pos, CxxProcessor.COMMENT_START)
                    # special case for /**/ (there is also a pattern
                    # match for this case)
                    if token.endswith(r"*/"):
                        self.in_ml_comment = False
                        self.emit_marker(m.end(), CxxProcessor.COMMENT_END)
                elif token.startswith("//"):
                    self.emit(pos, capture_upto(m.start()))
                    self.in_comment = True
                    self.emit_marker(pos, CxxProcessor.COMMENT_START)
            elif token.endswith("*/"):
                assert self.in_ml_comment is True
                self.emit(pos, capture_upto(m.start()))
                self.in_ml_comment = False
                self.emit_marker(pos, CxxProcessor.COMMENT_END)
            elif token == "\\":  # only matches at end of line
                self.emit(pos, capture_including(m.end()))
                self.emit_marker(m.start(), CxxProcessor.LINE_CONT)
            elif token == "#":  # only matches at beginning of line
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
        if self.in_comment and not self.in_ml_comment:
            self.in_comment = False
            self.emit_marker(pos + len(capture), CxxProcessor.COMMENT_END)

    def emit(self, pos: int, capture: int):
        if not capture:
            return
        is_comment = self.in_ml_comment | self.in_comment
        if self.debug_atoms:
            print(
                '[Content] [{}:{}#{}] "{}" comment?: {}'.format(
                    self.stream_data.name,
                    self.line_num,
                    pos,
                    capture,
                    is_comment,
                )
            )
        data = {r"type": CxxProcessor.CONTENT, r"value": capture}
        self.stream_data.append(Atom(self.line_num, pos, data))

    def emit_macro(self, pos, capture):
        if self.debug_atoms:
            print(
                '[Macro] [{}:{}#{}] "{}"'.format(
                    self.stream_data.name, self.line_num, pos, capture
                )
            )
        self.stream_data.append(
            Atom(
                self.line_num,
                pos,
                {r"type": CxxProcessor.MACRO, r"value": capture},
            )
        )

    def emit_marker(self, pos, marker):
        is_comment = self.in_ml_comment | self.in_comment
        if self.debug_atoms:
            print(
                "[Marker] [{}:{}#{}] {} comment?: {}".format(
                    self.stream_data.name,
                    self.line_num,
                    pos,
                    marker,
                    is_comment,
                )
            )
        self.stream_data.append(Atom(self.line_num, pos, {"type": marker}))
