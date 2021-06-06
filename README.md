# Linux にて、bluepy を使って、toio コアキューブを動かすクラス

-----
# 目次

[coreCubeクラスの概要](#coreCubeクラスの概要)

各メソッドの説明

* [接続関連](#接続関連)
* [センサー関連（READ系）](#センサー関連（READ系）)
* [モーター関連（WRITE系）](#モーター関連（WRITE系）)
* [ランプ関連（WRITE系）](#ランプ関連（WRITE系）)
* [サウンド関連（WRITE系）](#サウンド関連（WRITE系）)
* [その他（READ系）](#その他（READ系）)


[Notifyの活用](#Notifyの活用)

* [Notifyとは？](#Notifyとは？)
* [Delegateクラスの作成方法](#Delegateクラスの作成方法)
* [Notify要求について](#Notify要求について)
* [プログラムの構造について](#プログラムの構造について)

<br>

-----
# coreCubeクラスの概要


ここで紹介している `coreCube` クラスは、SIE製 toio のコアキューブを Bluetooth のコマンドを使って操作するものです。エラー処理などは、省いているのでご了承ください。基本的には、Pythonと、bluepy という Pythonモジュールが動作すれば動くと思います。


### 動作確認したLinux

* Raspberry Pi 3  (rasbian)
* Raspberry Pi 4  (ubuntu)
* Intel Linux (Debian buster)

### bluepy のインストール
> 詳細については[こちら](http://ianharvey.github.io/bluepy-doc/index.html)を参照してください。
````
★必要なパッケージのインストール
$ sudo apt install libbluetooth3-dev libglib2.0 libboost-python-dev libboost-thread-dev

★Raspberry Pi (rasbian Bustrer以前) では、バージョン不整合があるようなので以下の操作をする
$ cd /usr/lib/arm-linux-gnueabihf/
$ sudo ln libboost_python-py35.so libboost_python-py34.so

★bluepy のインストール
$ sudo pip3 install gattlib
$ sudo pip3 install bluepy

★bluetooth サービスがインストールされていなければインストールする
$ sudo apt install bluetooth
$ sudo systemctl enable bluetooth
$ sudo restart
````

### CoreCube バージョンについて
> toio CoreCube のfirmware は不定期にアップデートされ、機能追加と安定性向上が図られています。
  https://toio.io/update/

> いろいろな機能がありすぎて、このクラスはすべてに対応しているわけではありません。なるべく有用な機能に対応していこうと思います。

> また、CoreCube のバージョンは常に最新にしてください。
> <br> 2021/06/06 現在、**BLEプロトコルバージョン 2.3.0 に対応**しています

<br>

### CoreCube の詳細について
> 本家の情報は、以下になります。
* [toio 技術仕様](https://toio.github.io/toio-spec/)
* [toio 技術仕様 BLE通信仕様](https://toio.github.io/toio-spec/docs/ble_communication_overview)

<br>

### 大雑把な機能の説明
> このクラスで提供する機能は、大きく４つのグループに分けられます<br>

> * 接続関連　　コアキューブと接続する
>   * [接続関連](#接続関連)
> * READ系　　センサーなどの情報を読み取る
>   * [センサー関連（READ系）](#センサー関連（READ系）)
>   * [その他（READ系）](#その他（READ系）)
> * WRITE系　 モーター、ライト、サウンドに対して命令を送る
>   * [モーター関連（WRITE系）](#モーター関連（WRITE系）)
>   * [ランプ関連（WRITE系）](#ランプ関連（WRITE系）)
>   * [サウンド関連（WRITE系）](#サウンド関連（WRITE系）)
> * NOTIFY系　センサーなどからの通知を受ける
>   * [Notifyの活用](#Notifyの活用)
>
> コアキューブから情報を受け取る手段として、READ系とNOTIFY系があります。<br>
> READ系は、順序立てて命令を実行させるやり方に適しています。<br>
> NOTIFY系は、コールバック的に、コアキューブからの通知をもとに動作させるようなやり方に適しています。<br>

<br>

### 簡単な使い方（READ/WRITE系）
> 接続して、READ系で情報読み込んで、WRITE系で命令を送って、切断するという基本形です
````py 
import time
from coreCube import CoreCube

toio = CoreCube()

# --- 接続
toio_addr = "xx:xx:xx:xx:xx:xx"
toio.connect(toio_addr)
time.sleep(1)

# --- READ系
id = toio.id()
if id == 1:
  print("Position: x=%d, y=%d, dir=%d" % (toio.x, toio.y, toio.dir))
print("Battery: %d" % toio.battery())
print("BLE Version : " + toio.bleVersion())

# --- WRITE系
toio.motorTarget(100, 100, speed_max=0x30)
toio.soundId(3)

# --- 切断
time.sleep(5)
toio.disconnect()
````

<br>

### 簡単な使い方（NOTIFY系）
> ボタンがNOTIFYで返ってくるまで、ループし続けるという基本形です
````py 
from coreCube import CoreCube
from coreCube import toioDefaultDelegate

class MyDelegate(toioDefaultDelegate):　　# toioDefaultDelegateを継承したクラス定義
    def notify_button(self, id, stat):　　# button の notifyメソッドをオーバーライド
      self.corecube.soundId(2)

if __name__ == "__main__":
  toio = CoreCube()
  toio.connect("xx:xx:xx:xx:xx:xx")

  # --- 上で定義したクラスを、Delegate用クラスとして設定
  toio.withDelegate(MyDelegate(toio))

  # --- ボタンに対して、Notifyを要求
  toio.setNotify(toio.HANDLE_TOIO_BTN, True)

  # ここでは、Notifyを１０秒待つことを、無限ループさせている。
  # Notifyが来たら（ボタンが押されたら）、MyDelegate.notify_button()が実行され、終了する。
  while True:
    if toio.waitForNotifications(10.0):
      # Notify処理が実行された時
      break

  # --- 切断
  toio.disconnect()
````
> Notifyについては、後述しますが、マットのXY座標や、姿勢角検出値など、連続的に読み出際には、こちらのやり方で行います。

<br>

-----
# 接続関連

## connect メソッド

> コアキューブのアドレスを指定して、接続するメソッド

#### 詳細

|項目|詳細|
|:---|:--|
|書式|**connect(deviceAddr)**|
|引数|**deviceAddr**: 接続したいコアキューブのアドレス|
|戻り値|なし|

#### 実行例

````py
  toio_addr = "xx:xx:xx:xx:xx:xx"
  toio = coreCube()
  try:
    toio.connect(toio_addr)
  except:
    print("接続エラー")
    sys.exit()
````

#### 備考
> コアキューブのアドレスを知るには、`find_toio.py` を実行する。近くにある電源の入ったコアキューブの一覧が表示される。（`find_toio.py` の実行は、root で行うこと）

<br>

## cubeSearch　メソッド
> 電源の入っているコアキューブを探して、見つかったコアキューブのアドレスを配列で返す。
> コアキューブが存在しなければ、空の配列をかえす。<p>
> 配列は、RSSIの強さでソートされる（つまり、近くにあるコアキューブから順）。<p>
> **★ クラスメソッドなので、インスタンスを作成しなくても実行できる。<p>
> ★ このメソッドは、rootで実行する必要がある**

#### 詳細

|項目|詳細|
|:---|:--|
|書式|**cubeSearch()**|
|引数|なし|
|戻り値|コアキューブのアドレスが、配列で戻る|

#### 実行例

````py
  toio_addrs = CoreCube.cubeSearch()

  if len(toio_addrs) == 1:
    toio1 = coreCube()
    toio1.connect(toio_addr[0])
    print("Connect to " + toio_addrs[0])
  elif len(toio_addrs) == 2:
    toio1 = coreCube()
    toio1.connect(toio_addr[0])
    toio2 = coreCube()
    toio2.connect(toio_addr[1])
````
<br>



-----
# センサー関連（READ系）

## id メソッド

[toio 技術仕様 読み取りセンサー](https://toio.github.io/toio-spec/docs/ble_id)

> コアキューブが置かれているマットの`Position ID`( X,Y座標, 角度)や、カード・ステッカーの`Standard ID`( カードを識別する番号、角度）を取り出す。<p>
> BLEのREADで読み込む（Notifyではない）。このメソッドを呼び出すことで、`CoreCube`クラスの `x`, `y`, `dir`, `stdid` オブジェクトに`Position ID`/`Standard ID` が設定される。

#### 詳細

|項目|詳細|
|:---|:--|
|書式|**id()**|
|引数|なし|
|戻り値|読込んだIDの種類<p>**1**: Position ID（x, y, dir が設定される）<p>**2**: Standard ID（stdid, dir が設定される）<p>**3**: その他|

#### 実行例

````py
toio = CoreCube()
toio.connect("xx:xx:xx:xx:xx:xx")  # 実際のアドレスを指定

id = toio.id()
if id == 1:
  print("id=%d: x=%d, y=%d, dir=%d" % (id, toio.x, toio.y, toio.dir))
elif id == 2:
  print("id=%d: stdid=%d, dir=%d" % (id, toio.stdid, toio.dir))
else:
  print("id=%d:" % id)
````

#### 補足
>読み取りセンサー情報は、このモジュールを使って、直接READする方法と、Notifyで受け取る方法がある。Notify については、後述。

<br>

#### id関連のオブジェクト

|項目|型|詳細|
|:---|:--|:--|
|**x**|int|id()メソッドで読み込んだ X座標|
|**y**|int|id()メソッドで読み込んだ Y座標|
|**dir**|int|id()メソッドで読み込んだ 角度|
|**stdid**|int|id()メソッドで読み込んだ Standard ID|
<br>

## sensor メソッド

[toio 技術仕様 モーションセンサー](https://toio.github.io/toio-spec/docs/ble_sensor)

> コアキューブのモーションセンサーの傾き情報

#### 詳細
|項目|詳細|
|:---|:--|
|書式|**sensor()**|
|引数|なし|
|戻り値|なし|

#### 実行例

````py
id = toio.sensor()
if toio.horizon == 0:
  print("傾いています!!")
````

#### 補足
>衝突検知の値なども取り出せるが、readメソッドでは、ほぼ「衝突していない」の値しか返ってこない（現在の状態をとってくるので、衝突した瞬間の値を読むのは至難の業・・・）。<br>衝突検知については、Notifyのところで後述する。

<br>

#### sensor関連のオブジェクト

|項目|型|詳細|
|:---|:--|:--|
|**horizon**|int|水平検出値<p>**00**: 水平ではないとき<p>**01**: 水平な時<br> [詳細](https://toio.github.io/toio-spec/docs/ble_sensor#%E6%B0%B4%E5%B9%B3%E6%A4%9C%E5%87%BA)|
|**posture**|int|姿勢検出値 キューブの姿勢によって 1～6 の値をとる（ex. 1なら天面が上）<br>[詳細](https://toio.github.io/toio-spec/docs/ble_sensor#%E5%A7%BF%E5%8B%A2%E6%A4%9C%E5%87%BA)|

<br>

-----

# モーター関連（WRITE系）

## mortor メソッド

[toio 技術仕様 モーター](https://toio.github.io/toio-spec/docs/ble_motor)

> 左右のモーターの速度を指定して、キューブを動かす

#### 詳細
|項目|詳細|
|:---|:--|
|書式|**mortor(speed, duration)**|
|引数|**speed**: 左右のスピードを指定した配列<p>[left, right] のように -115 <= 0 <= 115 で指定<p>ただし、＋値は前進、－値は後退。<p>また、遅すぎると(-8～8 )、0に丸められる。<br>これらの値は、コアキューブのバージョンによって異なる可能性があるため、[詳細ページ](https://toio.github.io/toio-spec/docs/ble_motor#%E3%83%A2%E3%83%BC%E3%82%BF%E3%83%BC%E3%81%AE%E9%80%9F%E5%BA%A6%E6%8C%87%E7%A4%BA%E5%80%A4) にて確認すること|
||**duration**: モーターを回す時間を指定<p>0 時間指定なし(無期限) <p> 1～255 指定された数×0.01秒 |
|戻り値|なし|

#### 実行例

````py
speed = [50, 50]
toio.mortor(speed, 100)     # １秒前進
time.sleep(1)
toio.mortor([50, -50], 100)    # １秒回転
time.sleep(1)
toio.mortor([s*-1 for s in speed], 100)   # １秒後退
time.sleep(1)
````

#### 補足
>mortor()で、durationを指定しても、指定した時間分待たずに返ってくる。必要であれば、上記の例のように、呼び出した側で待ち時間を入れる必要がある。

<br>

## motorTarget メソッド
[toio 技術仕様 目標指定付きモーター制御](https://toio.github.io/toio-spec/docs/ble_motor#%E7%9B%AE%E6%A8%99%E6%8C%87%E5%AE%9A%E4%BB%98%E3%81%8D%E3%83%A2%E3%83%BC%E3%82%BF%E3%83%BC%E5%88%B6%E5%BE%A1)
> マットの上に置かれたコアキューブを指定された座標まで動かす。<br>

#### 詳細
|項目|詳細|
|:---|:--|
|書式|**motorTarget(x, y, dir, timeout, mtype, speed_max, speed_type))**|
|引数|**X**: 目的のX座標|
||**Y**: 目的のY座標|
||dir: 目的地でのコアキューブの角度。`省略可能`。省略時は角度の修正は行わない。 [詳細](https://toio.github.io/toio-spec/docs/ble_motor#%E7%9B%AE%E6%A8%99%E5%9C%B0%E7%82%B9%E3%81%A7%E3%81%AE%E3%82%AD%E3%83%A5%E3%83%BC%E3%83%96%E3%81%AE%E8%A7%92%E5%BA%A6-%CE%B)|
||timeout: タイムアウト時間(秒)。`省略可能`。省略時は10秒|
||mtype: 移動タイプ。`省略可能`。省略時は0（回転しながら移動）。 [詳細](https://toio.github.io/toio-spec/docs/ble_motor#%E7%A7%BB%E5%8B%95%E3%82%BF%E3%82%A4%E3%83%97)|
||speed_max: モーターの最大速度指示値。`省略可能`。省略時は 0x50|
||speed_type: モーターの速度変化タイプ。 `省略可能`。省略時は 0(速度変化なし)  [詳細](https://toio.github.io/toio-spec/docs/ble_motor#%E3%83%A2%E3%83%BC%E3%82%BF%E3%83%BC%E3%81%AE%E9%80%9F%E5%BA%A6%E5%A4%89%E5%8C%96%E3%82%BF%E3%82%A4%E3%83%97)|
|戻り値|なし|

#### 実行例

````py
toio.motorTarget( 200, 200, speed_max=0x30)
time.sleep(10)
````

#### 補足
>motorTarget()も、呼び出したらすぐに返ってくるので注意。<p>
>処理がうまくいったかどうかについては、Notifyで確認することができる。詳細は、Notify関連の `notify_motor_response()` を参照のこと。

<br>

-----
# ランプ関連（WRITE系）

## lightOn メソッド

[toio 技術仕様 ランプ](https://toio.github.io/toio-spec/docs/ble_light)

> RGBを指定して、コアキューブのLEDを点灯させる

#### 詳細
|項目|詳細|
|:---|:--|
|書式|**lightOn(color, duration)**|
|引数|**color**: LEDの色を指定した配列<p>[RED, GREEN, BLUE] のように、それぞれ、0 <= 255 で指定<p>|
||**duration**: モーターを回す時間を指定<p>0 時間指定なし(無期限) <p> 1～255 指定された数×0.01秒 |
|戻り値|なし|

#### 実行例

````py
color = [255, 255, 255]
toio.lightOn(color, 0)
time.sleep(1)
for i in range(256):
  toio.lightOn([i, i, i], 0) 
  time.sleep(0.1)
toio.lightOff()  
````

#### 補足

>lightOn()で、durationを指定しても、指定した時間分待たずに返ってくるため、必要であれば、上記の例のように、呼び出した側で待ち時間を入れる必要がある。

<br>

## lightOff メソッド

[toio 技術仕様 ランプ](https://toio.github.io/toio-spec/docs/ble_light)

> コアキューブのLEDを消灯させる

#### 詳細
|項目|詳細|
|:---|:--|
|書式|**lightOff()**|
|引数|なし|
|戻り値|なし|

#### 実行例

````py
color = [255, 255, 255]
time.sleep(1)
for i in range(256):
  toio.lightOn([i, i, i], 0) 
  time.sleep(0.01)
toio.lightOff()  
````
<br>

## lightSequence メソッド

[toio 技術仕様 ランプ](https://toio.github.io/toio-spec/docs/ble_light)

> コアキューブのLEDをパターンを指定して点灯させる

#### 詳細

|項目|詳細|
|:---|:--|
|書式|**lightSequence(times, operations)**|
|引数|**times**:<p>0: 無限に繰り返す<P>1～255: 繰り返し回数 |
||**operations**: LED色の点灯パターンを配列で指定<p> [ [duration, [R, G, B]], [duration, [R, G, B]], ... ] のように指定する。|
|戻り値|なし|

#### 実行例

````py
op_W = [20, [255, 255, 255]]
op_R = [20, [255, 0, 0]]
toio.lightSequence(5, [op_W, op_R])
time.sleep(2)
toio.lightOff()  
````

#### 補足

>lightSequence()で、durationを指定しても、指定した時間分待たずに返ってくるため、必要であれば、上記の例のように、呼び出した側で待ち時間を入れる必要がある。

>BLEでは、１度に送れるデータ量に制限がある。bluepyでは、デフォルト値が小さいため、2 operation しか送ることができない。（MTUの変更ができるハズだが、うまくいかない）

<br>

-----
# サウンド関連（WRITE系）

## soundID メソッド

[toio 技術仕様 サウンド](https://toio.github.io/toio-spec/docs/ble_sound)

>コアキューブから効果音を再生する。

### 詳細

|項目|詳細|
|:---|:--|
|書式|**soundID(id)**|
|引数|**id**: 効果音のID<p> idと音の対応は、 [toio 技術仕様 サウンド](https://toio.github.io/toio-spec/docs/ble_sound) を参照|
|戻り値|なし|

#### 実行例

````py
toio.soundID(1)   # selected再生音
time.sleep(0.5)
````

#### 補足

>soundID()は、サウンドの終了を待たずに処理が戻る。

<br>

## soundMono メソッド

[toio 技術仕様 サウンド](https://toio.github.io/toio-spec/docs/ble_sound)

> note（音階）を指定して、コアキューブのサウンドを再生させる

#### 詳細

|項目|詳細|
|:---|:--|
|書式|**soundMono(duration, note)**|
|引数|**duration**: サウンドを鳴らす時間を指定<p>0 時間指定なし(無期限) <p> 1～255 指定された数×0.01秒 |
||**note**: note id<p> note idは、[toio 技術仕様 サウンド](https://toio.github.io/toio-spec/docs/ble_sound) を参照|
|戻り値|なし|

#### 実行例

````py
toio.soundMono(50, 60)   # ド
time.sleep(0.5)
toio.soundMono(50, 62)   # レ
time.sleep(0.5)
toio.soundMono(50, 64)   # ミ
time.sleep(0.5)
````

#### 補足

>soundMono()で、durationを指定しても、指定した時間分待たずに返ってくるため、必要であれば、上記の例のように、呼び出した側で待ち時間を入れる必要がある。

<br>

## soundSequence メソッド

[toio 技術仕様 サウンド](https://toio.github.io/toio-spec/docs/ble_sound)

> コアキューブのサウンドをパターンを指定して再生させる

#### 詳細

|項目|詳細|
|:---|:--|
|書式|**soundSequence(times, operations)**|
|引数|**times**:<p>0: 無限に繰り返す<P>1～255: 繰り返し回数 |
||**operations**: サウンドの再生パターンを配列で指定<p> [ [duration, note], [duration, note], ... ] のように指定する。|
|戻り値|なし|

#### 実行例

````py
op_do = [20, 60]
op_re = [20, 62]
op_me = [20, 64]
toio.soundSequence(5, [op_do, op_re, op_mi])
time.sleep(3)
toio.soundStop()  
````

#### 補足

>soundSequence()も、再生の終了を待たずに返ってくるため、必要であれば、上記の例のように、呼び出した側で待ち時間を入れる必要がある。

>BLEでは、１度に送れるデータ量に制限がある。bluepyでは、デフォルト値が小さいため、4 operation しか送ることができない。（MTUの変更ができるハズだが、うまくいかない）

<br>

## soundStop メソッド

[toio 技術仕様 サウンド](https://toio.github.io/toio-spec/docs/ble_sound)

>コアキューブの効果音を停止する。

### 詳細

|項目|詳細|
|:---|:--|
|書式|**soundStop()**|
|引数|なし|
|戻り値|なし|

#### 実行例

````py
toio.soundMono(0, 60)   # ド
time.sleep(2.0)
toio.soundStop()
````

-----
# その他（READ系）

## battery メソッド

[toio 技術仕様 バッテリー](https://toio.github.io/toio-spec/docs/ble_battery)

> コアキューブのバッテリー残量を返す

#### 詳細

|項目|詳細|
|:---|:--|
|書式|**battery()**|
|引数|なし|
|戻り値| バッテリー残量 <p> 10%刻みで、0% ～ 100%が返る|

#### 実行例

````py
print(toio.battery())
````
<br>

## bleVersion メソッド

[toio 技術仕様 設定](https://toio.github.io/toio-spec/docs/ble_configuration)

> コアキューブのプロトコルバージョンを返す

#### 詳細

|項目|詳細|
|:---|:--|
|書式|**bleVersion()**|
|引数|なし|
|戻り値| BLEのプロトコルバージョン<p> "2.3.0" というようなテキストが返る|

#### 実行例

````py
print(toio.bleVersion())
````

<br>

-----
# Notifyの活用

  * [Notifyとは？](#Notifyとは？)
  * [Delegateクラスの作成方法](#Delegateクラスの作成方法)
  * [Notify要求について](#Notify要求について)
  * [プログラムの構造について](#プログラムの構造について)

## Notifyとは？

> コアキューブが衝突したときや、コアキューブのボタンを押した時の通知のことを Notify という。コアキューブでは、ほとんどの命令が Notify に対応している。<br>
> Notifyが発生したときに実行される関数（callback関数的なもの）を定義することで、Notifyが発生した時の処理を記述することができる。

実行のイメージ
````py
from coreCube import CoreCube
from coreCube import toioDefaultDelegate

class MyDelegate(toioDefaultDelegate):　　# toioDefaultDelegateを継承したクラス定義
    def notify_button(self, id, stat):　　# button の notifyメソッドをオーバーライド
      self.corecube.soundId(2)

if __name__ == "__main__":
  toio = CoreCube()
  toio.connect("xx:xx:xx:xx:xx:xx")

  # --- 上で定義したクラスを、Delegate用クラスとして設定
  toio.withDelegate(MyDelegate(toio))

  # --- ボタンに対して、Notifyを要求
  toio.setNotify(toio.HANDLE_TOIO_BTN, True)

  # ここでは、Notifyを１０秒待つことを、無限ループさせている。
  # Notifyが来たら（ボタンが押されたら）、MyDelegate.notify_button()が実行され、終了する。
  while True:
    if toio.waitForNotifications(10.0):
      # Notify処理が実行された時
      break

  # --- 切断
  toio.disconnect()
````

> Notifyを受け取るためにやることは３つ。

1. **`Delegateクラスを定義`し、デフォルトのnotifyメソッドを、自分なりのメソッドにオーバーライドする**
   * デフォルトのDelegateクラス（toioDefaultDelegateクラス）を継承したクラスを作成する
   * Notifyごとにコールバックされる notiry_xxxxx() というメソッドが用意されているので、自分なりのメソッドにオーバーライドする。上記の例では、button が押されたときにNotiry を受け取っている。
1. **上記で定義した自分なりのクラスを、delegateクラスとして指定する**
   * 「おまじない」だと考える。
  　<br>  toio.withDelegate(MyDelegate(toio))
1. **コアキューブに、`Notify を返すように要求`する**
   * 以下のように、必要なハンドルに対して、Notify を要求する
    <br>toio.setNotify(toio.HANDLE_TOIO_BTN, True)

<br>

## Delegateクラスの作成方法

> オーバーライドできる notify_xxxxx() メソッドとしては、以下のものが用意されている。<br>
> これらのメソッドの中で、Notifyを返してきたコアキューブを特定するために、<br>
>   `corecube`<br>
> というプロパティが用意されているので、こちらを参照することで、対象コアキューブに命令を送りなおすことなどができる<br>
> 　　使用例) 　`self.corecube.soundId(2)`　　# Notifyを送ってきたコアキューブで音を出す

<br>

> `notify_positionID(self, x, y, dir): `
> |項目|型|詳細|
> |:---|:--|:--|
> |**x**|int|X座標|
> |**y**|int|Y座標|
> |**dir**|int|角度|
> 
> PositionIDに変化があった場合に呼ばれる

<br>

> `notify_standardID(self, stdid, dir):`
> |項目|型|詳細|
> |:---|:--|:--|
> |**stdid**|int|StandardID|
> |**dir**|int|角度|
> 
> StandardIDを読み込んだときに呼ばれる

<br>

> `notify_motion(self, id, horizon, tap, dbltap, posture, shake):`
> <br>[詳細情報](https://toio.github.io/toio-spec/docs/ble_sensor#%E3%83%A2%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3%E6%A4%9C%E5%87%BA%E6%83%85%E5%A0%B1%E3%81%AE%E5%8F%96%E5%BE%97)
> |項目|型|詳細|
> |:---|:--|:--|
> |**id**|int| 0x01 固定|
> |**horizon**|int|水平検出|
> |**tap**|int|衝突検出|
> |**dbltap**|int|ダブルタップ検出|
> |**posture**|int|姿勢検出|
> |**shake**|int|シェイク検出|
>
> モーションに変更があったときに呼ばれる

<br>

> `notify_sensor_angle(self, id, mode, roll, pitch, yaw):`
> <br>[詳細情報](https://toio.github.io/toio-spec/docs/ble_high_precision_tilt_sensor#%E5%A7%BF%E5%8B%A2%E8%A7%92%E6%83%85%E5%A0%B1%E3%81%AE%E5%8F%96%E5%BE%97%EF%BC%88%E3%82%AA%E3%82%A4%E3%83%A9%E3%83%BC%E8%A7%92%E3%81%A7%E3%81%AE%E9%80%9A%E7%9F%A5%EF%BC%89)
> |項目|型|詳細|
> |:---|:--|:--|
> |**id**|int| 0x03 固定|
> |**mode**|int|種類（0x01 オイラー角のみ利用可能）|
> |**roll**|int|Roll X軸|
> |**pitch**|int|Pitch Y軸|
> |**yaw**|int|Yaw Z軸|
>
> 姿勢角に変更があったときに呼ばれる
> **事前に sensor_angle() メソッドで姿勢角検出をONにしなければならない**

<br>

> `notify_magnetic(self, id, status, power, x, y, z):`
> <br>[詳細情報](https://toio.github.io/toio-spec/docs/ble_magnetic_sensor#%E7%A3%81%E6%B0%97%E3%82%BB%E3%83%B3%E3%82%B5%E3%83%BC%E6%83%85%E5%A0%B1%E3%81%AE%E5%8F%96%E5%BE%97)
> |項目|型|詳細|
> |:---|:--|:--|
> |**id**|int| 0x02 固定|
> |**status**|int|[磁石の状態](https://toio.github.io/toio-spec/docs/ble_magnetic_sensor#%E7%A3%81%E7%9F%B3%E3%81%AE%E7%8A%B6%E6%85%8B)|
> |**power**|int|[磁力の検出](https://toio.github.io/toio-spec/docs/ble_magnetic_sensor#%E7%A3%81%E5%8A%9B%E3%81%AE%E6%A4%9C%E5%87%BA)（強度）|
> |**x**|int|[磁力の検出](https://toio.github.io/toio-spec/docs/ble_magnetic_sensor#%E7%A3%81%E5%8A%9B%E3%81%AE%E6%A4%9C%E5%87%BA)（（磁力の方向 X軸）|
> |**y**|int|[磁力の検出](https://toio.github.io/toio-spec/docs/ble_magnetic_sensor#%E7%A3%81%E5%8A%9B%E3%81%AE%E6%A4%9C%E5%87%BA)（（磁力の方向 Y軸）|
> |**z**|int|[磁力の検出](https://toio.github.io/toio-spec/docs/ble_magnetic_sensor#%E7%A3%81%E5%8A%9B%E3%81%AE%E6%A4%9C%E5%87%BA)（（磁力の方向 Z軸）|
>
> 磁気センサーの情報が変化すると呼ばれる
> **事前に magnetic() メソッドで磁気センサー検出をONにしなければならない**

<br>

> `notify_button(self, id, stat):`
> |項目|型|詳細|
> |:---|:--|:--|
> |**id**|int| 0x02 固定|
> |**status**|int|ボタンの状態<br> 押されたら0x80, 話したら0x00 が返る|
>
> ボタンが押されたら呼ばれる

<br>

> `notify_motor_response(self, response):`
> <br>[詳細情報](https://toio.github.io/toio-spec/docs/ble_motor#%E5%BF%9C%E7%AD%94%E5%86%85%E5%AE%B9)
> |項目|型|詳細|
> |:---|:--|:--|
> |**self**|int| 正常終了のとき0x00<br>その他は上記、詳細情報を参照|
>
> motorTarget() メソッドにてコアキューブを動かした際、その動作が終了したときに返る

<br>

## Notify要求について
> Notifyは、通常OFFになっているため、HANDLEを指定して、ONにしなければならない。
> BLEの通信帯域はそれほど広くないため、必要なものだけをONにすべきである。<br>
> また、HANDLEは、connect時に取得されるため、connectの後に指定する。<br>
> 現時点で指定できるのは以下の４種類
* HANDLE_TOIO_ID　　→　Position ID, Standard ID系
* HANDLE_TOIO_SEN 　→　各種センサー系
* HANDLE_TOIO_BTN　 →　ボタン
* HANDLE_TOIO_MTR　 →　目標指定モーター応答

全部を指定した例
```py
  toio = CoreCube()
  toio.connect("xx:xx:xx:xx:xx:xx")

  toio.setNotify(toio.HANDLE_TOIO_ID, True)
  toio.setNotify(toio.HANDLE_TOIO_SEN, True)
  toio.setNotify(toio.HANDLE_TOIO_BTN, True)
  toio.setNotify(toio.HANDLE_TOIO_MTR, True)
```

> また、デフォルトでOFFになっているセンサーがあるので、ONにするためのメソッドが用意されている

<br>

> **磁気センサーをONにする**
>
> `magnetic(mode, interval)`
> |項目|型|詳細|
> |:---|:--|:--|
> |**mode**|int| 0x00 無効化<br>0x01 磁石の状態検出の有効化<br>0x02 磁力の検出の有効化|
> |**interval**|int|Notifyを返す間隔(10ms単位)|
>
> 「状態検出」と「磁力の検出」は同時に設定できない。詳細は、[こちらを参照](https://toio.github.io/toio-spec/docs/ble_configuration#_%E7%A3%81%E6%B0%97%E3%82%BB%E3%83%B3%E3%82%B5%E3%83%BC%E3%81%AE%E8%A8%AD%E5%AE%9A_)のこと

<br>

> **姿勢角検出をONにする**
>
> `sensor_angle(mode, interval)`
> |項目|型|詳細|
> |:---|:--|:--|
> |**mode**|int| 通知内容の種類（0x01 オイラー角のみ）|
> |**interval**|int|Notifyを返す間隔(10ms単位)|
>
> 本来、オイラー角の他、クォータニオンでの通知が可能だが、複雑になるので、オイラー角のみ有効にしている

<br>

## プログラムの構造について


> Notifyを受け取り、処理するためには、**waitForNotifications() というメソッドを呼ぶことで、Notify待ち状態のループにする。（←　ココ大事）**　具体的には、下記サンプルを参照<br>
````py
from coreCube import CoreCube
from coreCube import toioDefaultDelegate

class MyDelegate(toioDefaultDelegate):　　# toioDefaultDelegateを継承したクラス定義
    def notify_button(self, id, stat):　　# button の notifyメソッドをオーバーライド
      self.corecube.soundId(2)

if __name__ == "__main__":
  toio = CoreCube()
  toio.connect("xx:xx:xx:xx:xx:xx")

  # --- 上で定義したクラスを、Delegate用クラスとして設定
  toio.withDelegate(MyDelegate(toio))

  # --- ボタンに対して、Notifyを要求
  toio.setNotify(toio.HANDLE_TOIO_BTN, True)

  # ここでは、Notifyを１０秒待つことを、無限ループさせている。
  # Notifyが来たら（ボタンが押されたら）、MyDelegate.notify_button()が実行され、終了する。
  while True:
    if toio.waitForNotifications(10.0):
      # Notify処理が実行された時
      break
    elif
      # Notify処理がなく、10.0秒経った時
      pass

  # --- 切断
  toio.disconnect()
````

> プログラムの処理としては、waitForNotifications()を呼び、指定時間だけNotify待ちになり、その間にNotifyが来たらdelegateクラスのコールバックメソッドが実行され、waitForNotifications()は Trueを返す。もし、指定時間にNotifyがなければ、Falseが返る<br>
> つまり、イベントドリブン的な感じになるということ。

