import re
import os

from .cxx_processor import CxxProcessor
from .stream import Stream, Chunk, InputFile, Processor


def full_to_relative(module, source_full_path):
    # Convert the source file, making it relative to the output
    prefix = os.path.commonprefix([
        module.source.full_path,
        source_full_path])
    # Strip the common prefix and path separator
    return source_full_path[len(prefix) + 1:]


class Combiner(Processor):
    """
    The combiner takes stream data from cxx_processor and turns them into

    Tagged comment/statement blocks.
    """
    def __init__(self, project, module, source):
        Processor.__init__(self, project, source, InputFile, Chunk)
        self.proc = CxxProcessor(project, module, source)
        self.stream_data = Stream(source)
        self.chunk = None
        self.comments = list()
        self.statements = list()
        self.macros = list()
        self.in_comment = False
        self.in_block = False
        self.newline = '\n'
        self.debug_chunks = project.config.get('debug_chunks', False)
        self.directive_expr = re.compile(r'\.\.(?P<name>\w+)\:\:\s+?(?P<value>\w+)')
        self.project_relative_path = full_to_relative(module, source.full_path)

    def __str__(self):
        return '[Combiner] <full_path: {}, chunks: {}>'.format(self.source.full_path, len(self.stream_data.content))

    def process(self):
        self.proc.process()
        self.combine()

    def process_directive(self, chunk, name, value):
        # rST directives can be added here
        if name == 'class':
            chunk.class_name = value
        chunk.directives[name] = value

    def _finish_chunk(self):
        # Emit the chunk if it has a valid class name
        if self.chunk.class_name:
            self.chunk.comment = ''.join(self.comments)
            self.chunk.stmt = ''.join(self.statements)

            if self.debug_chunks:
                print("[_finish_chunk]: {}".format(self.chunk))
            self.stream_data.append(self.chunk)

        # Start a new chunk
        self.chunk = Chunk()
        self.comments = list()
        self.statements = list()

    def _block_start_handler(self, _):
        # Out
        self.in_block = True

    def _block_end_handler(self, _):
        self.in_block = False
        self._finish_chunk()

    def _statement_end_handler(self, _):
        if not self.in_block:
            self._finish_chunk()

    def _content_handler(self, atom):
        content = atom.data[r'content']
        is_comment = atom.data[r'is_comment']
        if is_comment:
            if not self.in_comment:
                self._finish_chunk()
                self.in_comment = True

            # The first directive marks the chunk start
            stripped = content.strip()
            if stripped.startswith('..'):
                match = self.directive_expr.match(stripped)
                name = match.group('name')
                value = match.group('value')
                assert(match is not None)
                assert(name is not None)
                assert(value is not None)
                self.chunk.line_num = atom.line_num
                self.process_directive(self.chunk, name, value)
            else:
                self.comments.append(content)
        else:
            self.in_comment = False
            self.statements.append(atom.data[r'content'])

    def _default_handler(self, atom):
        if type(atom.data) is dict and atom.data.get(r'content') is not None:
            self._content_handler(self, atom)

    def _newline_handler(self, atom):
        if atom.data[r'is_comment']:
            self.comments.append(self.newline)
        else:
            self.statements.append(self.newline)

    def _macro_handler(self, atom):
        self.macros.append(atom.data.get('content'))

    def combine(self):
        self.chunk = Chunk()
        self.comments = list()
        self.statements = list()

        handlers = {
            r'content': self._content_handler,
            r'block_start': self._block_start_handler,
            r'block_end': self._block_end_handler,
            r'stmt_end': self._statement_end_handler,
            r'newline': self._newline_handler,
            r'macro': self._macro_handler
        }
        for atom in self.proc.stream().read():
            handler = handlers.get(atom.data[r'type']) or self._default_handler
            handler(atom)
        self._finish_chunk()

    def stream(self):
        return self.stream_data

