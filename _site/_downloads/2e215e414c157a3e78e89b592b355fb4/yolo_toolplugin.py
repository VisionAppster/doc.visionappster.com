import visionappster as va
from visionappster.coordinates import pixel_to_world
import numpy as np
import cv2
import os


class Yolo:
    # Shared by all instances of this class
    _dnn_model = None
    _class_names = []

    @staticmethod
    def _load_yolo_model():
        # Initialize the DNN model
        data_dir = os.path.dirname(__file__) + '/yolov4/'
        Yolo._dnn_model = cv2.dnn_DetectionModel(data_dir + 'yolov4.cfg', data_dir + 'yolov4.weights')
        Yolo._dnn_model.setInputSize(704, 704)
        Yolo._dnn_model.setInputScale(1.0 / 255)
        Yolo._dnn_model.setInputSwapRB(True)
        with open(data_dir + 'coco.names', 'rt') as f:
            Yolo._class_names = f.read().rstrip('\n').split('\n')

    def __init__(self):
        if Yolo._dnn_model is None:
            Yolo._load_yolo_model()

    def process(self,
                inputs: [('image', va.Image, va.Image()),
                         ('confidenceThreshold', float, 0.1, {'min': 0, 'max': 1.0}),
                         ('suppressionThreshold', float, 0.4, {'min': 0, 'max': 1.0})],
                outputs: [('className', va.Array),
                          ('classId', va.Matrix.Int32),
                          ('confidence', va.Matrix.Double),
                          ('frame', va.Matrix.Double, {'typeName': 'Matrix<double>/frame',
                                                       'blockSize': 4}),
                          ('size', va.Matrix.Double, {'typeName': 'Matrix<double>/size',
                                                      'linkedTo': 'frame/region',
                                                      'blockSize': 1}),
                          ('numberOfObjects', int)]):

        if inputs.image.is_empty():
            raise ValueError('Input image must be non-empty.')

        # The neural network requires 704x704x3 input.
        img = inputs.image.to_rgb().scaled(704, 704)

        # Do the detection using the given confidence + non-maximum
        # suppression thresholds
        classes, confidences, boxes = Yolo._dnn_model.detect(np.array(img, copy=False),
                                                             confThreshold=inputs.confidenceThreshold,
                                                             nmsThreshold=inputs.suppressionThreshold)

        class_names = []
        num_objects = len(confidences)
        if num_objects > 0:
            confidences = confidences.flatten()
            classes = classes.flatten()
            for class_id in classes:
                class_names.append(Yolo._class_names[class_id])

        outputs.className = class_names
        outputs.numberOfObjects = num_objects

        # Create output matrices
        outputs.confidence = va.Matrix.Double(num_objects, 1)
        outputs.classId = va.Matrix.Int32(num_objects, 1)
        outputs.frame = va.Matrix.Double(4 * num_objects, 4)
        outputs.size = va.Matrix.Double(num_objects, 2)

        # Copy results to output matrices.
        for j in range(num_objects):
            # Coordinate frames are aligned to image axes.
            # Initialize to identity matrices.
            for i in range(4):
                outputs.frame[4 * j + i, i] = 1.0
            outputs.confidence[j, 0] = confidences[j]
            outputs.classId[j, 0] = classes[j]
            left, top, width, height = boxes[j]
            # Move corner points to world coordinates
            x0, y0 = pixel_to_world(img, left, top)
            x1, y1 = pixel_to_world(img, left + width, top + height)
            outputs.frame[4 * j, 3] = x0
            outputs.frame[4 * j + 1, 3] = y0
            outputs.size[j, 0] = x1 - x0
            outputs.size[j, 1] = y1 - y0


va.Tool.publish('com.visionappster.opencvpython/1', Yolo)
