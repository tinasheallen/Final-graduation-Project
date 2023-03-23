#! /usr/bin/env python
# coding=utf-8

from easydict import EasyDict as edict

__C = edict()
cfg = __C

# Inference options

__C.inference_face_detector = edict()
__C.inference_face_detector.objectness_confidance = 0.24  # threshold for filter the higher detection scores lager than 0.24
__C.inference_face_detector.nms_threshold = 0.6  # iou threshold when executing the NMS process to remove, when there are more than a single bbox with various detection scores for a single object.
__C.inference_face_detector.labels_file = "./model_data/class_face.names"  # list of classes
__C.inference_face_detector.weight_file = "./model_data/model_face.weights"  # weight/model file to load the trained weights
__C.inference_face_detector.config_file = "./model_data/model_face.cfg"  # configuration file which includes the network architecture configs

__C.inference_people_counter = edict()
__C.inference_people_counter.objectness_confidance = 0.24  # threshold for filter the higher detection scores lager than 0.24
__C.inference_people_counter.nms_threshold = 0.6  # iou threshold when executing the NMS process to remove, when there are more than a single bbox with various detection scores for a single object.
__C.inference_people_counter.labels_file = "./model_data/class_people.names"  # list of classes
__C.inference_people_counter.weight_file = "./model_data/model_people.weights"  # weight/model file to load the trained weights
__C.inference_people_counter.config_file = "./model_data/model_people.cfg"  # configuration file which includes the network architecture configs


__C.infer_options = edict()
__C.infer_options.objectness_confidance = 0.24
__C.infer_options.nms_threshold = 0.6

__C.registry = edict()
__C.registry.startup_registry_creation = False


# temperature measure
__C.temperature = edict()

__C.temperature.VENDOR_ID = 0x413d
__C.temperature.PRODUCT_ID = 0x2107
__C.temperature.TIMEOUT = 5000
__C.temperature.OFFSET = 0
__C.temperature.INTERFACE = 1
__C.temperature.REQ_INT_LEN = 8
__C.temperature.ENDPOINT = 0x81
__C.temperature.COMMANDS = {
    'temp': b'\x01\x80\x33\x01\x00\x00\x00\x00',
    'ini1': b'\x01\x82\x77\x01\x00\x00\x00\x00',
    'ini2': b'\x01\x86\xff\x01\x00\x00\x00\x00',
}
