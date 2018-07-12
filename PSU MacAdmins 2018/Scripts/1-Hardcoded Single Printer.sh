#!/bin/bash

/usr/sbin/lpadmin -p Sales_Printer -L "1st Floor, West Side" \
  -P /System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/PrintCore.framework/Versions/A/Resources/Generic.ppd \
  -v "ipp://192.168.5.5" -o printer-error-policy=abort-job \
  -o printer-is-shared=false -E
