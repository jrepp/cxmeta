import re
import logging
import os

from .cxx_processor import (
    CxxProcessor,
    is_cxx_identifier,
    is_cxx_type,
    tokenize_cxx_identifiers,
)
from .stream import Stream, Chunk, InputFile, Processor, Atom


RST_DIRECTIVE_REGEXP = re.compile(r"\.\.(?P<name>\w+)::\s+?(?P<value>\w+)")


WHITESPACE_REGEXP = re.compile(r"^\s+?")


def full_to_relative(module, source_full_path):
    """Convert the source file, making it relative to the output"""
    prefix = os.path.commonprefix([module.source.full_path, source_full_path])
    # Strip the common prefix and path separator
    return source_full_path[len(prefix) + 1 :]


class ChunkBuilder(object):
    def __init__(self):
        self.line_num = 0
        self.left_justified_spaces = 0
        self.left_justified_pos = 0
        self.directives = dict()
        self.docs = list()
        self.code = list()
        self.macros = list()
        self.types = list()
        self.names = list()

    def is_typedef(self):
        return r"typedef" in self.types

    def is_macro(self):
        return r"macro" in self.types

    def is_function(self):
        return r"function" in self.types

    def has_docs(self):
        return len(self.docs) > 0

    def has_code(self):
        return len(self.code) > 0

    def parse_rst_directive(self, value):
        match = RST_DIRECTIVE_REGEXP.match(value)
        name = match.group("name")
        value = match.group("value")
        assert match is not None
        assert name is not None
        assert value is not None
        self.directives[name] = value

    def parse_cxx_decls(self, value, in_expr_group):
        """Convert the statement text into types and names"""
        for token in tokenize_cxx_identifiers(value):
            if is_cxx_type(token):
                # Capture cxx specific types
                self.types.append(token)
            elif is_cxx_identifier(token) and not in_expr_group:
                # Capture name outside of parameter lists
                self.names.append(token)

    def add_doc(self, atom: Atom):
        value = atom.data[r"value"]
        # Convert tabs to spaces
        value.replace("\t", "    ")

        # Do one time setup of docs section
        if not self.line_num:
            self.line_num = atom.line_num
            self.left_justified_spaces = len(value) - len(value.lstrip())
            self.left_justified_pos = atom.pos

        # Process rST directives
        stripped_value = value.lstrip()
        if stripped_value.startswith(".."):
            self.parse_rst_directive(stripped_value)

        # Remove leading whitespace of doc lines that are left aligned
        # with the original documentation line
        leading_spaces = len(value) - len(value.lstrip())
        should_justify = (
            atom.pos == self.left_justified_pos
            and leading_spaces >= self.left_justified_spaces
        )
        if should_justify:
            value = value[self.left_justified_spaces :]
        self.docs.append(value)

    def add_doc_newline(self, newline):
        """Turn consecutive newlines into content breaks"""
        content_break = newline * 2
        try:
            top = self.docs[-1]
            if top == newline:
                self.docs[-1] = content_break
            elif top == content_break:
                pass
            else:
                self.docs.append(newline)
        except IndexError:
            self.docs.append(newline)

    def add_code(self, value):
        self.code.append(value)

    def build(self):
        # Skip chunks that are only documented by whitespace
        if not ("".join(self.docs)).strip():
            return None

        chunk = Chunk()
        chunk.line_num = self.line_num
        chunk.directives = self.directives
        chunk.docs = self.docs
        chunk.code = self.code
        chunk.types = self.types
        chunk.names = self.names
        return chunk


