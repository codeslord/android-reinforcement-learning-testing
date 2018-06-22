#!/bin/bash

echo "- Killing All Emulators"
#killall emulator64-x86
adb -s emulator-5554 emu kill
pkill -f emulator

#echo "- Deleting Emulator" $1
#android delete avd -n $1
#
#echo "- Copying emulator template"
#cp -r ./avd_templates/$1.* ~/.android/avd/

echo "- Starting emulator"

~/Library/Android/sdk/emulator/emulator -avd $1 -wipe-data &

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
