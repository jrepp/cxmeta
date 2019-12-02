import itertools

from .line_processor import LineProcessor
from .cxx_comments import CommentProcessor
from .cxx_statements import StatementProcessor


class Chunk(object):
    def __init__(self, comment, stmt):
        self.comment = comment
        self.stmt = stmt

    def __str__(self):
        return "{}\n{}".format(self.coment, self.stmt)


class Combiner(LineProcessor):
    def __init__(self, source):
        self.comment_proc = CommentProcessor(source)
        self.stmt_proc = StatementProcessor(source)
        self.comments = None
        self.stmts = None
        self.linenum = 0

    def process_line(self, line):
        self.comment_proc.process_line(line)
        self.stmt_proc.process_line(line)

    def combine(self):
        comments = self.comment_proc.stream().read()
        stmts = self.stmt_proc.stream().read()

        # discover chunks to extract from the comment stream
        for comment in comments:
            if not comment.data['content'].strip().startswith('..class::'):
                next

            # find the first related statement
            for stmt in itertools.takewhile(lambda x: x.linenum <= comment.linenum, stmts):
                pass

            # combine all comments up to first statement
            related_comments = list()
            related_comments.extend(itertools.takewhile(lambda x: x.linenum <= stmt.linenum, comments))

            # combine all statements till end of block
            related_stmts = list()
            related_stmts.extend(itertools.takewhile(lambda x: x.data['type'] != r'block-end', stmts))

            chunk = Chunk('\n'.join(comments), '\n'.join(stmts))
            self.stream.append(comment.linenum, 0, chunk)

    def stream(self):
        return self.stream

