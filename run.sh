#!/usr/bin/env bash

# Usage run.sh emulator app step ep
# Setting up emulator
export ANDROID_SDK_ROOT=/Users/tuyetvuong/Library/Android/

#echo "- Killing All Emulators"
#killall emulator64-x86
#
#echo "- Copying emulator template"
#cp -r ./avd_templates/$1.* ~/.android/avd/

echo "- Starting emulator"
emulator -avd $1 &

date1=$(date +"%s")

echo "- Waiting for emulator to boot"
OUT=`adb shell getprop init.svc.bootanim`
while [[ ${OUT:0:7}  != 'stopped' ]]; do
  OUT=`adb shell getprop init.svc.bootanim`
  echo '   Waiting for emulator to fully boot...'
  sleep 5
done

echo "Emulator booted!"

date2=$(date +"%s")
diff=$(($date2-$date1))
echo ".. Emulator boot took $(($diff / 60)) minutes and $(($diff % 60)) seconds."

#Logging

adb logcat -c

adb install apk/$1.apk

cd src

python main.py $1 $2 $3 $4
