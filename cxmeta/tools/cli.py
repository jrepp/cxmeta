#!/usr/bin/env python3
import os
import sys
import logging
import colorlog  # type: ignore
from docopt import docopt  # type: ignore
from cxmeta.pipeline.builder import Builder
from cxmeta.config.config_loader import ConfigLoader, VALID_SETTINGS
from cxmeta.style.registry import STYLES

USAGE = """
Usage:
  {command}.py [options] <source_file_or_dir>

  -h, --help                        Show this screen.
  --version                         Show the version
  --help-config                     Show configuration help
  --help-styles                     Show available styles
  -d, --debug                       Enable debug information

""".format(
    command=os.path.basename(__file__)
)


def configure_logging():

    output = colorlog.StreamHandler()
    output.setLevel(logging.DEBUG)  # \033[1m
    output.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s %(levelname)-7s %(reset)s"
            "[%(black)s%(name)s%(reset)s] %(message)s"
        )
    )
    logger = logging.getLogger("cxmeta")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(output)
    return logger


def main():
    log = configure_logging()

    args = docopt(USAGE)
    debug = args.get("--debug", True)
    if debug:
        for k, v in args.items():
            log.debug("{} {}".format(k, v))

    # TODO: broken
    if args.get("--help-config"):
        for k, v in VALID_SETTINGS.items():
            log.info("{} {}".format(k, v))
            sys.exit(1)
    if args.get("--help-styles"):
        for k, v in STYLES.items():
            log.info("{} {}".format(k, v))
            sys.exit(1)

    source_path = args["<source_file_or_dir>"]
    full_path = os.path.abspath(source_path)

    # Load the project config, combine with arguments
    config = ConfigLoader(full_path).doc
    config.setdefault("settings", dict()).setdefault("debug", debug)
    log.info("project-config:")
    for k, v in config.items():
        log.info("  {}: {}".format(k, v))

    # Build the project object
    project = Builder().build_from_config(config)
    status = project.process()
    log.info("project-status: {}".format(status))
    # TODO: convert to attrs
    # for k, v in status.items():
    #   print("  {}: {}".format(k, v))


if __name__ == "__main__":
    main()
