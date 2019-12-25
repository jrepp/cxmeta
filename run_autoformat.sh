#!/usr/bin/env bash

if [[ ! -x "autopep8" ]]; then
    echo autopep8 is not insalled
    exit 1
fi

function format_file() {
    filename=$1
    echo formatting $filename
    autopep8 --in-place $filename
}

for filename in `git ls-files '*.py'`;
do
    format_file $filename
done
