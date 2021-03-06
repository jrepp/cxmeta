import sys
import os
import logging

from cxmeta.style.registry import get_style_type


def copy_header_to_output(header_file_path, output_file):
    copy_size = 8192
    with open(header_file_path, "r") as input_file:
        byte_data = input_file.read(copy_size)
        output_file.write(byte_data)


class GfmExporter(object):
    def __init__(self, project):
        self.log = logging.getLogger("cxmeta")
        self.project = project
        self.output = sys.stdout
        self.debug_export = project.config.get("debug_exporter", False)
        self.config = None
        self.output_path = project.output_path
        self.output_file_path = None  # computed path to current output file
        self.newline = project.newline
        assert self.newline is not None
        style_name = project.config.get("style")
        style_class = get_style_type(style_name)
        if style_class is None:
            raise ValueError(
                "Exporter style '{}' not supported.".format(style_name)
            )
        self.style = style_class()

    def open_output_for(self, module):
        # Get the final output file for the module
        output_file_name = self.project.config.get("output_file_name")
        if output_file_name:
            self.output_file_path = os.path.join(
                self.output_path, output_file_name
            )
        else:
            self.output_file_path = os.path.join(
                self.output_path, module.name + ".md"
            )
        self.log.info(
            "writing module {} to {}".format(module, self.output_file_path)
        )
        return open(self.output_file_path, "w+")

    def export_module(self, module):
        if self.debug_export:
            print("[export] exporting module: {}".format(module))

        # Create the output directories
        os.makedirs(self.output_path, exist_ok=True)

        with self.open_output_for(module) as output_file:
            if self.debug_export:
                print(
                    "[export] exporting module to: {}".format(
                        self.output_file_path
                    )
                )

            project_header = self.project.config.get("project_header")
            if project_header:
                header_full_path = os.path.join(
                    module.source.full_path, project_header
                )
                if self.debug_export:
                    print(
                        "[export] copying in project_header: {}".format(
                            header_full_path
                        )
                    )
                copy_header_to_output(header_full_path, output_file)
                output_file.write(self.newline * 2)

            output_file.write(self.style.start_module(module))

            # Export each file
            for source_file in module.files:
                self.export_source_file(output_file, module, source_file)

            output_file.write(self.style.end_module(module))

    def export_source_file(self, module_output_file, module, source_file):
        if self.project.config.get("publish_single_file"):
            if self.debug_export:
                print(
                    "[export] exporting source file: {} to module".format(
                        source_file
                    )
                )
            self.log.info(
                "writing source {} to {}".format(
                    source_file, self.output_file_path
                )
            )
            self.export_source_file_inner(
                module_output_file, module, source_file
            )
        else:
            # Convert to a markdown file in the output directory
            file_name, _ = os.path.splitext(source_file.project_relative_path)
            file_path = os.path.join(self.output_path, file_name + ".md")
            if self.debug_export:
                print(
                    "[export] exporting source file: {} to file {}".format(
                        source_file, file_path
                    )
                )
            with open(file_path, "w+") as output_file:
                self.log.info(
                    "writing source {} to {}".format(source_file, file_path)
                )
                self.export_source_file_inner(output_file, module, source_file)

    def export_source_file_inner(self, output_file, module, source_file):
        output_file.write(self.style.start_source_file(module, source_file))
        for chunk in source_file.stream().read():
            self.export_chunk(output_file, module, source_file, chunk)
        output_file.write(self.style.end_source_file(module, source_file))

    def export_chunk(self, output_file, module, source_file, chunk):
        if self.debug_export:
            print(
                "[export] exporting chunk: {} to file: {}".format(
                    chunk, self.output_file_path
                )
            )
        output_file.write(self.style.chunk(module, source_file, chunk))
