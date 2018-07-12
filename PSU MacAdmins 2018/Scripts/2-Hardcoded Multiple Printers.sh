#!/bin/bash

/usr/sbin/lpadmin -p Sales_Printer -L "1st Floor, West Side" \
  -P /System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/PrintCore.framework/Versions/A/Resources/Generic.ppd \
  -v "ipp://192.168.5.5" -o printer-error-policy=abort-job \
  -o printer-is-shared=false -E

/usr/sbin/lpadmin -p Marketing_Printer -L "1st Floor, East Side" \
  -P /System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/PrintCore.framework/Versions/A/Resources/Generic.ppd \
  -v "ipp://172.16.10.10" -o printer-error-policy=abort-job \
  -o printer-is-shared=false -E

/usr/sbin/lpadmin -p Management_Printer -L "2nd Floor" \
  -P /System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/PrintCore.framework/Versions/A/Resources/Generic.ppd \
  -v "smb://printserver1.domain.com/MGTPrt1" \
  -o printer-error-policy=abort-job -o printer-is-shared=false \
  -o auth-info-required=negotiate -E
