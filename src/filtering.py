import cv2 as cv
import numpy as np
from frame import Frame

"""Class for handling all the filtering."""
class VideoFiltering:

    def __init__(self, frame=None):
        """Adds frame to be filtered. All filtering is done to this frame."""
        self.frame = frame

    def clahe(self, clip=2.0, tile=(8, 8)):
        """CLAHE (Contrast Limited Adaptive Histogram Equalization) (https://docs.opencv.org/3.1.0/d5/daf/tutorial_py_histogram_equalization.html)"""
        frame = self.frame.get_frame_hsv()
        lum = frame[:, :, 2]
        clahe = cv.createCLAHE(clipLimit=clip, tileGridSize=tile)
        frame[:, :, 2] = clahe.apply(lum)
        self.frame.set_frame_hsv(frame)
        return self.frame.frame

    def blur(self, value=(7, 7)):
        """"Median blur filter."""
        frame = self.frame.frame
        if np.sum(value) > 0:
            # Values should not be dividable by 2
            if value[0] % 2 is 0:
                val = value[0] + 1
            else:
                val = value[0]
            frame = cv.medianBlur(frame, val)
        self.frame.frame = frame
        return self.frame.frame

    def brightness_contrast(self, brightness=None, contrast=None):
        """Custom brightness and contrast filter."""
        frame = self.frame.get_frame_hsv()
        lum = frame[:, :, 2] # Luminisity from hsv color space frame
        if brightness is None and contrast is None:
            brightness = contrast = np.mean(lum)
        lum = cv.multiply(lum, (contrast / 127 + 1))

        lum = cv.subtract(lum, contrast)
        lum = cv.add(lum, brightness)

        # Scale values to 0 - 255
        lum = cv.subtract(lum, np.asscalar(np.min(lum)))
        lum = cv.divide(lum, np.asscalar(np.max(lum) / 255))

        frame[:, :, 2] = lum
        self.frame.set_frame_hsv(frame)
        return self.frame.frame

    def threshold(self, threshold=127, max_value=255,
                  mode=cv.THRESH_BINARY_INV):
        """Inverted threshold filter."""
        frame = self.frame.get_frame_hsv()
        if threshold > 0:
            ret, frame[:, :, 2] = cv.threshold(frame[:, :, 2], threshold,
                                                  max_value, mode)
        self.frame.set_frame_hsv(frame)
        return self.frame.frame

    def frequencies(self):
        """Calculates white pixels from binarized frame."""
        frame = self.frame.get_frame_hsv ()
        return np.sum(frame[:, :, 2] / 255, dtype=np.int_)

    def resize(self, size):
        """Resize frame to given dimensions."""
        frame = cv.resize(self.frame.frame, size)
        self.frame.frame = frame
        return self.frame.frame

    def roi(self, points, pad):
        """Defines ROI area with given dimensions with padding."""
        frame = self.frame.frame
        size = self.frame.get_frame_size()
        if points:
            # Tries to keep ROI inside the original frame dimensions.
            x = points['x'] - pad
            y = points['y'] - pad
            xw = points['x'] + points['w'] + pad
            yh = points['y'] + points['h'] + pad
            if x < 0:
                x = 0
            if y < 0:
                y = 0
            if xw < 0:
                xw = 0
            if xw > size[0]:
                xw = size[0]
            if yh < 0:
                yh = 0
            if yh > size[1]:
                yh = size[1]

            return {'x': x, 'y': y, 'xw': xw, 'yh': yh}

    def crop_roi(self, points, pad):
        """Crops frame to given dimensions."""
        pt = self.roi(points, pad)
        self.frame.frame = self.frame.frame[pt['y']:pt['yh'], pt['x']:pt['xw']]

    def draw_bounding_box(self, points, pad=0, color=(255, 0, 0), line_thickness=2):
        """Draws rectangle bounding box for given dimensions."""
        if points:
            pt = self.roi(points, pad)
            frame = cv.rectangle(self.frame.frame, (pt['x'], pt['y']),
                        (pt['xw'], pt['yh']), color, line_thickness)
            self.frame.frame = frame


    def draw_dot(self, points, pad=0, radius=2, color=(0, 255, 0), line_thickness=2):
        """Draws circle for given dimensions."""
        frame = self.frame.frame
        for pt in points[0]:
            frame = cv.circle(frame, tuple(pt), radius, color, line_thickness)
        self.frame.frame = frame
