#!/usr/bin/env bash

# Usage run.sh emulator app step ep
# Setting up emulator
export ANDROID_SDK_ROOT=~/Library/Android/sdk

echo "Setting up AVD"
./setupEmu.sh $1

#Logging

adb logcat -c

adb install apk/$2.apk

cd src

python main.py emulator-5554 $2 $3 $4
