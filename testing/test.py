# #!/usr/bin/python
# import sys
# import usb.core
# # find USB devices
# dev = usb.core.find(find_all=True)
# # loop through devices, printing vendor and product ids in decimal and hex
# for cfg in dev:
#   sys.stdout.write('Decimal VendorID=' + str(cfg.idVendor) + ' & ProductID=' + str(cfg.idProduct) + '\n')
#   sys.stdout.write('Hexadecimal VendorID=' + hex(cfg.idVendor) + ' & ProductID=' + hex(cfg.idProduct) + '\n\n')

import usb.core
from config import cfg
dev = usb.core.find(idVendor=0x413d, idProduct=0x2107)

dev.set_configuration()
while True:
    # try:
    # dev.ctrl_transfer(bmRequestType=0x21, bRequest=0x09, wValue=0x0201, wIndex=0x00,
    #              data_or_wLength=b'\x01\x01', timeout=cfg.temperature.TIMEOUT)
    dev.ctrl_transfer(bmRequestType=0x21, bRequest=0x09, wValue=0x0200, wIndex=0x01,
                           data_or_wLength=b'\x01\x80\x33\x01\x00\x00\x00\x00', timeout=cfg.temperature.TIMEOUT)

    test =dev.read(cfg.temperature.ENDPOINT, cfg.temperature.REQ_INT_LEN, timeout=cfg.temperature.TIMEOUT)
    print(test)
    # except usb.core.USBError as e:
    #     if str(e).find("timeout") >= 0:
    #         pass
    #     else:
    #         raise IOError("USB Error: %s"%str(e))



