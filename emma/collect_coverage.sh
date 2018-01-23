#! /bin/bash

i=0
while true
do
    sleep 30s
    echo $i
    adb shell am broadcast -a edu.gatech.m3.emma.COLLECT_COVERAGE
    adb pull /sdcard/coverage.ec ./coverage$i.ec
    (( i++))
done
