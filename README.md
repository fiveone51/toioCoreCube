# Raspberry pi にて、bluepy を使って、toio コアキューブを動かすサンプル(python3)

## raspberry pi 以外（Intel Linux）でも動作してます。というか、最近は Intel Linux で確認しています

事前に、raspberry pi に bluepyをインストールする必要あり。

````
$ sudo apt install libbluetooth3-dev libglib2.0 libboost-python-dev libboost-thread-dev
$ sudo apt install python3-pip
$ cd /usr/lib/arm-linux-gnueabihf/　　　　　　　　　　　　　　　　　←　raspi のみ。Intel Linuxでは不要
$ sudo ln libboost_python-py35.so libboost_python-py34.so　　　　 ←　raspi のみ。Intel Linuxでは不要
$ sudo pip3 install gattlib
$ sudo pip3 install bluepy
$ sudo systemctl daemon-reload
$ sudo service bluetooth restart
````
> 3,4行目は、buster から不要になったみたいです。

### CoreCube バージョンアップ対応
> toio CoreCube のfirmware がアップデートされ、機能追加と安定性向上が図られました。（2020年1月前後）

  https://toio.io/update/

>  この新しいアップデートでは、GATT Handle が変更されています。利用するBLEのライブラリによっては気にする必要はないのですが、bluepy はもろに影響を受けます。ということで、BLE Version を取り出して、Handle をダイナミックに変更するように修正しました。

> また、モーターコントロールにいろいろな機能が追加されています。いろいろありすぎて、どのように対応するべきか、ちょっと考えてから、coreCubeクラスを修正しようかなぁと思っていますので、少々お待ちください。（磁気センサーなども使えるようになっています）


その他、以下に簡単な説明あり。

[Raspberry Pi で toio コアキューブをコントロールする](https://qiita.com/FiveOne/items/505f369d1f77fa846a8b)

-----

# coreCube クラス の概要

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

# 接続関連

## cubeSearch()
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
toio.connect(TOIO_ADDR)

id = toio.id()
if id == 1:
  print("id=%d: x=%d, y=%d, dir=%d" % (id, toio.x, toio.y, toio.dir))
elif id == 2:
  print("id=%d: stdid=%d, dir=%d" % (id, toio.stdid, toio.dir))
else:
  print("id=%d:" % id)
````

#### 補足
>本来、読み取りセンサー情報は、notify で読み込むべきなので、このメソッドを使う必要はない。しかし、現時点で、このクラスは非同期対応していないため、うまくnotify を受け取ることができていない。そのための苦肉の策となっている。

#### id関連のオブジェクト

|項目|型|詳細|
|:---|:--|:--|
|**x**|int|id()メソッドで読み込んだ X座標|
|**y**|int|id()メソッドで読み込んだ Y座標|
|**dir**|int|id()メソッドで読み込んだ 角度|
|**stdid**|int|id()メソッドで読み込んだ Standard ID|

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
>こちらも readメソッドで読み込んでいる。ホントは collision という衝突検知の値も取り出せるが、readメソッドでは常に「衝突していない」の値しか返ってこないので、ここでは取り上げない

#### sensor関連のオブジェクト

|項目|型|詳細|
|:---|:--|:--|
|**horizon**|int|sensor()メソッドで読み込んだ 水平検出値<p>**00**: 水平ではないとき<p>**01**: 水平な時|

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

## moveTo メソッド

> トイオコレクションのマットの上に置かれたコアキューブを指定された座標まで動かす。

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

-----
