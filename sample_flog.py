from coreCube import CoreCube
import time
import bluepy
import sys

toio_addr = CoreCube.cubeSearch()
if len(toio_addr) != 2:
  print("2台のコアキューブの電源を入れてください")
  sys.exit()

toio1 = CoreCube()
toio1.connect(toio_addr[0], bluepy.btle.ADDR_TYPE_RANDOM)

toio2 = CoreCube()
toio2.connect(toio_addr[1], bluepy.btle.ADDR_TYPE_RANDOM)

MELODY_LENGTH = 0.5
MELODY_FLOG = [60, 62, 64, 65, 64, 62, 60, 128, 64, 65, 67, 69, 67, 65, 64, 128, 60, 128, 60, 128, 60, 128, 60, 128, 60, 62, 64, 65, 64, 62, 60, 128, 128, 128, 128, 128, 128, 128, 128, 128]

time.sleep(1)

for i in range(len(MELODY_FLOG)):
  toio1.soundMono(0xFF, MELODY_FLOG[i])
  if i >=8:
    toio2.soundMono(0xFF, MELODY_FLOG[i-8])
  time.sleep(MELODY_LENGTH)

toio1.soundStop()
toio1.disconnect()
toio2.soundStop()
toio2.disconnect()
