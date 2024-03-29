from coreCube import CoreCube
from coreCube import toioDefaultDelegate
import bluepy
import sys

# --- Notifyされたときに実行される処理記述
class MyDelegate(toioDefaultDelegate):
    # HANDLE_TOIO_BTN
    def notify_button(self, id, status):
      if status == 0x80:
        print("Push !!")
        self.corecube.soundId(2)

    # HANDLE_TOIO_SEN
    def notify_sensor_angle(self, id, mode, roll, pitch, yaw):
      print("id, mode, (Roll, Pitch, Yaw) = %d, %d, (%d, %d, %d)" % (id, mode, roll, pitch, yaw))

if __name__ == "__main__":

  # --- コアキューブへの接続（自動接続を行うには、rootで実行する必要あり）
  toio = CoreCube()
  if len(sys.argv) == 1:
    toio_addr = toio.cubeFinder()
    print("Connect to " + toio_addr)
  else:
    toio_addr = sys.argv[1]
  toio.connect(toio_addr)
  
  # --- Notifyを受け取るクラスの設定
  toio.withDelegate(MyDelegate(toio))

  # --- Notifyを要求
  toio.setNotify(toio.HANDLE_TOIO_BTN, True)
  toio.setNotify(toio.HANDLE_TOIO_SEN, True)

  # 姿勢角検出をONにする
  toio.sensor_angle(1, 5)  # mode = 1,  interval = 100ms

  # --- Notify待ち関数を実行させる。 10秒Notifyがなければ終了
  while True:
    if toio.waitForNotifications(5.0):
      pass
    else:
      break

  toio.disconnect()
