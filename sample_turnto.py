from coreCube import CoreCube
import time
import bluepy
import sys

toio_addr = CoreCube.cubeSearch()
if len(toio_addr) != 1:
  print("1台のコアキューブの電源を入れてください")
  sys.exit()

toio = CoreCube()
#toio.connect(toio_addr[0], bluepy.btle.ADDR_TYPE_RANDOM)
toio.connect(toio_addr[0])
time.sleep(1)

for k in range(10):
  toio.turnTo(270)
  toio.id()
  print("dir = %d" % toio.dir)
  toio.soundId(4)
  time.sleep(2)

toio.soundStop()
toio.disconnect()
