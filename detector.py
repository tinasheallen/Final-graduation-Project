#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
standalone functions of the inference

"""

__author__ = "Allen"
__copyright__ = "Copyright 2022"
__version__ = "1.0"
__maintainer__ = "Allen"
__status__ = "Staging"

import cv2
from imutils.video import FPS
import time
from config import cfg


class ModelFiles:
    def __init__(self, detector_type):
        if detector_type == 'people_detector':
            self.labelspath = cfg.inference_people_counter.labels_file
            self.configpath = cfg.inference_people_counter.config_file
            self.weightspath = cfg.inference_people_counter.weight_file
            self.detector_type = detector_type

        elif detector_type == 'face_detector':
            self.labelspath = cfg.inference_face_detector.labels_file
            self.configpath = cfg.inference_face_detector.config_file
            self.weightspath = cfg.inference_face_detector.weight_file
            self.detector_type = detector_type
        else:
            raise ValueError(" detector type is not valid")


class Inference:
    def __init__(self, target_gpu_id, model_file):
        # opencv config
        self.labelspath = model_file.labelspath
        self.configpath = model_file.configpath
        self.weightspath = model_file.weightspath
        self.objectness_confidance = cfg.infer_options.objectness_confidance
        self.nms_threshold = cfg.infer_options.nms_threshold
        self.gpu_id = target_gpu_id
        self.avg_fps = []
        self.flag_render_detections = True
        self.type = model_file.detector_type

        self.LABELS = self.get_classes()
        self.net = cv2.dnn_DetectionModel(self.configpath, self.weightspath)

        # initialize a list of colors to represent each possible class label
        self.COLORS = {'green': [64, 255, 64],
                       'blue': [255, 128, 0],
                       'coral': [0, 128, 255],
                       'yellow': [0, 255, 255],
                       'gray': [169, 169, 169],
                       'cyan': [255, 255, 0],
                       'magenta': [255, 0, 255],
                       'white': [255, 255, 255],
                       'red': [64, 0, 255]
                       }

        self.fps = FPS().start()
        self.names = self.get_classes()

        # OpenCV GPU on CUDA support
        try:
            device_count = cv2.cuda.getCudaEnabledDeviceCount()
            print("[INFO] GPU device count", device_count)
            cv2.cuda.setDevice(self.gpu_id)
            print(f"DNN_TARGET_CUDA set to GPU id {self.gpu_id}")

            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
            print("[INFO] You are using DNN_TARGET_CUDA_FP16 backend to increase the FPS. "
                  "Please make sure your GPU supports floating point 16, or change it back to DNN_TARGET_CUDA. "
                  "Ref: https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#arithmetic-instructions")
        except Exception as e:
            print(e)
            print("[INFO] Please build OpenCV with GPU support in order to use DNN_BACKEND_CUDA: "
                  "https://www.pyimagesearch.com/2020/02/03/how-to-use-opencvs-dnn-module-with-nvidia-"
                  "gpus-cuda-and-cudnn/")
            print("[INFO] Shifting back to DNN_TARGET_CPU")
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            pass

        self.version = cv2.__version__
        if self.version < '4.5.4':
            print(f"[INFO] Your OpenCV version is {self.version} and it does not support the Scaled-YOLO models:"
                  f"yolov4-csp, yolov4-csp-swish, yolov4-p5, yolov4-p6. Please install OpenCV-4.5.4 or later")

        net_width, net_height = self.get_networksize()

        self.net.setInputParams(size=(int(net_width), int(net_height)), scale=1 / 255, swapRB=True, crop=False)

    def get_networksize(self):
        file = open(self.configpath, 'r')
        content = file.read()
        paths = content.split("\n")
        # default net size will be set as 416 if the network size is not detected from the cfg file
        net_width = None
        net_height = None
        for path in paths:
            if path.split("=")[0] == 'width':
                net_width = path.split("=")[1]
            if path.split("=")[0] == 'height':
                net_height = path.split("=")[1]
        return net_width, net_height

    def opencv_infer(self, image):
        start_time = time.time()
        class_ids, confidences, boxes = self.net.detect(image, self.objectness_confidance, self.nms_threshold)

        try:
            bboxes = boxes.tolist()
            confidences_scores = confidences.flatten().tolist()
            class_names = [self.LABELS[id] for id in class_ids.flatten().tolist()]
            for i in range(class_ids.shape[0]):
                class_id = int(class_ids[i])
                confidence = float(confidences[i])
                x = int(boxes[i, 0])
                y = int(boxes[i, 1])
                w = int(boxes[i, 2])
                h = int(boxes[i, 3])

                color = self.COLORS[list(self.COLORS)[class_id % len(self.COLORS)]]
                label = "{}: {:.4f}".format(class_names[i], confidence)
                if self.flag_render_detections:
                    if self.type == 'people_detector':
                        if class_names[i] == 'person':
                            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
                            cv2.putText(image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                    else:
                        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
                        cv2.putText(image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                self.fps.update()
        except Exception as e:
            class_names = []
            bboxes = []
            confidences_scores = []
            pass
        end_time = time.time()
        self.avg_fps.append(1 / (end_time - start_time))
        self.fps.stop()

        # avg_fps = "[INFO] approx. FPS: {:.2f}".format(sum(self.avg_fps) / len(self.avg_fps))
        # print("[INFO] elapsed time: {:.2f}".format(self.fps.elapsed()))
        #
        # print("[INFO] approx. FPS per image: {:.2f}".format(1 / (end_time - start_time)))
        # print("[INFO] average FPS: {}".format(avg_fps))
        # print("=================================================================================================")
        return image, bboxes, confidences_scores, class_names

    def get_classes(self):
        names = []
        with open(self.labelspath) as f:
            content = f.read().splitlines()
            for line in content:
                names.append(line)
        return names


if __name__ == '__main__':
    TARGET_GPU_ID = 0
    inference = Inference(TARGET_GPU_ID)
    fps = FPS().start()