class Combiner(Processor):
    """
    The combiner takes stream data from cxx_processor and turns them into

    Tagged comment/statement blocks.
    """

    STATE_NONE = "none"
    STATE_DOCS = "docs"
    STATE_CODE = "code"

    def __init__(self, project, module, source):
        Processor.__init__(self, project, source, InputFile, Chunk)
        self.log = logging.getLogger("cxmeta")
        self.proc = CxxProcessor(project, module, source)
        self.stream_data = Stream(source)
        self.state = Combiner.STATE_NONE
        self.builder = ChunkBuilder()
        self.in_comment = False
        self.last_doc_comment_line = 0
        self.last_stmt_line = 0
        self.in_expr_group = False
        self.newline = "\n"
        self.block_level = 0
        self.debug_chunks = project.config.get("debug_chunks", False)
        self.project_relative_path = full_to_relative(module, source.full_path)

    def __str__(self):
        return "[Combiner] <full_path: {}, chunks: {}>".format(
            self.source.full_path, len(self.stream_data.content)
        )

    def process(self):
        self.proc.process()
        self.combine()
        return self

    def _change_state(self, new_state):
        if self.debug_chunks:
            print("[_change_state]: {} -> {}".format(self.state, new_state))
        self.state = new_state

    def _finish_chunk(self):
        chunk = self.builder.build()
        if chunk is not None:
            if self.debug_chunks:
                print("[_finish_chunk]: {}".format(chunk))
            self.stream_data.append(chunk)
        self.builder = ChunkBuilder()
        self._change_state(Combiner.STATE_NONE)

    def _block_start_handler(self, _):
        if self.state == Combiner.STATE_CODE:
            self.block_level += 1

    def _block_end_handler(self, _):
        if self.state == Combiner.STATE_CODE:
            self.block_level -= 1

    def _statement_end_handler(self, atom):
        self.last_stmt_line = atom.line_num

    def _comment_start(self, atom: Atom):
        self.in_comment = True

        # Consider lines starting with comment lines as starting documentation
        if atom.pos == 0:
            self.last_doc_comment_line = atom.line_num
            if self.state == Combiner.STATE_NONE:
                self._change_state(Combiner.STATE_DOCS)

    def _comment_end(self, atom: Atom):
        self.in_comment = False

    def _comment_token(self, atom: Atom):
        if self.state == Combiner.STATE_CODE:
            self.builder.add_code(atom.data[r"value"])

    def _content_handler(self, atom: Atom):
        value = atom.data[r"value"]
        if self.state == Combiner.STATE_DOCS:
            # Content occurring right after documentation will be included
            # as code. Note that if the current line was "documentation"
            # last_doc_comment_line would be equal to atom.line_num
            if self.last_doc_comment_line == (atom.line_num - 1):
                self._change_state(Combiner.STATE_CODE)
            else:
                self.builder.add_doc(atom)

        if self.state == Combiner.STATE_CODE:
            # Parse statement data on line start into types
            if atom.pos == 0 and self.block_level == 0:
                self.builder.parse_cxx_decls(value, self.in_expr_group)
            self.builder.add_code(value)

    def _default_handler(self, atom: Atom):
        if type(atom.data) is dict and atom.data.get(r"content") is not None:
            self._content_handler(atom)

    def _newline_handler(self, atom: Atom):
        if self.state == Combiner.STATE_DOCS:
            # Empty line
            if atom.pos == 0:
                self._finish_chunk()
            else:
                self.builder.add_doc_newline(self.newline)
        elif self.state == Combiner.STATE_CODE:
            # Empty line when block enclosed
            if atom.pos == 0 and self.block_level == 0:
                self._finish_chunk()
            else:
                self.builder.add_code(self.newline)

    def _macro_handler(self, atom):
        self.builder.types.append("macro")
        self.builder.macros.append(atom.data.get("content"))

    def _expr_group_start(self, _):
        self.in_expr_group = True

    def _expr_group_end(self, _):
        self.in_expr_group = False
        if not self.builder.is_macro() and not self.builder.is_function():
            self.builder.types.append(r"function")

    def combine(self):
        handlers = {
            CxxProcessor.CONTENT: self._content_handler,
            CxxProcessor.COMMENT_START: self._comment_start,
            CxxProcessor.COMMENT_END: self._comment_end,
            CxxProcessor.COMMENT_TOKEN: self._comment_token,
            CxxProcessor.BLOCK_START: self._block_start_handler,
            CxxProcessor.BLOCK_END: self._block_end_handler,
            CxxProcessor.STMT_END: self._statement_end_handler,
            CxxProcessor.NEWLINE: self._newline_handler,
            CxxProcessor.MACRO: self._macro_handler,
            CxxProcessor.EXPR_GROUP_START: self._expr_group_start,
            CxxProcessor.EXPR_GROUP_END: self._expr_group_end,
        }
        self.builder = ChunkBuilder()
        for atom in self.proc.stream().read():
            handler = handlers.get(atom.data[r"type"]) or self._default_handler
            handler(atom)
        self._finish_chunk()

    def stream(self):
        return self.stream_data
