import re
from .stream import Stream
from .line_processor import LineProcessor

class CommentProcessor(LineProcessor):
    def __init__(self, source):
        self.source = source
        self.match = re.compile(r'(//+)|(/\*+)|(\*+/)')
        self.comment_stream = Stream('{}-comment'.format(source))
        self.data_stream = Stream('{}-data'.format(source))
        self.in_ml_comment = False
        self.in_comment = False
        self.line_num = 0
        self.sequence = 0

    def __str__(self):
        return "CommentProcessor {} (in_comment: {}, in_ml_comment: {}, line_num: {}, sequence: {})".format(
            self.source, self.in_comment, self.in_ml_comment, self.line_num, self.sequence)

    def streams(self):
        return [self.comment_stream, self.data_stream]

    def process_line(self, line):
        matches = []
        pos = 0
        self.line_num += 1
        while True:
            match = self.match.search(line, pos)
            if match is None:
                break
            matches.append(match)
            pos = match.end()
        return self.evaluate_matches(line, matches)

    def evaluate_matches(self, line, matches):
        # the entire line is content
        if len(matches) == 0:
            self.emit(0, line)
            return self.streams()

        pos = 0
        for m in matches:
            assert(m is not None)

            # capture everything from the previous mark to the start of the match
            capture = line[pos:m.start()]
            if capture:
                self.emit(pos, capture)
            matched = line[m.start():m.end()]
            if matched.startswith('/*'):
                assert(self.in_ml_comment is False)
                self.in_ml_comment = True
                pos = m.end()
            elif matched.endswith('*/'):
                assert(self.in_ml_comment is True)
                self.in_ml_comment = False
                pos = m.end()
            elif matched.startswith('//'):
                pos = m.end()
                self.in_comment = True

        capture = line[pos:]
        if capture:
            self.emit(pos, capture)

        # line endings always end immediately
        self.in_comment = False
        return self.streams()

    def emit(self, pos, s):
        # print("{} <- ({}: '{}')".format(self, pos, s))
        self.sequence += 1
        if self.in_comment or self.in_ml_comment:
            self.comment_stream.append(self.sequence, pos, s)
        else:
            self.data_stream.append(self.sequence, pos, s)

