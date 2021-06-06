import sys
import bluepy

def main():
    try:
        peri = bluepy.btle.Peripheral()
        peri.connect(devadr, bluepy.btle.ADDR_TYPE_RANDOM)  # addrTypeがpublic なら、ADDR_TYPE_PUBLICを指定
    except:
        print("device connect error")
        sys.exit()

    charas = peri.getCharacteristics()
    for chara in charas:
        print("======================================================")
        print(" UUID : %s" % chara.uuid )
        print(" Handle %04x: %s" % (chara.getHandle(), chara.propertiesToString()))

    peri.disconnect()

if __name__ == "__main__":
    if len(sys.argv) == 1:
      print('Usage: getHandle.py BLE_DEVICE_ADDRESS')
      sys.exit()
    devadr = sys.argv[1]

    main()