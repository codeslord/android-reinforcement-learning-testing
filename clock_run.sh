#!/usr/bin/env bash

step=10
ep=60

emulator -avd Galaxy_Nexus_API_23 -wipe-data &

sleep 60s

adb logcat -c

adb install apk/WorldClock.apk

cd src

python main.py emulator-5554 clock $step $ep