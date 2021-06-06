import time
import sys
from coreCube import CoreCube
from coreCube import toioDefaultDelegate

# ##########################################
#   coreCube クラスの基本機能をチェックする
# ##########################################

# --- Notifyされたときに実行される処理記述
class MyDelegate(toioDefaultDelegate):
    # HANDLE_TOIO_ID
    def notify_positionID(self, x, y, dir):
      print("X,Y,dir = (%d,%d),%d" % (x,y,dir))

    def notify_standardID(self, stdid, dir):
      print("ID = %d, dir = %d" % (stdid,dir))

    # HANDLE_TOIO_SEN
    def notify_motion(self, id, horizon, tap, dbltap, posture, shake):
      print("Motion: 水平= %d, 衝突=%d, ダブルタップ=%d, 姿勢=%d, シェイク=%d" % (horizon, tap, dbltap, posture, shake))
      if dbltap == 1:
        self.corecube.soundId(6)

    def notify_sensor_angle(self, id, mode, roll, pitch, yaw):
      print("Motion: id, mode, (Roll, Pitch, Yaw) = %d, %d, (%d, %d, %d)" % (id, mode, roll, pitch, yaw))

    def notify_magnetic(self, id, status, power, x, y, z):
      print("Magne: id, status, power, (X, Y, Z) = %d, %d, %d, (%d, %d, %d)" % (id, status, power, x, y, z))

    # HANDLE_TOIO_BTN
    def notify_button(self, id, stat):
      global loop_flag
      if stat == 0x80:
        print("終了 !!")
        self.corecube.soundId(2)
        loop_flag = False

    # HANDLE_TOIO_MTR
    def notify_motor_response(self, response):
      print("motor target response = %d" % (response))


if __name__ == "__main__":

  # ---------------------------------
  #     コアキューブへの接続
  # ---------------------------------
  # 実行時引数に、コアキューブのアドレスを渡して実行するか、
  # 空白にして、最も近くにあるコアキューブに自動接続する
  # ※自動接続を行う場合は、rootで実行するが必要ある
  print("Initialize CoreCube")
  toio = CoreCube()
  if len(sys.argv) == 1:
    print(" ... Searching CoreCube by cubeFinder()")
    toio_addr = toio.cubeFinder()
  else:
    toio_addr = sys.argv[1]
  print("Connect to " + toio_addr)
  toio.connect(toio_addr)
  time.sleep(1)

  print("WRITE系のテスト ====================================")
  # ---------------------------------
  #     ライトとサウンドのテスト
  # ---------------------------------
  print("***** Sound/Light Test *****")
  # Light は、(300ms, Red), (300ms, Green) を3回繰り返す
  # Sound は、(300ms,ド), (300ms,レ), (300ms,ミ) を2回繰り返す
  print("soundSequence/lightSequence")
  toio.lightSequence( 3, ( (30,(255,0,0)), (30,(0,255,0)) ) )
  toio.soundSequence( 2, ( (30,60), (30,62), (30,64) ) )
  time.sleep(2)

  print("soundID/lightOn")
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

  print("soundMono/lightOff")
  # Light は 白を2.55秒点灯
  # Sound は、(255*10ms,ド) を再生する
  # 1秒後に強制停止
  toio.lightOn((255,255,255), 0xFF)
  toio.soundMono(0xFF, 60)
  time.sleep(1)
  toio.lightOff()
  toio.soundStop()

  # ---------------------------------
  #     モーターのテスト
  # ---------------------------------
  print("***** Motor Test *****")
  # 左右=(50,50)で進む
  # 左右=(-50,-50)で進む（後退する）
  # 左右 (50, -50)で進む（回転する）
  print("motor * 3")
  toio.motor((50, 50), 0)
  time.sleep(1)
  toio.motor((-50, -50), 0)
  time.sleep(1)
  toio.motor((50, -50), 0)
  time.sleep(1)
  toio.motor((0, 0), 0)
  time.sleep(1)

  print("***** Motor Target Test *****")
  print("５秒以内にマットの上にcoreCubeを置くと、(100, 100) の位置に移動させます")
  onMat = False
  for i in range(5,0,-1):
    id = toio.id()
    print(i)
    if id == 1:
      onMat = True
    time.sleep(1)
  if onMat:
    print("motor Target")
    toio.motorTarget(100, 100, speed_max=0x30)
    time.sleep(5)

  print("READ系のテスト ====================================")
  # ---------------------------------
  #     ＩＤ読み込みのテスト
  # ---------------------------------
  # MATのID情報を毎秒10回読み取る
  print("***** Read ID Test *****")
  print("Please put coreCube on MAT ...")
  for i in range(10,0,-1):
    id = toio.id()
    if id == 1:    print("%d: id=1 x=%d, y=%d, dir=%d" % (i, toio.x, toio.y, toio.dir))
    elif id == 2:  print("%d: id=2 stdid=%d, dir=%d" % (i, toio.stdid, toio.dir))
    else:          print("%d: id=%d" % (i, id))
    time.sleep(1)

  # ---------------------------------
  #     センサー情報取得
  # ---------------------------------
  print("***** Read Sensor Test *****")
  id = toio.sensor()
  if id == 1: print("horizon, posture : %d, %d" % (toio.horizon, toio.posture))

  # ---------------------------------
  #     各種情報取得
  # ---------------------------------
  print("***** Read information Test *****")
  # Battery/BLE Version 
  print("Battery: %d" % toio.battery())
  print("BLE Version : " + toio.bleVersion())
  time.sleep(1)



  print("Notify系のテスト ====================================")
  print("Notify系のテストを５秒後に開始します。")
  print("途中でやめたい場合は、コアキューブのボタンを押してください")
  print("または、何もNotifyがない状態が10秒間続くと終了します")
  time.sleep(5)

  toio.withDelegate(MyDelegate(toio))

  # --- Notifyを要求
  toio.setNotify(toio.HANDLE_TOIO_ID, True)
  toio.setNotify(toio.HANDLE_TOIO_SEN, True)
  toio.setNotify(toio.HANDLE_TOIO_BTN, True)
  toio.setNotify(toio.HANDLE_TOIO_MTR, True)

  # 磁気センサーをONにする
  toio.magnetic(2, 5)  # mode = 2,  interval = 100ms
  
  # 姿勢角検出をONにする
  toio.sensor_angle(1, 5)  # mode = 1,  interval = 100ms

  # --- Notify待ち関数を実行させる。 ボタンをう押すか、10秒Notifyがなければ終了
  loop_flag = True
  while loop_flag:
    if toio.waitForNotifications(10.0):
      pass
    else:
      break

  toio.disconnect()

