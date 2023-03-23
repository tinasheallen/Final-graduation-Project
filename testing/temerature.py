#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
temperature measuring functions

"""
__author__ = "Allen"
__copyright__ = "Copyright 2022"
__version__ = "1.0"
__maintainer__ = "Allen"
__status__ = "Staging"


import sys
import usb  # form pyusb library
from config import cfg


class TemperDevice(object):
    def __init__(self, device):
        self._device = device

    def get_temperature(self):
        if self._device is None:
            return "Device not ready"
        else:
            try:
                self._device.set_configuration()
                ret = self._device.ctrl_transfer(bmRequestType=0x21, bRequest=0x09, wValue=0x0201, wIndex=0x00,
                                                 data_or_wLength=b'\x01\x01', timeout=cfg.temperature.TIMEOUT)
                self._control_transfer(cfg.temperature.COMMANDS['temp'])
                self._interrupt_read()
                self._control_transfer(cfg.temperature.COMMANDS['ini1'])
                self._interrupt_read()
                self._control_transfer(cfg.temperature.COMMANDS['ini2'])
                self._interrupt_read()
                self._interrupt_read()
                self._control_transfer(cfg.temperature.COMMANDS['temp'])
                data = self._interrupt_read()
                self._device.reset()
                temp = (data[3] & 0xFF) + (data[2] << 8)
                temp_c = temp * (125.0 / 32000.0)
                temp_c = temp_c + cfg.temperature.OFFSET
                return temp_c
            except usb.USBError as err:
                if "not permitted" in str(err):
                    return "Permission problem accessing USB."
                else:
                    return err
            except:
                return "Unexpected error:", sys.exc_info()[0]
                raise

    def _control_transfer(self, data):
        ret = self._device.ctrl_transfer(bmRequestType=0x21, bRequest=0x09, wValue=0x0200, wIndex=0x01,
                                         data_or_wLength=data, timeout=cfg.temperature.TIMEOUT)

    def _interrupt_read(self):
        data = self._device.read(cfg.temperature.ENDPOINT, cfg.temperature.REQ_INT_LEN, interface=cfg.temperature.INTERFACE, timeout=cfg.temperature.TIMEOUT)
        return data


if __name__ == '__main__':
    dev = usb.core.find(idVendor=cfg.temperature.VENDOR_ID, idProduct=cfg.temperature.PRODUCT_ID)
    TDev = TemperDevice(dev)
    output = TDev.get_temperature()
    print(output)
