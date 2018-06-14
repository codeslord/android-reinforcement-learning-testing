#!/usr/bin/env bash

# Usage run.sh emulator app step ep

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APPDIR=/home/vagrant/subjects/
RESULTDIR=/vagrant/results/`hostname`/mytool/
TOOLDIR=/vagrant/android-reinforcement-learning-testing/src
STEP=30
EP=100

source $DIR/env.sh

cd $APPDIR

for p in `ls -d */`; do
#for p in `cat $DIR/projects2.txt`; do

    echo "Setting up AVD"
    setupEmu.sh $1

    echo "@@@ Processing project "$p
    mkdir -p $RESULTDIR$p
    cd $APPDIR$p

    app=`ls bin/*-debug.apk`
    apkName=`basename $app`
    echo "** PROCESSING APP " $app

    rm -rf $TOOLDIR/apps/*
#    cp bin/*-debug.apk $TOOLDIR/apps/
    adb install bin/*-debug.apk

    echo "** RUNNING MY TOOL FOR" $app
    cd $TOOLDIR
    python main.py emulator-5554 $app $STEP $EP

done
    #Logging

    #adb logcat -c