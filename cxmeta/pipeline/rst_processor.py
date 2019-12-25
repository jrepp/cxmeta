import docutils.nodes
import docutils.parsers.rst
import docutils.utils
import docutils.frontend

from cxmeta.pipeline.stream import Processor, Chunk


# RST parsing tip by: https://stackoverflow.com/users/4973698/mbdevpl
def parse_rst(text: str) -> docutils.nodes.document:
    parser = docutils.parsers.rst.Parser()
    components = (docutils.parsers.rst.Parser,)
    settings = docutils.frontend.OptionParser(
        components=components
    ).get_default_values()
    document = docutils.utils.new_document("<rst-doc>", settings=settings)
    parser.parse(text, document)
    return document


class MyVisitor(docutils.nodes.NodeVisitor):
    def visit_reference(self, node: docutils.nodes.reference) -> None:
        """Called for "reference" nodes."""
        print(node)

    def unknown_visit(self, node: docutils.nodes.Node) -> None:
        """Called for all other node types."""
        pass


class RstProcessor(Processor):
    def __init__(self, project, source):
        Processor.__init__(project, source, Chunk, Chunk)


if __name__ == "__main__":
    doc = parse_rst("spam spam lovely spam")
    visitor = MyVisitor(doc)
    doc.walk(visitor)
