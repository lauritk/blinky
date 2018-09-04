from copy import copy, deepcopy
import cv2 as cv

"""Handles the frame information."""
class Frame:

    def __init__(self, frame=None, frame_num=None, frame_time=None):
        self.frame = frame
        self.frame_num = frame_num
        self.frame_time = frame_time

    def get_frame_hsv(self):
        """Returns BGR frame in HSV format."""
        return cv.cvtColor(self.frame, cv.COLOR_BGR2HSV)

    def set_frame_hsv(self, frame, frame_num=None):
        """Sets HSV frame as objects frame in BGR format."""
        self.frame = cv.cvtColor(frame, cv.COLOR_HSV2BGR)

    def get_frame_size(self):
        """Return frame size as tuple."""
        return (self.frame.shape[1], self.frame.shape[0])
