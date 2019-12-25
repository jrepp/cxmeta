#!/usr/bin/env bash
flake8 cxmeta \
    --show-source \
    --exclude=.git,__pycache__,build,dist,_output \
    --max-complexity=10
flake8 test
