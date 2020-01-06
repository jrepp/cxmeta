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
    COMMENT_TOKEN = r"comment_token"

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
        self.line_num = line.line_num
        while True:
            match = self.match.search(line.data, pos)
            if match is None or match.start() == match.end():
                break
            matches.append(match)
            pos = match.end()
        if len(matches) == 0:
            self.emit_content(0, line.data)
            self.emit_marker(len(line.data), CxxProcessor.NEWLINE)
        else:
            self.evaluate_matches(line.data, matches)
        return self

    def evaluate_matches(self, line, matches):
        pos = 0
        for match in matches:
            token = line[match.start() : match.end()]
            in_comment = self.in_comment | self.in_ml_comment
            if self.debug_matches:
                print("match: '{}', comment?: {}".format(token, in_comment))
            if not in_comment:
                self.evaluate_in_statement(pos, match, line, token)
            else:
                self.evaluate_in_comment(pos, match, line, token)
            pos = match.end()

        # write the remainder of the line if any, stripping embedded newlines
        capture = line[pos:].rstrip("\r\n")
        self.emit_content(pos, capture)
        self.emit_marker(pos + len(capture), CxxProcessor.NEWLINE)

        # line level comments always end when the line is finished
        if self.in_comment and not self.in_ml_comment:
            self.in_comment = False
            self.emit_marker(pos + len(capture), CxxProcessor.COMMENT_END)

    def evaluate_in_statement(self, pos, match, line, token):
        def capture_including_end(atom_type):
            self.emit_content(pos, line[pos : match.end()])
            self.emit_marker(match.start(), atom_type)

        if token == r"{":
            capture_including_end(CxxProcessor.BLOCK_START)
        elif token == r"}":
            capture_including_end(CxxProcessor.BLOCK_END)
        elif token == r";":
            capture_including_end(CxxProcessor.STMT_END)
        elif token == r"(":
            capture_including_end(CxxProcessor.EXPR_GROUP_START)
        elif token == r")":
            capture_including_end(CxxProcessor.EXPR_GROUP_END)
        elif token.startswith(r"/*"):
            self.emit_content(pos, line[pos : match.start()])
            pos = match.start()
            self.in_ml_comment = True
            self.emit_marker(pos, CxxProcessor.COMMENT_START)
            self.emit_comment_token(pos, line[pos : match.end()])
            # special case for /**/
            if token.endswith(r"*/"):
                self.in_ml_comment = False
                self.emit_marker(match.end(), CxxProcessor.COMMENT_END)
        elif token.startswith(r"//"):
            self.emit_content(pos, line[pos : match.start()])
            pos = match.start()
            self.in_comment = True
            self.emit_marker(pos, CxxProcessor.COMMENT_START)
            self.emit_comment_token(pos, line[pos : match.end()])
        elif token.startswith(r"#"):
            self.emit_macro(pos, token)

    def evaluate_in_comment(self, pos, match, line, token):
        def capture_including_end(atom_type):
            self.emit_content(pos, line[pos : match.end()])
            self.emit_marker(match.start(), atom_type)

        if token.endswith(r"*/"):
            self.emit_content(pos, line[pos : match.start()])
            pos = match.start()
            self.emit_comment_token(pos, line[pos : match.end()])
            self.in_ml_comment = False
            self.emit_marker(pos, CxxProcessor.COMMENT_END)
        elif token == r"\\":  # only matches at end of line
            capture_including_end(CxxProcessor.LINE_CONT)
        elif token == r"#":  # only matches at beginning of line
            capture_including_end(CxxProcessor.MACRO_START)
        else:
            self.emit_content(pos, line[pos : match.end()])

    def emit(self, pos: int, **kwargs):
        is_comment = self.in_ml_comment | self.in_comment
        if self.debug_atoms:
            print(
                '[{}] [{}:{}#{}] "{}" comment?: {}'.format(
                    kwargs["type"],
                    self.stream_data.name,
                    self.line_num,
                    pos,
                    kwargs.get(r"value", r""),
                    is_comment,
                )
            )
        self.stream_data.append(Atom(self.line_num, pos, kwargs))

    def emit_content(self, pos: int, value: str):
        if len(value) == 0:
            return
        self.emit(pos, type=CxxProcessor.CONTENT, value=value)

    def emit_macro(self, pos: int, value: str):
        self.emit(pos, type=CxxProcessor.MACRO, value=value)

    def emit_comment_token(self, pos: int, value: str):
        self.emit(pos, type=CxxProcessor.COMMENT_TOKEN, value=value)

    def emit_marker(self, pos: int, marker: str):
        self.emit(pos, type=marker)
