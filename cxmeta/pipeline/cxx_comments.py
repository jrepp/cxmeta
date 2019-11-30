import re


class CommentProcessor(object):
    def __init__(self):
        self.match = re.compile(r'')

    def process_line(self, line):
        return re.findall(line, self.match)
