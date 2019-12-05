#!/usr/bin/env python3
import os
from docopt import docopt
from cxmeta.pipeline.source_module import Module, module_name
from cxmeta.pipeline.source_file import FileProcessor
from cxmeta.config.config_loader import ConfigLoader

USAGE = """
Usage:
  {command}.py [options] <source_file_or_dir>

  -h, --help                        Show this screen.
  --version                         Show the version
  -d, --debug                       Enable debug information

""".format(command=os.path.basename(__file__))


def main():
    args = docopt(USAGE)
    self_path = os.path.dirname(__file__)
    debug = args.get('--debug', True)
    if debug:
        for k, v in args.items():
            print("{} {}".format(k, v))

    source_path = args['<source_file_or_dir>']
    full_path = os.path.abspath(source_path)

    config = ConfigLoader(full_path).doc

    print("config: {}".format(config))

    if os.path.isdir(full_path):
        Module(full_path).process(debug=debug)
    elif os.path.isfile(full_path):
        FileProcessor(full_path).process()

if __name__ == '__main__':
    main()
