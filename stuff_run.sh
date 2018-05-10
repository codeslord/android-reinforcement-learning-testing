#!/usr/bin/env bash

step=5
ep=5

emulator -avd Galaxy_Nexus_API_23 -wipe-data &

sleep 60s

adb logcat -c

adb install apk/whohasmystuff-vm.apk

cd src

python main.py emulator-5554 stuff $step $ep
