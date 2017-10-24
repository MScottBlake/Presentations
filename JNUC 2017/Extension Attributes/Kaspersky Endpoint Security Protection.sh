#!/bin/bash

RESULT=$(timeout 2 /usr/local/bin/kav status Protection | awk '/Protection/ {print $2}')

if [ "${RESULT}" = "" ]; then
    echo "<result>$(timeout 2 /usr/local/bin/kav status)</result>"
else
    echo "<result>${RESULT}</result>"
fi
