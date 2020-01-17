from coreCube import CoreCube
import time
import bluepy
import sys

toio_addr = CoreCube.cubeSearch()
if len(toio_addr) == 0:
  print("コアキューブの電源を入れてください")
  sys.exit()

toio = CoreCube()
toio.connect(toio_addr[0])
time.sleep(1)

toio.moveTo(100, 100, 60)
toio.id()
print("(x, y) = (%d, %d)" % (toio.x, toio.y) )
toio.soundId(3)
time.sleep(1)

toio.moveTo(400, 400, 60)
toio.id()
print("(x, y) = (%d, %d)" % (toio.x, toio.y) )
toio.soundId(3)
time.sleep(1)

toio.moveTo(100, 300, 60)
toio.id()
print("(x, y) = (%d, %d)" % (toio.x, toio.y) )
toio.soundId(3)
time.sleep(1)

toio.moveTo(300, 100, 60)
toio.id()
print("(x, y) = (%d, %d)" % (toio.x, toio.y) )
toio.soundId(3)
time.sleep(1)

toio.disconnect()
