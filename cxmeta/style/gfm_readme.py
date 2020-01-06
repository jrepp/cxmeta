from cxmeta.style.gfm_common import GfmStyle
from cxmeta.pipeline.stream import Chunk
from cxmeta.pipeline.source_module import Module
from cxmeta.pipeline.combiner import Combiner


class GfmReadmeStyle(GfmStyle):
    def __init__(self):
        self.newline = None

    def start_module(self, module: Module) -> str:
        self.newline = module.project.newline
        return ""

    def end_module(self, module: Module) -> str:
        return ""

    def start_source_file(self, module: Module, source_file: Combiner) -> str:
        return ""

    def end_source_file(self, module: Module, source_file: Combiner) -> str:
        return ""

    def chunk(
        self, module: Module, source_file: Combiner, chunk: Chunk
    ) -> str:
        buffer = list()
        # Make a simple chunk title out of any proper names
        if chunk.names:
            buffer += [ "### ", ' '.join(chunk.names), self.newline, self.newline ]

        # Main document section
        buffer += ["".join(chunk.docs)]

        # Additional code section
        if chunk.code:
            buffer += [
                self.newline,
                "```c",
                self.newline,
                "".join(chunk.code).rstrip(),
                self.newline,
                "```",
                self.newline,
                self.newline]
        return "".join(buffer)
