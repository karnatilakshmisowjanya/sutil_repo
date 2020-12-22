#!/bin/bash

# This script generate a detailed changelog for the released changes to the seismic store sdutil tool

logname='../CHANGELOG.md'

printf "%s\n" "# Seismic Store sdutil Tool Change Log" > $logname

printf "%s\n" "The Change log contains all changes released to the seismic store sdutil tool." >> $logname

git log --pretty=format:'<li><a href="https://dev.azure.com/slb-des-ext-collaboration/open-data-ecosystem/_git/os-seismic-sdutil/commit/%H">%cd</a> %s</li>' --date=short | grep 'Merged PR' | awk '{$3=$4=$5=""; print $0}' | tr -s " " >> $logname