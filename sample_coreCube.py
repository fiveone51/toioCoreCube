import bluepy
import time
import sys
from coreCube import CoreCube

if __name__ == "__main__":

  toio = CoreCube()
  if len(sys.argv) == 1:
    toio_addr = toio.cubeFinder()
    print("Connect to " + toio_addr)
  else:
    toio_addr = sys.argv[1]
  toio.connect(toio_addr)
  time.sleep(1)

  # Light は、(30ms, Red), (30ms, Green) を3回繰り返す
  # Sound は、(30ms,ド), (30ms,レ), (30ms,ミ) を2回繰り返す
  toio.lightSequence( 3, ( (30,(255,0,0)), (30,(0,255,0)) ) )
  toio.soundSequence( 2, ( (30,60), (30,62), (30,64) ) )
  time.sleep(2)

  # Light は Redを点灯
  # Sound は、id = 0 を再生
  toio.lightOn((255,0,0), 0)
  toio.soundId(0)
  time.sleep(1)

  # Light は Greenを点灯
  # Sound は、id = 1 を再生
  toio.lightOn((0,255,0), 0)
  toio.soundId(1)
  time.sleep(1)

  # Light は Bleuを点灯
  # Sound は、id = 2 を再生
  toio.lightOn((0,0,255), 0)
  toio.soundId(2)
  time.sleep(1)

  # 左右=(50,50)で進む
  # 左右=(-50,-50)で進む（後退する）
  # 左右 (50, -50)で進む（回転する）
  toio.lightOff()
  toio.motor((50, 50), 0)
  time.sleep(1)
  toio.motor((-50, -50), 0)
  time.sleep(1)
  toio.motor((50, -50), 0)
  time.sleep(1)
  toio.motor((0, 0), 0)
  time.sleep(1)

  # Battery/BLE Version 
  print("Battery: %d" % toio.battery())
  print("BLE Version : " + toio.bleVersion())

  # MATのID情報を毎秒10回読み取る
  print("Please put coreCube on MAT ...")
  for i in range(10,0,-1):
    id = toio.id()
    if id == 1:    print("%d: id=1 x=%d, y=%d, dir=%d" % (i, toio.x, toio.y, toio.dir))
    elif id == 2:  print("%d: id=2 stdid=%d, dir=%d" % (i, toio.stdid, toio.dir))
    else:          print("%d: id=%d" % (i, id))
    time.sleep(1)

  toio.disconnect()
