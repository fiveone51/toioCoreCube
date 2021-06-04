# Linux にて、bluepy を使って、toio コアキューブを動かす

-----
# 目次

* [coreCubeクラスの概要](#coreCubeクラスの概要)
* [接続関連](#接続関連)
* [センサー関連](#センサー関連)
* [モーター関連](#モーター関連)
* [ランプ関連](#ランプ関連)
* [サウンド関連](#サウンド関連)
* [その他](#その他)

<br>

* [Notifyの活用](#Notifyの活用)
  * Notifyとは？
  * Notify用のメソッドの定義方法
  * Notifyが使えるメソッド

<br>

-----

ここで紹介している coreCube クラスは、SIE製 toio のコアキューブを Bluetooth のコマンドを使って操作するものです。エラー処理などは、省いているのでご了承ください。基本的には、Pythonと、bluepy という Pythonモジュールが動作すれば動くと思います。


### 動作確認したLinux

* Raspberry Pi 3  (rasbian)
* Raspberry Pi 4  (ubuntu)
* Intel Linux (Debian buster)

### bluepy のインストール

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

### CoreCube バージョンアップ対応
> toio CoreCube のfirmware は不定期にアップデートされ、機能追加と安定性向上が図られています。
  https://toio.io/update/

> いろいろな機能がありすぎて、このクラスはすべてに対応しているわけではありません。なるべく有用な機能に対応していこうと思います。

<br><br>

-----
# coreCubeクラスの概要

toio コアキューブを操作するための各種機能をまとめたクラス。以下の例のような感じで使います。

````py 
import time
from coreCube import CoreCube

toio_addr = CoreCube.cubeSearch()
if len(toio_addr) == 0:
  print("コアキューブが見つかりません")
else:
  toio = CoreCube()
  toio.connect(toio_addr[0])  # 一番近い Cubeに接続
  time.sleep(1)

  toio.moveTo(100, 100, 60)
  toio.soundId(3)

  toio.disconnect()
````

````
$ sudo python3 sample.py                            # 一番近くのコアキューブに自動接続
````

-----
# 接続関連

## cubeSearch　メソッド
> 電源の入っているコアキューブを探して、見つかったコアキューブのアドレスを配列で返す。
> コアキューブの存在しなければ、空の配列をかえす。<p>
> 配列は、RSSIの強さでソートされる（つまり、近くにあるコアキューブから順）。<p>
> **★ クラスメソッドなので、インスタンスを作成しなくても実行できる。<p>
> ★ rootで実行する必要がある**

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

-----
# センサー関連

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
>衝突検知の値も取り出せるが、readメソッドでは常に「衝突していない」の値しか返ってこないので、ここでは取り上げない。衝突件については、Notifyのところで後述する。

<br>
#### sensor関連のオブジェクト

|項目|型|詳細|
|:---|:--|:--|
|**horizon**|int|sensor()メソッドで読み込んだ 水平検出値<p>**00**: 水平ではないとき<p>**01**: 水平な時|

<br>

-----

# モーター関連

## mortor メソッド

[toio 技術仕様 モーター](https://toio.github.io/toio-spec/docs/ble_motor)

> 左右のモーターの速度を指定して、キューブを動かす

#### 詳細
|項目|詳細|
|:---|:--|
|書式|**mortor(speed, duration)**|
|引数|**speed**: 左右のスピードを指定した配列<p>[left, right] のように -100 <= 0 <= 100 で指定<p>ただし、＋値は前進、－値は後退。<p>また、-9～9 は、0に丸められる。|
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
>mortor()で、durationを指定しても、指定した時間分待たずに返ってくるため、必要であれば、上記の例のように、呼び出した側で待ち時間を入れる必要がある。

<br>

## moveTo メソッド

> トイオコレクションのマットの上に置かれたコアキューブを指定された座標まで動かす。<br>**※コアキューブのファームウェアアップデートで、本体側に同様の機能が追加された。そちらの方が精度が高いと思うので、そのうち置き換えます**


#### 詳細
|項目|詳細|
|:---|:--|
|書式|**moveTo(x, y, speed)**|
|引数|**X**: 目的のX座標|
||**Y**: 目的のY座標|
||**speed**: コアキューブの移動のスピード <p> 10～100 の範囲で指定 |
|戻り値|なし|

#### 実行例

````py
toio.moveTo( 100, 100, 50)
toio.soundId(1)

toio.moveTo( 400, 400, 50)
toio.soundId(1)
````

#### 補足
>moveTo()は、コアキューブが指定された位置に到着するまで返ってこないので注意。<p>
>停止位置は、指定された位置と多少誤差が発生する。<p>
>停止する直前に、コアキューブの速度が遅くなる。

<br>

-----
# ランプ関連

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
# サウンド関連

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

> noteを指定して、コアキューブのサウンドを再生させる

#### 詳細

|項目|詳細|
|:---|:--|
|書式|**soundMono(duration, note)**|
|引数|**duration**: モーターを回す時間を指定<p>0 時間指定なし(無期限) <p> 1～255 指定された数×0.01秒 |
||**note**: note id<p> note idは、[toio 技術仕様 サウンド](https://toio.github.io/toio-spec/docs/ble_sound) を参照|
|戻り値|なし|

#### 実行例

````py
toio.soundMono(60, 50)   # ド
time.sleep(0.5)
toio.soundMono(62, 50)   # レ
time.sleep(0.5)
toio.soundMono(64, 50)   # ミ
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
toio.soundID(1)   # selected再生音
time.sleep(0.5)
````

-----
# その他

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
|戻り値| BLEのプロトコルバージョン<p> "2.0.0" というようなテキストが返る|

#### 実行例

````py
print(toio.bleVersion())
````

<br>

-----
# Notifyの活用

  * Notifyとは？
  * Notify用のメソッドの定義方法
  * Notifyが使えるメソッド

## Notifyとは？

> コアキューブが衝突したときや、コアキューブのボタンを押した時の通知のことを Notify という。コアキューブでは、ほとんどの命令が Notify に対応している。<br>
> Notifyが発生したときに実行される関数（callback関数的なもの）を定義できるようにした。

````py
# --- toioDefaultDelegateクラスを継承したクラスを、notify用として定義する
class MyDelegate(toioDefaultDelegate):
    def notify_button(self, id, stat):　　# button のnotifyメソッドをオーバーライド
      if stat == 0x80:
        self.ctoio.soundId(2)

if __name__ == "__main__":
  toio = CoreCube()
  toio.connect("xx:xx:xx:xx:xx:xx")

  # --- 上で定義したクラスを、Delegate用クラスとして設定
  toio.withDelegate(MyDelegate(bluepy.btle.DefaultDelegate, toio))

  # --- Notifyを要求
  toio.setNotify(toio.HANDLE_TOIO_BTN, True)

  # --- Notify待ち関数を実行させる。 10秒Notifyがなければ終了
  while True:
    if toio.waitForNotifications(10.0):
      # 10.0秒以内にNotifyが来た時
      pass
    else:
      # 10.0秒以内にNotifyが来なかった時
      break
````

> Notifyを受け取るためにやることは３つ。

1. Delegateクラスを定義し、デフォルトのnotifyメソッドを、自分なりのメソッドにオーバーライドする
   * デフォルトのDelegateクラスとして toioDefaultDelegateクラスを定義したので、これを継承したクラスを作成する
   * Notifyしたい機能ごとに notiry_xxxxx() というメソッドを用意されているので、自分なりのメソッドにオーバーライドする。上記の例では、button が押されたときNotiry を受け取っている。（どんなメソッドを用意したのかや、渡される引数の詳細については、後述。）
   * ちなみに、button の stat == 0x80 は「ボタンが押されたとき」に返ってきたという意味
1. 上記で定義した自分なりのメソッドを、delegate クラスとして設定する。
   * 「おまじない」だと考える。
  　<br>toio.withDelegate(MyDelegate(bluepy.btle.DefaultDelegate, toio))
1. コアキューブに、Notify を返すように要求する
   * 以下のように、必要なハンドルに対して、Notify を要求する
    <br>toio.setNotify(toio.HANDLE_TOIO_BTN, True)

> これで、Notifyを受け取るための準備ができた。bluepy では、この後、**waitForNotifications() というメソッドを呼ぶことで、Notify待ち状態のループにする。（←　ココ大事）**　具体的には、上記サンプルを参照<br>
> プログラムの処理としては、waitForNotifications()を呼び、指定時間だけNotify待ちになり、その間にNotifyが来たらdelegateクラスで指定されたメソッドが実行され、waitForNotifications()は Trueを返す。もし、指定時間にNotifyがなければ、Falseが返る<br>
> つまり、イベントドリブン的な感じになるということ。

