#!/usr/bin/env bash

if [[ -x "/usr/local/bin/gsed" ]]; then
    SED=/usr/local/bin/gsed
else
    SED=sed
fi

function trim_file() {
    filename=$1
    echo $SED $filename
    $SED --in-place 's/[[:space:]]\+$//' $filename
}

for filename in `git ls-files '*.py' '*.c' '*.h' '*.md'`;
do
    trim_file $filename
done
