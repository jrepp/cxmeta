#!/usr/bin/env bash

BLACK=$(which black)
if [[ ! -x "$BLACK" ]]; then
    echo black is not installed
    exit 1
fi

function format_file() {
    filename=$1
    echo formatting $filename
    $BLACK --line-length=79 $filename
}

for filename in `git ls-files '*.py'`;
do
    format_file $filename
done
