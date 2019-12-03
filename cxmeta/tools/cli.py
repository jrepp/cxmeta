#!/usr/bin/env python3
import os
from docopt import docopt
from cxmeta.pipeline.source_module import Module, module_name


USAGE = """
Usage:
  {command}.py [options] PATH

  -h, --help                        Show this screen.
  --version                         Show the version
  --include=<PATH>                  Include directory
  --define=<DEFINE>                 Define symbol value

""".format(command=os.path.basename(__file__))


def main():
    args = docopt(USAGE)
    self_path = os.path.dirname(__file__)
    for k, v in args.items():
        print("{} {}".format(k, v))
    source_path = args['<source_path>']

    module_path = os.path.join(self_path, source_path)
    Module(module_name(source_path)).each_file(module_path)


if __name__ == '__main__':
    main()
