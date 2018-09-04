import cv2 as cv
from frame import Frame

"""Capture class handles all OpenCV frame capturing from video device or video file."""
class Capture:

    def __init__(self, source_id, **kwargs):
        """Accepts filename or device id. Capture arguments passed as kwargs."""
        self.source = source_id
        self.capture = cv.VideoCapture(source_id)
        self.frame = Frame() # Frame object contains image and frame number, time
        self.total_frames = self.capture.get(cv.CAP_PROP_FRAME_COUNT)
        self.fps = self.capture.get(cv.CAP_PROP_FPS)

        if 'width' in kwargs:
            self.capture.set(cv.CAP_PROP_FRAME_WIDTH, kwargs['width'])
        elif 'height' in kwargs:
            self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, kwargs['height'])
        elif 'fps' in kwargs:
            self.capture.set(cv.CAP_PROP_FPS, kwargs['fps'])
        elif 'start_ms' in kwargs:
            self.capture.set(cv.CAP_PROP_POS_MSEC, kwargs['start_ms'])
        # Only for video files
        elif 'start_frame' in kwargs:
            self.capture.set(cv.CAP_PROP_POS_FRAMES, kwargs['start_frame'])
        elif 'fourcc' in kwargs:
            self.capture.set(cv.CAP_PROP_FOURCC, kwargs['fourcc'])

    def capture_frame(self):
        """Handles capturing frame and updating the frame object."""
        try:
            ret, img = self.capture.read()
            if ret:
                self.frame.frame = img
                self.frame.frame_num = int(self.capture.get(cv.CAP_PROP_POS_FRAMES))
                self.frame.frame_time = self.capture.get(cv.CAP_PROP_POS_MSEC)
                return self.frame.frame
            else:
                raise IOError('Frame could not be read!')
        except IOError:
            self.release_capture()


    def reset(self):
        """Is called to start video from the beginning(ish). See the comments!"""
        # Getting 'non-existing PPS 0 referenced' form FFMPEG if starting from 0 msec (x264/mp4)
        # 24 ms from start seems to work
        # self.capture.set(cv.CAP_PROP_POS_MSEC, 24)
        self.capture.set(cv.CAP_PROP_POS_FRAMES, 24)

        # This breaks timing
        # self.capture = cv.VideoCapture(self.source)

    def capture_open(self):
        """To just check if capturing is still open."""
        return self.capture.isOpened()

    def release_capture(self):
        """Release capture."""
        print('Releasing capture or video. Exiting...')
        self.capture.release()

    def get_total_frames(self):
        """Getter for total frame count."""
        # Useless overhead?
        return self.total_frames

    def get_fps(self):
        """Getter for video frame rate."""
        return self.fps

    def get_lenght_in_s(self):
        """Returns video length in seconds."""
        return self.total_frames / self.fps
