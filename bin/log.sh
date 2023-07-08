#!/usr/bin/bash
export TZ="Asia/Hong_Kong"

LOGFILE=`date +"log/$1-%Y%m%d-%H%M.txt"`
echo "Archiving on logfile $LOGFILE ..."
script -f -c "python $2" $LOGFILE

