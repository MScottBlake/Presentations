#!/bin/bash

################################################################################
#
# VARIABLES
#

# Enter the protocol here. It should be smb, lpd, ipp, etc.
printserver_protocol="smb"

# Enter the shorthand name of the print server.
printserver_name="PRINTSVR_NAME"

# Enter the fully qualified domain name for the print server.
printserver_fqdn="printsvr_name.domain.com"

# Check to see if a value was passed in parameter 4. If so, assign to "printer_shortname".
[ "$4" != "" ] && printer_shortname=$4

# Check to see if a value was passed in parameter 5. If so, assign to "printer_location".
[ "$5" != "" ] && printer_location=$5

# Check to see if a value was passed in parameter 6. If so, assign to "driver_policy_trigger".
[ "$6" != "" ] && driver_policy_trigger=$6

# Check to see if a value was passed in parameter 7. If so, assign to "driver_ppd".
[ "$7" != "" ] && driver_ppd=$7

# Check to see if a value was passed in parameter 8. If so, assign to "option_1".
[ "$8" != "" ] && option_1=$8

# Check to see if a value was passed in parameter 9. If so, assign to "option_2".
[ "$9" != "" ] && option_2=$9

# Check to see if a value was passed in parameter 10. If so, assign to "option_3".
[ "${10}" != "" ] && option_3=${10}

# Check to see if a value was passed in parameter 11. If so, assign to "option_4".
[ "${11}" != "" ] && option_4=${11}

################################################################################
#
# ADDITIONAL VARIABLES - Do Not Edit
#

printername="${printserver_name}_${printer_shortname}"
gui_display_name="${printer_shortname} on ${printserver_name}"
address="${printserver_protocol}://${printserver_fqdn}/${printer_shortname}"

################################################################################
#
# Code
#

function DriverInstall() {
  # Trigger Jamf policy to (re)install drivers
  if [ ! -z "${driver_policy_trigger}" ]; then
    /usr/local/bin/jamf policy -event "${driver_policy_trigger}"
  fi

  # If driver PPD does not exist, fail and exit
  if [ ! -e "${driver_ppd}" ]; then
    /bin/echo "Driver not found at ${driver_ppd}."
    exit 1
  fi
}

function PrinterDelete() {
  # If printer already exists, remove it first
  if /usr/bin/lpstat -p "${printername}" > /dev/null 2>1; then
    /bin/echo "Existing printer found. Removing..."
    /usr/sbin/lpadmin -x "${printername}"
  fi
}

function PrinterInstall() {
  # Now we can install the printer.
  /usr/sbin/lpadmin \
    -p "${printername}" \
    -L "${printer_location}" \
    -D "${gui_display_name}" \
    -v "${address}" \
    -P "${driver_ppd}" \
    -o "${option_1}" \
    -o "${option_2}" \
    -o "${option_3}" \
    -o "${option_4}" \
    -o printer-error-policy=abort-job \
    -o auth-info-required=negotiate \
    -o printer-is-shared=false \
    -E

  result=$?
  if [ "${result}" -eq 0 ]; then
    /bin/echo "${printername} installed successfully."
  else
    exit "${result}"
  fi
}

function main() {
  DriverInstall
  PrinterDelete
  PrinterInstall
}

main
