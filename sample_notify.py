from coreCube import CoreCube
import time
import bluepy
import sys
import struct

class MyDelegate(bluepy.btle.DefaultDelegate):
    def __init__(self, params, ptoio):             # コンストラクタで対応するtoioを指定する
        bluepy.btle.DefaultDelegate.__init__(self)
        self.ctoio = ptoio

    # notify callback: cHandle で何のNotifyかを見分けて処理分岐
    def handleNotification(self, cHandle, data):
        # ------------- ボタン
        if cHandle == toio.HANDLE_TOIO_BTN:
          id, stat = struct.unpack('BB', data[0:2])
          if stat == 0x80:
            self.ctoio.soundId(2)
        # ------------- モーションセンサー
        if cHandle == toio.HANDLE_TOIO_SEN:
          id, horizon, collision = struct.unpack('BBB', data[0:3])
          print("SENSOR:   HORIZON={:02x}, COLLISION={:02x}".format(horizon, collision))
          if collision:
            self.ctoio.soundId(6)
        # ------------- IDセンサー
        if cHandle == toio.HANDLE_TOIO_ID:
          id = struct.unpack('b', data[0:1])[0]
          if id == 0x01:
            x, y, dir = struct.unpack('hhh', data[1:7])
            print("X,Y,dir = (%d,%d), %d" % (x,y,dir))
          elif id == 0x02:
            stdid = struct.unpack('i', data[1:5])[0]
            dir = struct.unpack('h', data[5:7])[0]
            print("ID = %d,  dir = %d" % (stdid,dir))

if __name__ == "__main__":

  # --- コアキューブへの接続（自動接続を行うには、rootで実行する必要あり）
  toio = CoreCube()
  if len(sys.argv) == 1:
    toio_addr = toio.cubeFinder()
    print("Connect to " + toio_addr)
  else:
    toio_addr = sys.argv[1]
  toio.connect(toio_addr, bluepy.btle.ADDR_TYPE_RANDOM)

  time.sleep(1)
  print("BLE Version : " + toio.bleVersion())
  print("Battery: %d" % toio.battery())

  # --- Notifyを受け取るクラスの設定
  toio.withDelegate(MyDelegate(bluepy.btle.DefaultDelegate, toio))

  # --- Notifyを要求
  toio.writeCharacteristic(toio.HANDLE_TOIO_ID  + 1, b'\x01\x00', True)
  toio.writeCharacteristic(toio.HANDLE_TOIO_SEN + 1, b'\x01\x00', True)
  toio.writeCharacteristic(toio.HANDLE_TOIO_BTN + 1, b'\x01\x00', True)

  # --- Notify待ち関数を実行させる。 10秒Notifyがなければ終了
  while True:
    if toio.waitForNotifications(10.0):
      pass
    else:
      break

  toio.disconnect()
