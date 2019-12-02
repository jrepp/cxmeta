import itertools

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

    def process_line(self, line):
        self.proc.process_line(line)

    def finish_chunk(self):
        if self.chunk.class_name:
            self.chunk.comment = ''.join(self.comments)
            self.chunk.stmt = ''.join(self.statements)
            self.stream_data.append(self.chunk.line_num, 0, self.chunk)
            self.chunk = Chunk()
            self.comments = list()
            self.statements = list()

    def comment_handler(self, atom):
        content = atom.data[r'content']
        self.comments.append(content)
        if content.strip().startswith('..class::'):
            self.chunk.class_name = content.split('::')[-1].strip()
            self.chunk.line_num = atom.line_num

    def block_end_handler(self, _):
        self.finish_chunk()

    def statement_end_handler(self, _):
        self.finish_chunk()

    def content_handler(self, atom):
        self.statements.append(atom.data[r'content'])

    def default_handler(self, atom):
        if type(atom.data) is dict:
            content = atom.data.get(r'content')
            if content:
                self.statements.append(content)

    def combine(self):
        self.chunk = Chunk()
        self.comments = list()
        self.statements = list()

        handlers = {
            r'content': self.content_handler,
            r'comment': self.comment_handler,
            r'block-end': self.block_end_handler,
            r'stmt-end': self.statement_end_handler,
        }
        for atom in self.proc.stream().read():
            handler = handlers.get(atom.data[r'type']) or self.default_handler
            handler(atom)

    def stream(self):
        return self.stream_data

