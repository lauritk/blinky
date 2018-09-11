import cv2 as cv
import numpy as np
import copy
from frame import Frame

# TODO: select the closest of the detected points. Fix jumping bounding box.
# TODO: Keep constant bounding box size
# TODO: Fine tune bounding box location
# TODO: Manual overdrive

"""Handles object detection, tracking and related functions."""
class Tracking:

    def __init__(self, frame=None):
        self.frame = frame
        self.initial_frame = frame
        self.tracking_points = {}

    # Optical flow (not in use, experimental and work in progress)
    def point_tracking(self, points=None, **kwargs):
        """Tracks given points in the video. Highly experimental, not used now."""
        lk_params = dict( winSize  = (15,15),
                          maxLevel = 2,
                          criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))

        frame = self.frame.frame
        points = np.array(points, dtype=np.float32)
        # calculate optical flow
        points, st, err = cv.calcOpticalFlowPyrLK(self.initial_frame.frame, frame, points, None, **lk_params)
        self.set_tracking_point('flow', points)


    def haar_classifier(self, **kwargs):
        """Detects eye with haar classifier."""
        # Default settings for haar cascade classifier
        scaleFactor = 1.01
        minNeighbors = 50
        minSize = (54, 54)
        maxSize = (320, 320)
        select = 0
        name = 'haar'
        maxMovement = 16

        frame = self.frame.frame

        if 'cascadeFile' in kwargs:
            cascade_file = kwargs['cascadeFile']
        else:
            raise RuntimeError('Cascade file not defined!')
        if 'scaleFactor' in kwargs:
            scaleFactor = kwargs['scaleFactor']
        if 'minNeighbors' in kwargs:
            minNeighbors = kwargs['minNeighbors']
        if 'minSize' in kwargs:
            minSize = kwargs['minSize']
        if 'maxSize' in kwargs:
            maxSize = kwargs['maxSize']
        if 'select' in kwargs:
            select = kwargs['select'] - 1
        if 'name' in kwargs:
            name = kwargs['name']
        if 'maxMovement' in kwargs:
            maxMovement = kwargs['maxMovement']

        cascade = cv.CascadeClassifier(cascade_file)
        detected = cascade.detectMultiScale(frame, scaleFactor=scaleFactor,
                                            minNeighbors=minNeighbors,
                                            minSize=minSize,
                                            maxSize=maxSize)

        # Updates tracking point if new point detected
        if detected is not None and len(detected) > 0:
            prev_point = self.get_tracking_point(name)
            new_point = {'x': detected[select][0], 'y': detected[select][1],
                         'w': detected[select][2], 'h': detected[select][3]}

            if prev_point:
                # Checks if eye moved too much. Updates new location.
                points = ((prev_point['x'], prev_point['y']), (new_point['x'], new_point['y']))
                if self._check_point_movement(points, maxMovement):
                    # print('Too much movement. Using new point!')
                    self.set_tracking_point(name, new_point)
            else:
                self.set_tracking_point(name, new_point)



    def _distance(self, point1, point2):
        """Manhattan distance for comparing point distances."""
        return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])

    def _check_point_movement(self, points, maxMovement):
        """Checks if the distance between two points is too long, but not too long."""
        if self._distance(points[0], points[1]) > maxMovement and not (self._distance(points[0], points[1]) > maxMovement * 2):
            print("Eye moved, getting current location.")
            return True
        else:
            return False



    def get_tracking_point(self, key):
        """Returns tracking points of the selected method."""
        if key in self.tracking_points:
            return self.tracking_points[key]
        else:
            return False



    def set_tracking_point(self, key, values):
        """Sets tracking points of the selected method."""
        self.tracking_points[key] = values
