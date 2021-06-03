import bluepy
import binascii
import time
import struct
import codecs
import os
import sys
import math

class CoreCube(bluepy.btle.Peripheral):
  
  def __init__(self):
    bluepy.btle.Peripheral.__init__(self)
    self.x = 0
    self.y = 0
    self.dir = 0
    self.stdid = 0
    self.horizon = 0
    self.collision = 0

  #  ---------------- connect
  def connect(self, deviceAddr, addrType=bluepy.btle.ADDR_TYPE_RANDOM):
    bluepy.btle.Peripheral.connect(self, deviceAddr, addrType)
    # UUIDからHANDLEを求める
    charas = bluepy.btle.Peripheral.getCharacteristics(self)
    for chara in charas:
      if chara.uuid.binVal.hex() == "10b201015b3b45719508cf3efcd7bbae":
        self.HANDLE_TOIO_ID = chara.getHandle()
      elif chara.uuid.binVal.hex() == "10b201025b3b45719508cf3efcd7bbae":
        self.HANDLE_TOIO_MTR = chara.getHandle()
      elif chara.uuid.binVal.hex() == "10b201035b3b45719508cf3efcd7bbae":
        self.HANDLE_TOIO_LED = chara.getHandle()
      elif chara.uuid.binVal.hex() == "10b201045b3b45719508cf3efcd7bbae":
        self.HANDLE_TOIO_SND = chara.getHandle()
      elif chara.uuid.binVal.hex() == "10b201065b3b45719508cf3efcd7bbae":
        self.HANDLE_TOIO_SEN = chara.getHandle()
      elif chara.uuid.binVal.hex() == "10b201075b3b45719508cf3efcd7bbae":
        self.HANDLE_TOIO_BTN = chara.getHandle()
      elif chara.uuid.binVal.hex() == "10b201085b3b45719508cf3efcd7bbae":
        self.HANDLE_TOIO_BAT = chara.getHandle()
      elif chara.uuid.binVal.hex() == "10b201ff5b3b45719508cf3efcd7bbae":
        self.HANDLE_TOIO_CFG = chara.getHandle()

  #  ---------------- ID Information
  def id(self):
    data = self.readCharacteristic(self.HANDLE_TOIO_ID)
    id = struct.unpack('b', data[0:1])[0]
    if id == 0x01:
      self.x, self.y, self.dir = struct.unpack('hhh', data[1:7])
    elif id == 0x02:
      self.stdid = struct.unpack('i', data[1:5])[0]
      self.dir = struct.unpack('h', data[5:7])[0]
    return id

  #  ---------------- Sensor Information
  def sensor(self):
    data = self.readCharacteristic(self.HANDLE_TOIO_SEN)
    id = struct.unpack('b', data[0:1])[0]
    if id == 0x01:
      self.horizon = struct.unpack('b', data[1:2])[0]
      self.collision = struct.unpack('b', data[2:3])[0]
    return id

  #  ---------------- Battery Information
  def battery(self):
    data = self.readCharacteristic(self.HANDLE_TOIO_BAT)
    return struct.unpack('b', data)[0]

  #  ---------------- Motor Control
  def motor(self, speeds, duration):
    data = "01" if duration == 0 else "02"
    data = data + "01" + ("01" if speeds[0] >= 0 else "02") + ("{:02x}".format(abs(speeds[0])))
    data = data + "02" + ("01" if speeds[1] >= 0 else "02") + ("{:02x}".format(abs(speeds[1])))
    if duration != 0:
      data = data + ("{:02x}".format(duration))
    self.writeCharacteristic(self.HANDLE_TOIO_MTR, binascii.a2b_hex(data))

  #  ---------------- Light Control
  def lightOn(self, color, duration):
    data = "03{:02x}0101{:02x}{:02x}{:02x}".format(duration, color[0], color[1], color[2])
    self.writeCharacteristic(self.HANDLE_TOIO_LED, binascii.a2b_hex(data))

  def lightSequence(self, times, operations):    # operations = ( (duration,(r,g,b)), (d,(r,g,b)), ... )
    data = "04{:02x}".format(times)
    data = data + "{:02x}".format(len(operations))
    for ope in operations:
      data = data + "{:02x}0101{:02x}{:02x}{:02x}".format(ope[0], ope[1][0], ope[1][1], ope[1][2])
    self.writeCharacteristic(self.HANDLE_TOIO_LED, binascii.a2b_hex(data))

  def lightOff(self):
    data = "01"
    self.writeCharacteristic(self.HANDLE_TOIO_LED, binascii.a2b_hex(data))

  #  ---------------- Sound Control
  def soundId(self, id):
    data = "02{:02x}FF".format(id)
    self.writeCharacteristic(self.HANDLE_TOIO_SND, binascii.a2b_hex(data))

  def soundSequence(self, times, operations):     # operations = ( (duration,note), (d,n), ... )
    data = "03{:02x}".format(times)
    data = data + "{:02x}".format(len(operations))
    for ope in operations:
      data = data + "{:02x}{:02x}FF".format(ope[0], ope[1])
    self.writeCharacteristic(self.HANDLE_TOIO_SND, binascii.a2b_hex(data))

  def soundMono(self, duration, note):
    data = "030101{:02x}{:02x}FF".format(duration, note)
    self.writeCharacteristic(self.HANDLE_TOIO_SND, binascii.a2b_hex(data))

  def soundStop(self):
    data = "01"
    self.writeCharacteristic(self.HANDLE_TOIO_SND, binascii.a2b_hex(data))

  #  ---------------- Configuration  ( BLE Version )
  def bleVersion(self):
    data = "0100"
    self.writeCharacteristic(self.HANDLE_TOIO_CFG, binascii.a2b_hex(data))
    time.sleep(0.1)
    data = self.readCharacteristic(self.HANDLE_TOIO_CFG)
    try:
      version = codecs.decode(data[2:8], encoding='utf-8')
    except:
      version = ''
    return version

  #  ---------------- Magnetic Sensor Information
  def magnetic(self, mode, interval):
    # Notify にて、intervalで指定した間隔で返ってくる
    data = "1b00{:02x}{:02x}01".format(mode, interval)
    self.writeCharacteristic(self.HANDLE_TOIO_CFG, binascii.a2b_hex(data))

  # ----------------- Utility

  # いちばん近いcoreCube のアドレスを返す。ただし、root で実行する必要がある。
  # （既にconnect中のものがあるとdisconnectされるので注意）
  @classmethod
  def cubeFinder(self):
    if os.environ.get('USER') == 'root':
      scaner = bluepy.btle.Scanner(0)
      devices = scaner.scan(3)
    
      finds = []
      for device in devices:
        for (adType, desc, value) in device.getScanData():
          if "toio Core Cube" in value:
            finds.append((device.rssi, device.addr))
      if len(finds):
        finds.sort(key = lambda rssi:rssi[0], reverse=True)
        return finds[0][1]
      else:
        raise FileNotFoundError('toio core cube is not found.')
    else:
      raise PermissionError('You need to execute this command as root')

  # coreCube を探して、アドレスを返す。ただし、root で実行する必要がある。
  # 戻り値は、近い順にソートされている
  # （既にconnect中のものがあるとdisconnectされるので注意）
  @classmethod
  def cubeSearch(self):
    if os.environ.get('USER') == 'root':
      scaner = bluepy.btle.Scanner(0)
      devices = scaner.scan(3)
    
      finds = []
      for device in devices:
        for (adType, desc, value) in device.getScanData():
          if "toio Core Cube" in value:
            finds.append((device.rssi, device.addr))
      ret = []
      if len(finds) != 0:
        finds.sort(key = lambda rssi:rssi[0], reverse=True)
        for i in finds:
          ret.append(i[1])
      return ret
    else:
      raise PermissionError('You need to execute this command as root')

  # 指定角度を向く
  #    細かいパラメータ:
  def turnTo(self, tdir):
    for i in range(20):
      self.id()
      diff_dir = tdir - self.dir
      if (abs(diff_dir) <= 15 ):
        self.motor( (0, 0), 0)
        break
      else:
        if diff_dir > 180: diff_dir -= 360
        if diff_dir < -180: diff_dir += 360
        sp = max(int(diff_dir/4), 10) if diff_dir > 0 else min(int(diff_dir/4), -10)
        self.motor( (sp, -sp), 10)
        time.sleep(0.02)

  # 指定位置に向かう
  #    
  def moveTo(self, tx, ty, speed):
    STOP = 10
    SLOW = speed
    while True:
      if self.id() != 1:
        break

      # --- 指定位置に近づいた？
      dist =  math.sqrt((tx - self.x)**2 + (ty - self.y)**2)
      ds = 1.0  # --- 減速係数
      if dist < STOP:          # --- 指定位置からSTOP範囲に入ったら、終了
        break
      if dist < SLOW:          # --- 指定位置からSLOW範囲に入ったら、減速
        ds = max(dist / SLOW, 0.3)

      # --- 現在位置から、指定位置までの角度を計算
      tdir = int(math.acos( (tx - self.x) / dist ) * 180.0 / math.pi)
      if ty - self.y < 0: tdir *= -1

      # --- 角度補正値計算
      diff_dir = tdir - self.dir
      if diff_dir > 180: diff_dir -= 360
      if diff_dir < -180: diff_dir += 360
      dr = abs(int(diff_dir / 2)) + 1 if diff_dir > 0 else 0
      dl = abs(int(diff_dir / 2)) + 1 if diff_dir < 0 else 0

      # --- move
      sl = max(int((speed - dl) * ds ), 10)
      sr = max(int((speed - dr) * ds ), 10)
      if sl+sr == 20:          # --- 最低速度だと差が出ないので・・・
        sl = sl + 1 if dr != 0 else sl
        sr = sr + 1 if dl != 0 else sr
      self.motor( (sl, sr), 0 )
      time.sleep(0.03)

    self.motor( (0, 0), 0 )
  
  def setNotify(self, handle, flag):
    if flag:
      self.writeCharacteristic(handle + 1, b'\x01\x00', True)
    else:
      self.writeCharacteristic(handle + 1, b'\x00\x00', True)


