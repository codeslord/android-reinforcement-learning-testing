#! /bin/bash

i=0
while true
do
    sleep 60s
    echo $i
    adb shell am broadcast -a edu.gatech.m3.emma.COLLECT_COVERAGE
    adb pull /sdcard/coverage.ec ./coverage$i.ec
		sleep 1s
		java -cp emma.jar emma report -sp ../src/ -r txt,html -in ../bin/coverage.em -in ./coverage$i.ec -Dreport.html.out.file=./coverage$i.html
    (( i++))
done
