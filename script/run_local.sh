#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APPDIR=~/subjects/
TOOLDIR=~/vagrant/androtest/android-reinforcement-learning-testing
RESULTDIR=~/mytooloutput/


STEP=25
EP=200

#source $DIR/env.sh

cd $APPDIR

#for p in `ls -d */`; do
 for p in `cat $DIR/projects2.txt`; do
#for p in `cat $DIR/one.txt`; do

    echo "Setting up AVD"
    cd $DIR
    ./setupEmu.sh android-23

    echo "@@@@@@ Processing project " $p "@@@@@@@"
    mkdir -p $RESULTDIR$p
    cd $APPDIR$p
    echo "** BUILDING APP " $p
    #ant clean
    #ant emma debug install &> $RESULTDIR$p/build.log
    #ant installd &> $RESULTDIR$p/install.log
    cp bin/coverage.em $RESULTDIR$p/
    app=`ls bin/*-debug.apk`
    adb install bin/*-debug.apk
    echo "** PROCESSING APP " $app
    package=`aapt d xmltree $app AndroidManifest.xml | grep package | awk 'BEGIN {FS="\""}{print $2}'`
    echo $package

    echo "** RUNNING LOGCAT"
    adb logcat &> $RESULTDIR$p/logcat.log &

    echo "** DUMPING INTERMEDIATE COVERAGE "
    cd $DIR
    ./dumpCoverage.sh $RESULTDIR$p &> $RESULTDIR$p/icoverage.log &

    echo "** RUNNING MY TOOL FOR" $package
    cd $TOOLDIR
    source activate android
    cd $TOOLDIR/src
    python main.py emulator-5554 $package $STEP $EP


    echo "-- FINISHED RUNNING MY TOOL"
    adb shell am broadcast -a edu.gatech.m3.emma.COLLECT_COVERAGE
    adb pull /mnt/sdcard/coverage.ec $RESULTDIR$p/coverage.ec

    NOW=$(date +"%m-%d-%Y-%H-%M")
    echo $NOW.$p >> $RESULTDIR/status.log

    killall dumpCoverage.sh
    killall adb
    pkill -f dumpCoverage.sh
    pkill -f adb
    pkill -f sleep

    echo "- Killing All Emulators"
    #killall emulator
    adb devices | grep emulator | cut -f1 | while read line; do adb -s $line emu kill; done
    adb -s emulator-5554 emu kill

    mv $TOOLDIR/src/mytool.log $RESULTDIR$p/

    sleep 10


done