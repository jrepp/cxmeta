import re
import os
from typing import AnyStr

from .cxx_processor import (
    CxxProcessor,
    is_cxx_identifier,
    is_cxx_type,
    tokenize_cxx_identifiers,
)
from .stream import Stream, Chunk, InputFile, Processor, Atom


RST_DIRECTIVE_REGEXP = re.compile(r"\.\.(?P<name>\w+)\:\:\s+?(?P<value>\w+)")


WHITESPACE_REGEXP = re.compile(r"^\s+?")


def full_to_relative(module, source_full_path):
    """Convert the source file, making it relative to the output"""
    prefix = os.path.commonprefix([module.source.full_path, source_full_path])
    # Strip the common prefix and path separator
    return source_full_path[len(prefix) + 1 :]


def append_newline(lines, newline):
    """
    Convert consecutive newlines into a content-break (double newline)
    """
    content_break = newline * 2
    try:
        top = lines[-1]
        if top == newline:
            lines[-1] = content_break
        elif top == content_break:
            pass
        else:
            lines.append(newline)
    except IndexError:
        lines.append(newline)


class ChunkBuilder(object):
    def __init__(self):
        self.line_num = 0
        self.comment_justification = 0
        self.directives = dict()
        self.comments = list()
        self.statements = list()
        self.macros = list()
        self.types = list()
        self.names = list()

    def is_typedef(self):
        return r"typedef" in self.types

    def is_macro(self):
        return r"macro" in self.types

    def is_function(self):
        return r"function" in self.types

    def parse_rst_directive(self, value):
        match = RST_DIRECTIVE_REGEXP.match(value)
        name = match.group("name")
        value = match.group("value")
        assert match is not None
        assert name is not None
        assert value is not None
        self.directives[name] = value

    def parse_cxx_decls(self, value, in_expr_group):
        for token in tokenize_cxx_identifiers(value):
            if is_cxx_type(token):
                # Capture cxx specific types
                self.types.append(token)
            elif is_cxx_identifier(token) and not in_expr_group:
                # Capture name outside of parameter lists
                self.names.append(token)

    def add_comment(self, value: AnyStr):
        if not self.comments:
            self.comment_justification = len(value) - len(value.lstrip())
        self.comments.append(value[self.comment_justification :])

    def add_statement(self, value):
        self.statements.append(value)

    def build(self):
        # Skip chunks that are only whitespace
        comment_str = ("".join(self.comments)).strip()
        statement_str = ("".join(self.statements)).strip()
        if not comment_str or not statement_str:
            return None

        chunk = Chunk()
        chunk.line_num = self.line_num
        chunk.directives = self.directives
        chunk.comments = self.comments
        chunk.statements = self.statements
        chunk.types = self.types
        chunk.names = self.names
        return chunk


class Combiner(Processor):
    """
    The combiner takes stream data from cxx_processor and turns them into

    Tagged comment/statement blocks.
    """

    def __init__(self, project, module, source):
        Processor.__init__(self, project, source, InputFile, Chunk)
        self.proc = CxxProcessor(project, module, source)
        self.stream_data = Stream(source)
        self.builder = ChunkBuilder()
        self.in_comment = False
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

    def _finish_chunk(self):
        # Emit the chunk if it has a valid class name
        chunk = self.builder.build()
        if chunk is not None:
            if self.debug_chunks:
                print("[_finish_chunk]: {}".format(chunk))
            self.stream_data.append(chunk)
        # Start a new chunk
        self.builder = ChunkBuilder()

    def _block_start_handler(self, _):
        # Out
        self.block_level += 1

    def _block_end_handler(self, _):
        self.block_level -= 1
        if self.block_level < 0:
            print("[_block_end_handler]: unbalanced blocks")
            self.block_level = 0
        if self.block_level == 0:
            if not self.builder.is_typedef():
                # If the chunk is a typedef the block is part of a statement
                self._finish_chunk()

    def _statement_end_handler(self, _):
        if self.block_level == 0:
            self._finish_chunk()

    def _comment_start(self, atom: Atom):
        # The comment start marker will always be the first line of the chunk
        self.in_comment = True
        if not self.builder.line_num:
            self.builder.line_num = atom.line_num

    def _comment_end(self, _):
        self.in_comment = False

    def _content_handler(self, atom: Atom):
        value = atom.data[r"value"]
        if self.in_comment:
            # The first directive marks the chunk start
            stripped = value.strip()
            if stripped.startswith(".."):
                self.builder.parse_rst_directive(stripped)
            else:
                self.builder.add_comment(value)
        else:
            # Parse the content into types and names if it
            # occurs outside the top-level block
            if self.block_level == 0:
                self.builder.parse_cxx_decls(value, self.in_expr_group)
            self.builder.add_statement(value)

    def _default_handler(self, atom: Atom):
        if type(atom.data) is dict and atom.data.get(r"content") is not None:
            self._content_handler(self, atom)

    def _newline_handler(self, _):
        if self.in_comment:
            append_newline(self.builder.comments, self.newline)
        else:
            append_newline(self.builder.statements, self.newline)

    def _macro_handler(self, atom):
        self.builder.types.append("macro")
        self.builder.macros.append(atom.data.get("content"))

    def _expr_group_start(self, atom):
        self.in_expr_group = True

    def _expr_group_end(self, atom):
        self.in_expr_group = False
        if not self.builder.is_macro() and not self.builder.is_function():
            self.builder.types.append(r"function")

    def combine(self):
        handlers = {
            CxxProcessor.CONTENT: self._content_handler,
            CxxProcessor.COMMENT_START: self._comment_start,
            CxxProcessor.COMMENT_END: self._comment_end,
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
