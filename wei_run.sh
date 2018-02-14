#!/usr/bin/env bash

step=10
ep=500

emulator -avd Galaxy_Nexus_API_23 -wipe-data &

sleep 60s

adb logcat -c

adb install apk/WeightChart.apk

cd src

python main.py emulator-5554 wei $step $ep