import bluepy
import os

# 周辺にある toio コアキューブを見つけ、address を表示します。
# このコマンドは、root で実行する必要があります。
if os.environ.get('USER') == 'root':
  scaner = bluepy.btle.Scanner(0)
  devices = scaner.scan(3)

  finds =0
  for device in devices:
    for (adType, desc, value) in device.getScanData():
      if "toio Core Cube" in value:
        finds = finds + 1
        print('toio Core Cube  Address=%s ,  RSSI=%s' % (device.addr, device.rssi))
  if finds == 0:
    print('toio core cube is not found.')
else:
  print('You need to execute this command as root')
