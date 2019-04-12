#!/bin/bash
success=0
fail=0
while IFS=, read -r col1 col2 col3
do
  {
  temp="${col1%\"}"
  temp="${temp#\"}"
  temp1="${col2%\"}"
  temp1="${temp1#\"}"
  temp2="${col3%\"}"
  temp2="${temp2#\"}"
  # echo $temp,$temp1,$temp2
  #replace="static/media/private"
  #new=${temp/static/$replace}
  #new_var="${new%/*}/"
  #echo $new,$new_var
  mkdir -p $temp2 &&  cp $temp $temp1 &&
  ((success++)) 
  echo temp 
  } || {
  ((fail++)) 
  echo "Error while moving file ", ${temp%\"}
  }
done < move.csv
echo "Move task completed. Successful : "$success" Failed: "$fail"