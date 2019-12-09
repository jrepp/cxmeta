import sys
import os

from cxmeta.pipeline.source_module import module_name


def make_md_link(name, link):
    return '[{}]({})'.format(name, link)


class GhmStyle(object):
    """
    Abstract style renderer
    """
    def __init__(self, project):
        self.newline = project.newline
        self.indent = r'    '
        self.debug_export = project.config.get('debug_exporter', False)

    def start_module(self, module):
        return "# " + module.name + self.newline

    def end_module(self, module):
        return ''

    def start_source_file(self, module, source_file):
        source_name = module_name(source_file.source.full_path)
        return ''.join([
            "## " + source_name, self.newline, self.newline,
            self.indent,
            make_md_link(source_file.project_relative_path,
                         source_file.project_relative_path),
            self.newline, self.newline
        ])

    def end_source_file(self, module, source_file):
        return ''

    def chunk(self, module, source_file, chunk):
        export = [
            "### " + chunk.class_name, self.newline, self.newline,
            chunk.comment, self.newline]

        trimmed_stmt = chunk.stmt.strip()
        if trimmed_stmt:
            export.extend([
                '~~~c', self.newline,
                trimmed_stmt, self.newline,
                '~~~', self.newline, self.newline
            ])

        return ''.join(export)


class GhmExporter(object):
    def __init__(self, project):
        self.project = project
        self.output = sys.stdout
        self.debug_export = project.config.get('debug_exporter', False)
        self.config = None
        self.output_path = project.output_path
        self.output_file_path = None  # computed path to current output file
        self.newline = project.newline
        assert(self.newline is not None)
        self.style = GhmStyle(self.project)

    def export_module(self, module):
        if self.debug_export:
            print("exporting module: {}".format(module))

        # Create the output directories
        os.makedirs(self.output_path, exist_ok=True)

        # Get the final output file for the module
        self.output_file_path = os.path.join(
            self.output_path, module.name + '.md')

        with open(self.output_file_path, 'w+') as output_file:
            if self.debug_export:
                print("exporting module to: {}".format(self.output_file_path))

            output_file.write(self.style.start_module(module))

            # Export each file
            for source_file in module.files:
                self.export_source_file(output_file, module, source_file)

            output_file.write(self.style.end_module(module))

    def export_source_file(self, module_output_file, module, source_file):
        if not self.project.config.get('separate_source_files'):
            if self.debug_export:
                print("exporting source file: {} to module".format(source_file))
            self.export_source_file_inner(module_output_file, module, source_file)
        else:
            # Convert to a markdown file in the output directory
            file_name, _ = os.path.splitext(source_file.project_relative_path)
            file_path = os.path.join(self.output_path, file_name + '.md')
            if self.debug_export:
                print("exporting source file: {} to file {}".format(
                    source_file, file_path))
            with open(file_path, 'w+') as output_file:
                self.export_source_file_inner(output_file, module, source_file)

    def export_source_file_inner(self, output_file, module, source_file):
        output_file.write(self.style.start_source_file(module, source_file))
        for chunk in source_file.stream().read():
            self.export_chunk(output_file, module, source_file, chunk)
        output_file.write(self.style.end_source_file(module, source_file))

    def export_chunk(self, output_file, module, source_file, chunk):
        if self.debug_export:
            print("exporting chunk: {} to file: {}".format(chunk, self.output_file_path))
        output_file.write(self.style.chunk(module, source_file, chunk))
