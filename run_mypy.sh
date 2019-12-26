#!/usr/bin/env bash

MYPY=$(which mypy)
if [[ ! -x "$MYPY" ]]; then
    echo mypy is not installed
    exit 1
fi

function check_file() {
    filename=$1
    echo checking $filename
    $MYPY $filename
}

for filename in `git ls-files '*.py'`;
do
    check_file $filename
done