class toioDefaultDelegate(bluepy.btle.DefaultDelegate):
    def __init__(self, params, ptoio):             # コンストラクタで対応するtoioを指定する
        bluepy.btle.DefaultDelegate.__init__(self)
        self.ctoio = ptoio

    # notify callback: cHandle で何のNotifyかを見分けて処理分岐
    def handleNotification(self, cHandle, data):
        # ------------- ボタン
        if cHandle == self.ctoio.HANDLE_TOIO_BTN:
          id, stat = struct.unpack('BB', data[0:2])
          self.notify_button(id, stat)

        # ------------- モーションセンサー
        if cHandle == self.ctoio.HANDLE_TOIO_SEN:
          id = struct.unpack('b', data[0:1])[0]
          if id == 0x01:
            id, horizon, tap, dbltap = struct.unpack('BBBB', data[0:4])
            self.notify_motion(id, horizon, tap, dbltap)
          if id == 0x02:
            id, status, power, x, y, z = struct.unpack('bbbBBB', data[0:6])
            self.notify_magnetic(id, status, power, x, y, z)

        # ------------- IDセンサー
        if cHandle == self.ctoio.HANDLE_TOIO_ID:
          id = struct.unpack('b', data[0:1])[0]
          if id == 0x01:
            x, y, dir = struct.unpack('hhh', data[1:7])
            self.notify_XY(x, y, dir)
          elif id == 0x02:
            stdid = struct.unpack('i', data[1:5])[0]
            dir = struct.unpack('h', data[5:7])[0]
            self.notify_ID(stdid, dir)

    def notify_button(self, id, stat):
      pass
    def notify_motion(self, id, horizon, tap, dbltap):
      pass
    def notify_XY(self, x, y, dir):
      pass
    def notify_ID(self, stdid, dir):
      pass
    def notify_magnetic(self, id, status, power, x, y, z):
      pass
