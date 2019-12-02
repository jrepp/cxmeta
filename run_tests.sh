#!/usr/bin/env bash
pushd test
PYTHONPATH=.. python3 -m unittest discover
popd
