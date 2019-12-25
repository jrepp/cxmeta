import os
from cxmeta.config import random_name


class StreamDatum(object):
    """
    Base type for all input and output data on a stream

    In general you shouldn't use StreamDatum instead look at sub-types
    of StreamDatum such as: InputFile, Line and Chunk

    """
    def __init__(self):
        pass


class InputDirectory(StreamDatum):
    """
        A file coming through a stream. The file is local, specified
        by it's full path.
        """
    def __init__(self, full_path):
        StreamDatum.__init__(self)
        self.full_path = full_path

    def read(self):
        for name in os.listdir(self.full_path):
            yield InputFile(os.path.join(self.full_path, name))


class InputFile(StreamDatum):
    """
    A file coming through a stream. The file is local, specified
    by it's full path.
    """
    def __init__(self, full_path):
        StreamDatum.__init__(self)
        self.full_path = full_path

    def __str__(self):
        return self.full_path

    def read(self):
        with open(self.full_path, 'r') as open_file:
            line_num = 0
            for line in open_file.readlines():
                line_num += 1
                yield Line(line_num, line)


class InputBuffer(InputFile):
    """
    An input file that comes from a buffer
    """
    def __init__(self, name, buffer):
        InputFile.__init__(self, name)
        self.buffer = buffer

    def read(self):
        line_num = 0
        if type(self.buffer) is list:
            for line_data in self.buffer:
                line_num += 1
                yield Line(line_num, line_data)
        elif type(self.buffer) is str:
            for line_data in self.buffer.splitlines():
                line_num += 1
                yield Line(line_num, line_data)
        yield Line(1, '')


class OutputFile(StreamDatum):
    """
    A file coming out of the system ready to be written.
    """
    def __init__(self, full_path):
        StreamDatum.__init__(self)
        self.full_path = full_path
        self.chunks = list()


class Line(StreamDatum):
    """
    Represents a single line for example as an input to a line
    based processor.
    """
    def __init__(self, line_num, data):
        StreamDatum.__init__(self)
        self.line_num = line_num
        self.data = data

    def __str__(self):
        return "[Line] <line_num: {}, data: '{}'>".format(
            self.line_num, self.data)


class Atom(object):
    """
    Represents a parsed atom from a line
    """
    def __init__(self, line_num, pos, data):
        self.line_num = line_num
        self.pos = pos
        self.data = data

    def __str__(self):
        return "[Atom] loc: {}:{}, data: '{}'".format(
            self.line_num, self.pos, self.data)


class Chunk(object):
    """
    Represents a final chunk to be rendered
    """
    def __init__(self):
        self.comments = list()
        self.statements = list()
        self.types = list()
        self.names = list()
        self.directives = dict()
        self.line_num = 0

    def __str__(self):
        return "[Chunk] \
<line_num: {}, directives: {}, comments: {}, stmts: {}>".format(
            self.line_num, self.directives, len(self.comments), len(self.statements))


class Processor(object):
    def __init__(self, project, source, in_type, out_type):
        self.source = source
        self.project = project
        self.in_type = in_type
        self.out_type = out_type
        assert isinstance(source, in_type)

    def start_stream(self):
        pass

    # Returns 0 or more streams of content after processing
    def stream(self):
        return None


class Stream(object):
    """
    An ordered list of items produced from the generator read()
    """
    def __init__(self, name=None):
        self.name = name or random_name()
        self.content = list()

    def __str__(self):
        buffer = []
        for i in self.content:
            buffer.append(str(i))
        return '\n'.join(buffer)

    def is_empty(self):
        return len(self.content) == 0

    def read(self):
        for atom in self.content:
            yield atom

    def append(self, atom):
        self.content.append(atom)
