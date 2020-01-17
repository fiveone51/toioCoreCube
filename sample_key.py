from coreCube import CoreCube
import time
import bluepy
import sys
import struct

class MyDelegate(bluepy.btle.DefaultDelegate):
    def __init__(self, params, ptoio):
        bluepy.btle.DefaultDelegate.__init__(self)
        self.toio = ptoio

    # notify callback: cHandle で何の情報かを見分けて処理分岐
    def handleNotification(self, cHandle, data):
        global loopFlag
        global cid
        global cix
        global ciy

        # ------------- ボタン
        if cHandle == CoreCube.HANDLE_TOIO_BTN:
          id , status = struct.unpack('BB', data[0:2])
          loopFlag = False
          cid = 0
        # ------------- IDセンサー
        if cHandle == CoreCube.HANDLE_TOIO_ID:
          cid = struct.unpack('b', data[0:1])[0]
          if cid == 0x01:
            x, y, dir = struct.unpack('hhh', data[1:7])
            if x > 500:    # Rythm&GO
              cix = int((x - 550) / 44)   # Rythm&Go MATのGRIDに変換
              ciy = int((y -  50) / 44)
            else:
              cix = 0
              ciy = 0

if __name__ == "__main__":

  # --- コアキューブへの接続（rootで実行する必要あり）
  toio_addr = CoreCube.cubeSearch()
  if len(toio_addr) == 0:
    print("コアキューブの電源を入れてください")
    sys.exit()

  toio = CoreCube()
  toio.connect(toio_addr[0])
  time.sleep(1)

  # ---  Notifyクラスを設定
  toio.withDelegate(MyDelegate(bluepy.btle.DefaultDelegate, toio))

  # ---  Notifyを要求
  toio.writeCharacteristic(CoreCube.HANDLE_TOIO_ID  + 1, b'\x01\x00', True)
  toio.writeCharacteristic(CoreCube.HANDLE_TOIO_BTN + 1, b'\x01\x00', True)

  # --- Rythm&Go MATのGRID に、SOUNDのnoteを割り当て
  notes = [
      [128,  49,  51, 128,  54,  56,  58, 128, 128],
      [ 48,  50,  52,  53,  55,  57,  59,  60, 128],
      [128,  61,  63, 128,  66,  68,  70, 128, 128],
      [ 60,  62,  64,  65,  67,  69,  71,  72, 128],
      [128,  73,  75, 128,  78,  80,  81, 128, 128],
      [ 72,  74,  76,  77,  79,  81,  83,  84, 128],
      [128,  85,  87, 128,  90,  92,  94, 128, 128],
      [ 84,  86,  88,  89,  91,  93,  95,  96, 128],
      [128, 128, 128, 128, 128, 128, 128, 128, 128]
  ]

  loopFlag = True
  note_bak = 128
  cix = ciy = cid = 0

  # --- ボタンが押されるまでループ
  while loopFlag:
    if toio.waitForNotifications(1.0):
      if cid == 1:
        note = notes[ciy][cix]
        if note != note_bak:
          print("note: (%d, %d) %d" % (cix, ciy, note))
          toio.soundMono(255, note)
          note_bak = note
      else:
        note_bak = 128
        toio.soundStop()    

  toio.soundStop()    
  toio.disconnect()
