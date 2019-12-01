import uuid


class Atom(object):
    def __init__(self, sequence, position, data):
        self.sequence = sequence
        self.position = position
        self.data = data

    def __str__(self):
        return "<seq: {}, pos: {}, data: '{}'>".format(
            self.sequence, self.position, self.data)


def random_name():
    return uuid.uuid4().split('-')[-1]


class Stream(object):
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

    def append(self, sequence, position, data):
        self.content.append(Atom(sequence, position, data))

