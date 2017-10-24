#!/bin/bash

result=$(defaults read /path/to/custom.plist AutoUpdateSoftware)

if [ $result -eq 0 ]; then
    echo "<result>Disabled</result>"
else
    echo "<result>Enabled</result>"
fi
