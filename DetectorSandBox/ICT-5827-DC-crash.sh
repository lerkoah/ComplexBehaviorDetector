#!/bin/bash

FROM=$1
TO=$2
SEP="----------------------------------------------------------------------------------"
echo "ICT-5827 analysis from $FROM to $TO"
echo "$SEP"

INSTANCES="$(LogQuery.py -i aos64 -f $FROM -t $TO -c TimeStamp '"ACC/DATACAPTURER/javaContainer" AND  "timed-out several times"')"
echo "Instances:"
echo $INSTANCES | tr " " "\n"
echo

secondsBefore() {
  echo $(date -d @$(( $(date -d "$(echo $1 | tr "T" " ")" +"%s") - $2 )) +"%Y-%m-%dT%H:%M:%S.000")
}
secondsAfter() {
  echo $(date -d @$(( $(date -d "$(echo $1 | tr "T" " ")" +"%s") + $2 )) +"%Y-%m-%dT%H:%M:%S.000")
}

for TS in $INSTANCES; do
  export QK_FROMTIME=$(secondsBefore $TS 3600)
  export QK_TOTIME=$(secondsAfter $TS 3600)
  echo "$SEP"
  #echo "Logs between $QK_FROMTIME - $QK_TOTIME"
  echo "Logs around $TS"
  echo
  LogQuery.py -i aos64 -g DEBUG 'DATACAPTURER' -l 10 -r -c TimeStamp,LogLevel,Process,SourceObject,text -t $TS | tac 
  echo "# Problem detected here..."
  LogQuery.py -i aos64 -g DEBUG 'DATACAPTURER' -l 10 -c TimeStamp,LogLevel,Process,SourceObject,text -f $TS 
  echo
done
