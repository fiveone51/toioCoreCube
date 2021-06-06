from coreCube import CoreCube
from coreCube import toioDefaultDelegate
import sys

# --- Notifyされたときに実行される処理記述
class MyDelegate(toioDefaultDelegate):
    # HANDLE_TOIO_BTN
    def notify_button(self, id, stat):
      global end_flag
      if stat == 0x80:
        print("終了 !!")
        self.corecube.soundId(2)
        end_flag = True

    # HANDLE_TOIO_SEN
    def notify_motion(self, id, horizon, tap, dbltap, posture, shake):
      print("Motion: 水平= %d, 衝突=%d, ダブルタップ=%d, 姿勢=%d, シェイク=%d" % (horizon, tap, dbltap, posture, shake))
      if dbltap == 1:
        self.corecube.soundId(6)
    
    # HANDLE_TOIO_ID
    def notify_positionID(self, x, y, dir):
      print("X,Y,dir = (%d,%d),%d" % (x,y,dir))

    def notify_standardID(self, stdid, dir):
      print("ID = %d, dir = %d" % (stdid,dir))


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
  toio.setNotify(toio.HANDLE_TOIO_ID, True)
  toio.setNotify(toio.HANDLE_TOIO_SEN, True)
  toio.setNotify(toio.HANDLE_TOIO_BTN, True)

  # --- Notify待ち関数を実行させる。 ボタンをう押すか、10秒Notifyがなければ終了
  end_flag = False
  while True:
    if toio.waitForNotifications(10.0):
      if end_flag:
        break
      pass
    else:
      break

  toio.disconnect()
