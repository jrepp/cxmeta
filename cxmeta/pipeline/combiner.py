from .line_processor import LineProcessor
from .cxx_processor import Processor
from .stream import Stream


class Chunk(object):
    def __init__(self):
        self.comment = None
        self.stmt = None
        self.class_name = None
        self.line_num = 0

    def __str__(self):
        return "COMMENTS: {}\nSTATEMENTS: {}\n".format(self.comment, self.stmt)


class Combiner(LineProcessor):
    def __init__(self, source):
        self.proc = Processor(source)
        self.stream_data = Stream(source)
        self.chunk = None
        self.comments = list()
        self.statements = list()
        self.in_comment = False
        self.newline = '\n'

    def process_line(self, line):
        self.proc.process_line(line)

    def _finish_chunk(self):
        if self.chunk.class_name:
            self.chunk.comment = ''.join(self.comments)
            self.chunk.stmt = ''.join(self.statements)
            self.stream_data.append(self.chunk.line_num, 0, self.chunk)
            self.chunk = Chunk()
            self.comments = list()
            self.statements = list()

    def _block_end_handler(self, _):
        self._finish_chunk()

    def _statement_end_handler(self, _):
        self._finish_chunk()

    def _content_handler(self, atom):
        content = atom.data[r'content']
        comment = atom.data[r'comment']
        if comment:
            if not self.in_comment:
                self._finish_chunk()
                self.in_comment = True

            self.comments.append(content)
            if content.strip().startswith('..class::'):
                self.chunk.class_name = content.split('::')[-1].strip()
                self.chunk.line_num = atom.line_num
        else:
            self.in_comment = False
            self.statements.append(atom.data[r'content'])

    def _default_handler(self, atom):
        if type(atom.data) is dict:
            content = atom.data.get(r'content')
            if content:
                self.statements.append(content)

    def _newline_handler(self, atom):
        if atom.data[r'comment']:
            self.comments.append(self.newline)
        else:
            self.statements.append(self.newline)

    def combine(self):
        self.chunk = Chunk()
        self.comments = list()
        self.statements = list()

        handlers = {
            r'content': self._content_handler,
            r'block-end': self._block_end_handler,
            r'stmt-end': self._statement_end_handler,
            r'newline': self._newline_handler
        }
        for atom in self.proc.stream().read():
            handler = handlers.get(atom.data[r'type']) or self._default_handler
            handler(atom)
        self._finish_chunk()

    def stream(self):
        return self.stream_data
