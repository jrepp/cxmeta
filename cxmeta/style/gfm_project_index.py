from cxmeta.style.gfm_common import GfmStyle, cxmeta_footer, make_md_link
from cxmeta.pipeline.stream import Chunk
from cxmeta.pipeline.source_module import Module
from cxmeta.pipeline.source_module import module_name
from cxmeta.pipeline.combiner import Combiner


class GfmProjectIndexStyle(GfmStyle):
    """
    Abstract style renderer
    """

    def __init__(self, project):
        self.newline = project.newline
        self.indent = r"    "
        self.debug_export = project.config.get("debug_exporter", False)

    def start_module(self, module: Module) -> str:
        return "# " + module.name + self.newline

    def end_module(self, module):
        return cxmeta_footer()

    def start_source_file(self, module: Module, source_file: Combiner) -> str:
        source_name = module_name(source_file.source.full_path)
        return "".join(
            [
                "### " + source_name,
                self.newline,
                self.newline,
                make_md_link(
                    source_file.project_relative_path,
                    source_file.project_relative_path,
                ),
                self.newline,
                self.newline,
            ]
        )

    def end_source_file(self, module: Module, source_file: Combiner) -> str:
        return ""

    def chunk(
        self, module: Module, source_file: Combiner, chunk: Chunk
    ) -> str:
        export = [
            "#### ",
            "`",
            chunk.names[-1],
            "` (",
            " ".join(chunk.types),
            ")",
            self.newline,
            self.newline,
            "".join(chunk.comments),
            self.newline,
        ]

        trimmed_stmt = "".join(chunk.statements).strip()
        if trimmed_stmt:
            export.extend(
                [
                    "~~~c",
                    self.newline,
                    trimmed_stmt,
                    self.newline,
                    "~~~",
                    self.newline,
                    self.newline,
                ]
            )

        return "".join(export)
