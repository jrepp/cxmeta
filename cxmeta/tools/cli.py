#!/usr/bin/env python3
import os
import logging
from docopt import docopt
from cxmeta.pipeline.builder import Builder
from cxmeta.config.config_loader import ConfigLoader


USAGE = """
Usage:
  {command}.py [options] <source_file_or_dir>

  -h, --help                        Show this screen.
  --version                         Show the version
  -d, --debug                       Enable debug information

""".format(
    command=os.path.basename(__file__)
)


def main():
    logging.basicConfig(filename=None, level=logging.DEBUG)
    args = docopt(USAGE)
    debug = args.get("--debug", True)
    if debug:
        for k, v in args.items():
            print("{} {}".format(k, v))

    source_path = args["<source_file_or_dir>"]
    full_path = os.path.abspath(source_path)

    # Load the project config, combine with arguments
    config = ConfigLoader(full_path).doc
    config.setdefault("settings", dict()).setdefault("debug", debug)
    print("project_config: {}".format(config))

    # Build the project object
    project = Builder().build_from_config(config)
    print(project.process())


if __name__ == "__main__":
    main()
