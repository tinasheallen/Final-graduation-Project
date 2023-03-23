#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
device registry functions

"""
__author__ = "Allen"
__copyright__ = "Copyright 2022"
__version__ = "1.0"
__maintainer__ = "Allen"
__status__ = "Staging"

import os
import cv2
import pickle
from config import cfg


class DeviceInformationModel:
    def __init__(self):
        self.registry = 'device_registry.pickle'
        self.is_registery = self.check_registry()

    @staticmethod
    def get_camera_devices():
        print(f'[INFO] getting camera device info')
        devices = []
        for deviceID in range(3):
            data = {}
            camera = cv2.VideoCapture(deviceID)
            if not camera.isOpened():
                continue
            else:
                data['deviceID'] = deviceID
                is_reading, img = camera.read()
                w = camera.get(3)
                h = camera.get(4)
                data['resolution'] = f'{w}*{h}'
                data['frame width'] = int(w)
                data['frame height'] = int(h)
                if is_reading:
                    data['status'] = 'working'
                else:
                    data['status'] = 'not working'
            devices.append(data)
            sorted(devices, key=lambda x: x['resolution'], reverse=True)
        return devices

    def check_registry(self): #Automation
        if os.path.isfile(self.registry):
            register = True
        else:
            register = False
        return register

    def get_registry_data(self):
        if self.is_registery:
            if not cfg.registry.startup_registry_creation:
                print(f'[INFO] device registry has found. Using the registry to obtain the device data. If new device is connected use startup_registry_creation = True to update the registry')
                with open(self.registry, 'rb') as handle:
                    device_data = pickle.load(handle)
            else:
                camera_devices = self.get_camera_devices()
                other_devices = self.get_other_devices()
                device_data = {'camera devices': camera_devices,
                               'other devices': other_devices}
                self.set_registry_data(device_data)
                self.disable_registry_update()

        else:
            camera_devices = self.get_camera_devices()
            other_devices = self.get_other_devices()
            device_data = {'camera devices': camera_devices,
                           'other devices': other_devices}
            self.set_registry_data(device_data)
        return device_data

    def set_registry_data(self, data):
        print(f'[INFO] updating registry ..')
        with open(self.registry, 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # @staticmethod
    # def get_other_devices():
    #     import usb.core
    #     busses = usb.busses()
    #     devices = []
    #     for bus in busses:
    #         devices_usb = bus.devices
    #         for dev in devices_usb:
    #             devs = {'Device': dev.filename, 'Manufacturer': dev.iManufacturer, 'Serial': dev.iSerialNumber,
    #                     'Product': dev.iProduct}
    #             devices.append(devs)
    #     return devices

    @staticmethod
    def disable_registry_update():
        with open("config.py", "rb") as f:
            content = f.read().splitlines()
            new_content = []
            cnt = 0
            for line in content:
                decode_line = line.decode("utf-8").split('=')[0].strip()
                if decode_line == '__C.registry.startup_registry_creation':
                    line = b'__C.registry.startup_registry_creation = False'
                new_content.append(line.decode("utf-8"))
                cnt = cnt + 1
            with open('config.py', 'w') as f:
                for item in new_content:
                    f.write("%s\n" % item)

