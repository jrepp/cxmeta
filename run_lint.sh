#!/usr/bin/env bash
# Note that E203 issue should be resolved in flake8
# as black is doing the right thing:
# https://github.com/psf/black/issues/544
flake8 cxmeta \
    --show-source \
    --ignore=E203 \
    --exclude=.git,__pycache__,build,dist,_output \
    --max-complexity=10
flake8 test
