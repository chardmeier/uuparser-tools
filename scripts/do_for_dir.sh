#!/bin/bash

for f in *; do
    if [ -f "$f" ]; then
        $1 $f
    fi
done
