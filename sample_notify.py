from coreCube import CoreCube
from coreCube import toioDefaultDelegate
import time
import bluepy
import sys
import struct

class MyDelegate(toioDefaultDelegate):
    # HANDLE_TOIO_BTN
    def notify_button(self, id, stat):
      if stat == 0x80:    # ボタンが押されたら音を出す
        self.ctoio.soundId(2)

    # HANDLE_TOIO_SEN
    def notify_motion(self, id, horizon, tap, dbltap):
      print("MOTION SENSOR:   HORIZON={:02x}, TAP={:02x}, DblTAP={:02x}".format(horizon, tap, dbltap))
      if dbltap == 1:     # ダブルタップされたら音を出す 
        self.ctoio.soundId(6)
    
    # HANDLE_TOIO_ID
    def notify_XY(self, x, y, dir):
      print("X,Y,dir = (%d,%d), %d" % (x,y,dir))　　　# マットの座標、角度を表示する

    def notify_ID(self, stdid, dir):
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
  toio.setNotify(toio.HANDLE_TOIO_ID, True)   # ID情報
  toio.setNotify(toio.HANDLE_TOIO_SEN, True)　# センサー情報
  toio.setNotify(toio.HANDLE_TOIO_BTN, True)  # ボタン情報

  # --- Notify待ち関数を実行させる。 10秒Notifyがなければ終了
  while True:
    if toio.waitForNotifications(10.0):
      pass
    else:
      break

  toio.disconnect()
