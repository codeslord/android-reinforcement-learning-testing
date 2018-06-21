#!/bin/bash
APPDIR=~/Subjects/

if [ $# -eq 0 ]
  then
    echo "Usage: dumpCoverage.sh <outdir>"
    exit
fi

#for i in `seq 1 12`;
i=0
while true
do
  i=$((i+1))
  sleep 300 #sleep for 5 minutes
  adb shell am broadcast -a edu.gatech.m3.emma.COLLECT_COVERAGE
  adb pull /mnt/sdcard/coverage.ec $1/coverage$i.ec
  mkdir -p $1/coverage$i #output directory
  cd $1/coverage$i
  app= `basename $1`
  srcDir=$APPDIR/$app/src
  emFile=$1/coverage.em
  java -cp $ANDROID_HOME/tools/lib/emma.jar emma report -r txt,html,xml -sp $srcDir -in $emFile -in $1/coverage$i.ec
done
