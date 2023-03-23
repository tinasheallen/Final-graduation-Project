#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
main app functions

"""
__author__ = "Allen"
__copyright__ = "Copyright 2022"
__version__ = "1.0"
__maintainer__ = "Allen"
__status__ = "Staging"



import threading
import cv2
from detector import Inference, ModelFiles
from DeviceRegistry import DeviceInformationModel
import usb  # form pyusb library
from config import cfg
#from temerature import TemperDevice


class App:
    def __init__(self):
        self.dev_information = DeviceInformationModel()
        model_file_people = ModelFiles('people_detector')
        model_file_face = ModelFiles('face_detector')
        TARGET_GPU_ID = 0
        self.inference_people = Inference(TARGET_GPU_ID, model_file_people)
        self.inference_face = Inference(TARGET_GPU_ID, model_file_face)
        #dev = usb.core.find(idVendor=cfg.temperature.VENDOR_ID, idProduct=cfg.temperature.PRODUCT_ID)
        #self.TDev = TemperDevice(dev)

    def people_counter(self, device):
        device_id = int(device['deviceID'])
        resolution = device['resolution']
        cap = cv2.VideoCapture(device_id)
        while True:
            ret, image = cap.read()
            if not ret:
                break
            image, bboxes, confidences_scores, class_names = self.inference_people.opencv_infer(image)
            count = len(bboxes)
            # temp = float(self.TDev.get_temperature())
            #temp = None
            cv2.putText(image, f'people_count: {count}', (40, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
            cv2.putText(image, f'device id: {device_id}', (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
            cv2.putText(image, f'camera resolution: {resolution}', (40, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
            #cv2.putText(image, f'room temperature: {temp}', (40, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255, 0, 255), 1)
            cv2.imshow('people counter', image)
            if cv2.waitKey(10) == 27:  # exit if Escape is hit
                break
        cap.release()
        cv2.destroyAllWindows()

    def face_detector(self, device):
        device_id = int(device['deviceID'])
        resolution = device['resolution']
        cap = cv2.VideoCapture(device_id)
        while True:
            ret, image = cap.read()
            if not ret:
                break
            image, bboxes, confidences_scores, class_names = self.inference_face.opencv_infer(image)
            # temp = float(self.TDev.get_temperature())
            temp = 'NONE'
            cv2.putText(image, f'device id: {device_id}', (40, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
            cv2.putText(image, f'camera resolution: {resolution}', (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 0, 255), 1)
            #cv2.putText(image, f'room temperature: {temp}', (40, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
            cv2.imshow('face detector', image)
            if cv2.waitKey(10) == 27:  # exit if Escape is hit
                break

    def main(self):
        device_data = self.dev_information.get_registry_data()
        camera_devices = device_data['camera devices']  # highest resolution will be at 0 position while lowes resolution device will at -1 position
        print(f'[INFO] found {len(camera_devices)} devices')
        if len(camera_devices) < 2:
            print(f'[ERROR] need 2 camera devices connected to the system to run both people counter and face detector.')
            print(f'Initializing only people counter process')
            process_people_counter = threading.Thread(target=self.people_counter, args=(camera_devices[0], ))
            process_people_counter.start()
        elif len(camera_devices) == 2:
            print(f'Initializing only people counter process')
            process_people_counter = threading.Thread(target=self.people_counter, args=(camera_devices[1],))
            print(f'Initializing only face detector process')
            process_face_detector = threading.Thread(target=self.face_detector, args=(camera_devices[0],))
            process_face_detector.start()
            process_people_counter.start()
        else:
            print(f"[ERROR] couldn't find any camera devices. Aborting the services...")


if __name__ == '__main__':
    app = App()
    app.main()


