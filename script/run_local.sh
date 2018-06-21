#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APPDIR=~/Subjects/
TOOLDIR=/Users/vuong/vagrant/androtest/android-reinforcement-learning-testing
RESULTDIR=/Users/vuong/vagrant/androtest/mytooloutput/


STEP=25
EP=200

#source $DIR/env.sh

cd $APPDIR

#for p in `ls -d */`; do
#for p in `cat $DIR/projects2.txt`; do
for p in `cat $DIR/one.txt`; do

    echo "Setting up AVD"
    cd $DIR
    ./setupEmu.sh android-19

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
    package=`~/Library/Android/sdk/build-tools/27.0.3/aapt d xmltree $app AndroidManifest.xml | grep package | awk 'BEGIN {FS="\""}{print $2}'`
    echo $package

    echo "** RUNNING LOGCAT"
    adb logcat &> $RESULTDIR$p/mytool.logcat &

    echo "** DUMPING INTERMEDIATE COVERAGE "
    cd $DIR
    ./dumpCoverage.sh $RESULTDIR$p &> $RESULTDIR$p/icoverage.log &

    echo "** RUNNING MY TOOL FOR" $package
    cd $TOOLDIR
    source activate android
    cd $TOOLDIR/src
    python main.py --recorda emulator-5554 $package $STEP $EP


    echo "-- FINISHED RUNNING MY TOOL"
    adb shell am broadcast -a edu.gatech.m3.emma.COLLECT_COVERAGE
    adb pull /mnt/sdcard/coverage.ec $RESULTDIR$p/coverage.ec

    NOW=$(date +"%m-%d-%Y-%H-%M")
    echo $NOW.$p >> $RESULTDIR/status.log

    killall dumpCoverage.sh
    killall adb

done