

class LineProcessor(object):
    def process_lines(self, lines):
        if type(lines) is list:
            for l in lines:
                self.process_line(l)
        elif type(lines) is str:
            for l in lines.splitlines():
                self.process_line(l)

    # Interface for line-at-a-time processing pipeline
    def process_line(self, line):
        pass

    # Returns 0 or more streams of content after processing
    def streams(self):
        return list()
