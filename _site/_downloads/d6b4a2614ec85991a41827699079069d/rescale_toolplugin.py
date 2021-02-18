import visionappster as va
import numpy as np
import cv2
from cv2 import dnn_superres
import os

class Rescale:
    # Shared by all instances of this class
    _sr_dict = {}

    @staticmethod
    def _load_superresolution_models():
        data_dir = os.path.dirname(__file__) + '/superresolution/'
        for scale in (2, 4, 8):
            Rescale._sr_dict[scale] = dnn_superres.DnnSuperResImpl_create()
            Rescale._sr_dict[scale].readModel(data_dir + 'LapSRN_x' + str(scale) + '.pb')
            Rescale._sr_dict[scale].setModel('lapsrn', scale)

    def __init__(self):
        if not Rescale._sr_dict:
            Rescale._load_superresolution_models()


    def process(self,
                inputs: [('image', va.Image, va.Image()),
                         ('zoomFactor', float, 1.0, {'min': 0.0})],
                outputs: [('image', va.Image)]):

        if inputs.image.is_empty():
            raise ValueError('Input image must be non-empty.')
        if inputs.zoomFactor <= 0:
            raise ValueError('Zoom factor must be greater than zero.')

        # VA image to numpy array
        np_img = np.array(inputs.image.to_rgb(), copy=False)

        rows, cols, _ = np_img.shape
        zoom_factor = inputs.zoomFactor

        # Maximum number of pixels in the output image
        max_pixels = 4.0 * 2**20
        # Actual number of pixels before limiter
        pixels = rows * cols * (zoom_factor * zoom_factor)
        overshoot = pixels / max_pixels

        # Limit the zoom factor so that the output image has
        # no more than max_pixels pixels.
        if overshoot > 1:
            zoom_factor = (max_pixels / (rows * cols)) ** 0.5

        # List of zoom factors to be applied by DNN
        power2list = []
        while zoom_factor > 1:
            if zoom_factor > 4:
                power2list.append(8)
                zoom_factor = zoom_factor / 8.0
            elif zoom_factor > 2:
                power2list.append(4)
                zoom_factor = zoom_factor / 4.0
            else:
                power2list.append(2)
                zoom_factor = zoom_factor / 2.0

        for z in power2list:
            np_img = Rescale._sr_dict[z].upsample(np_img)

        # Scale down by the zoom_factor (which is <= 1)
        rows, cols, _ = np_img.shape
        if zoom_factor != 1:
            np_img = cv2.resize(np_img, (int(cols * zoom_factor), int(rows * zoom_factor)))

        # Convert NumPy array to an image.
        outputs.image = va.Image(va.Image.RGB32, np_img)
        # The scaled image represents the same piece of world as the input
        # image, just with a different resolution. This aligns the output image
        # according to the input so that subsequent analysis steps know its
        # exact position.
        outputs.image.align_with(inputs.image)

va.Tool.publish('com.visionappster.opencvpython/1', Rescale)
