from pypylon import pylon
from pypylon import genicam
from pathlib import Path
import cv2 as cv
import skvideo.io
import csv

"""Camera class for controlling and recording high speed video from Basler USB-cameras."""
class Camera:
    def __init__(self, parameters=None):

        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice( ))
        self.info = self.camera.GetDeviceInfo()
        self.camera.MaxNumBuffer = 10 # Default is 10
        self.imageWindow = pylon.PylonImageWindow()
        self.imageWindow.Create(1)

        if parameters is None:
            # Use defaults
            self.parameters = {
                'output_file': 'output.mp4',
                'width': 160,
                'height': 160,
                'fps': 500.0,
                'exposure_time': 1000.0}
        else:
            self.parameters = parameters

        self.parameters['ffmpeg_param'] = {
          '-vcodec': 'libx264',
          '-preset': 'ultrafast',
          '-crf': '28',
          '-framerate': str(self.parameters['fps']),
          '-r': str(self.parameters['fps'])
          #'-g': str(self.parameters['fps']),
          #'-keyint_min': str(self.parameters['fps']),
          #'-sc_threshold': '0'
        }

        self.parameters['record'] = True
        file = Path(self.parameters['output_file'])
        self.parameters['output_csv'] = file.parent / (file.stem + "_recording.csv")
        self.data_out = []

        self.counter = 0
        self.first_timestamp = 0 # First time stamp is used for calculating start point as 0

        # Setup converter
        self.converter = pylon.ImageFormatConverter()
        # Convert to RGB8 to support skvideo
        self.converter.OutputPixelFormat = pylon.PixelType_RGB8packed
        # Convert image BGR8 to support OpenCV
        # self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned


    def print_info(self):
        print("Using device ", self.info.GetModelName())

    def enable_chunks(self):
        """Meta data is delivered within the frame as a chunks."""
        # Enable chunks in general.
        if genicam.IsWritable(self.camera.ChunkModeActive):
            self.camera.ChunkModeActive = True
        else:
            raise pylon.RUNTIME_EXCEPTION("The camera doesn't support chunk features")

        # Enable time stamp chunks.
        self.camera.ChunkSelector = "Timestamp"
        self.camera.ChunkEnable = True

        # Enable counter chunks
        self.camera.ChunkSelector = "CounterValue"
        self.camera.ChunkEnable = True

        # Enable exposure time chunk
        self.camera.ChunkSelector = "ExposureTime"
        self.camera.ChunkEnable = True

        # Enable CRC checksum chunks.
        self.camera.ChunkSelector = "PayloadCRC16"
        self.camera.ChunkEnable = True

    def disable_chunks(self):
        # Disable chunk mode.
        if genicam.IsWritable(self.camera.ChunkModeActive):
            self.camera.ChunkModeActive = False
        else:
            raise pylon.RUNTIME_EXCEPTION("The camera doesn't support chunk features")

        self.camera.ChunkSelector = "Timestamp"
        self.camera.ChunkEnable = False

        self.camera.ChunkSelector = "CounterValue"
        self.camera.ChunkEnable = False

        self.camera.ChunkSelector = "ExposureTime"
        self.camera.ChunkEnable = False

        self.camera.ChunkSelector = "PayloadCRC16"
        self.camera.ChunkEnable = False

    def update_parameters(self, parameters):
        """Updates camera parameters with the values passed."""
        self.camera.Open()
        self.parameters = parameters
        self.set_parameters()
        self.camera.Close()

    def set_parameters(self):
        """Basler camera parameters are accessed via NodeMap. Genicam interface is used to check if
        the nodes are writtable and then values are changed accordinly."""
        node_map = self.camera.GetNodeMap()
        if genicam.IsWritable(node_map.GetNode("GainAuto")):
            self.camera.GainAuto = "Off"
        if genicam.IsWritable(node_map.GetNode("ExposureAuto")):
            self.camera.ExposureAuto = "Off"
        if genicam.IsWritable(node_map.GetNode("Width")):
            self.camera.Width = self.parameters['width']
        if genicam.IsWritable(node_map.GetNode("Height")):
            self.camera.Height = self.parameters['height']
        if genicam.IsWritable(node_map.GetNode("OffsetX")):
            self.camera.CenterX = True
            # self.camera.OffsetX = 256
        if genicam.IsWritable(node_map.GetNode("OffsetY")):
            self.camera.CenterY = True
            # self.camera.OffsetY = 176
        if genicam.IsWritable(node_map.GetNode("PixelFormat")):
            self.camera.PixelFormat = "Mono8"
        if genicam.IsWritable(node_map.GetNode("AcquisitionFrameRateEnable")):
            self.camera.AcquisitionFrameRateEnable = True
        if genicam.IsWritable(node_map.GetNode("AcquisitionFrameRate")):
            self.camera.AcquisitionFrameRate = self.parameters['fps']
        if genicam.IsWritable(node_map.GetNode("ExposureTime")):
            self.camera.ExposureTime = self.parameters['exposure_time']

    def set_output_file(self):
        """Set OpenCV output file. -1 opens VFW dialog in Windows."""
        # self.output = cv.VideoWriter(self.parameters['output_file'],-1,
        #                 self.parameters['fps'], (self.parameters['width'],
        #                 self.parameters['height']))
        # Changed to support skvideo
        self.output = skvideo.io.FFmpegWriter(self.parameters['output_file'], outputdict=self.parameters['ffmpeg_param'])


    def set_counter(self):
        """Sets cameras frame counter (Counter1) and resets it."""
        self.camera.CounterSelector = "Counter1"
        self.camera.CounterResetSource = "Software"
        self.camera.CounterReset.Execute()

    def set_exp_output(self):
        """Sets Line3 as a output pin and pulse every exposure. Default is low as active, so
        inverted to high as active."""
        self.camera.LineSelector = "Line3"
        self.camera.LineMode = "Output"
        self.camera.LineSource = "ExposureActive"
        self.camera.LineInverter = True

    def set_user_output(self):
        """Sets Line4 as user defined io, but not used now."""
        self.camera.LineSelector = "Line4"
        self.camera.LineMode = "Output"
        self.camera.LineSource = "UserOutput3"
        self.camera.LineInverter = True
        self.camera.UserOutputSelector = "UserOutput3"
        self.camera.UserOutputValue = False

    def grab_one(self):
        """Grabs one frame for mainly recording app preview."""
        self.print_info()
        self.camera.Open()
        self.set_parameters()
        self.grabResult = self.camera.GrabOne(100)
        image = self.converter.Convert(self.grabResult)
        img = cv.cvtColor(image.GetArray(), cv.COLOR_BGR2RGB)
        self.camera.Close()
        return img

    def grab_image(self):
        """Grab frame data and append timing values to output variale."""
        if genicam.IsReadable(self.grabResult.ChunkCounterValue):
            if genicam.IsReadable(self.grabResult.ChunkExposureTime):
                if genicam.IsReadable(self.grabResult.ChunkTimestamp):
                    if self.first_timestamp == 0:
                        self.first_timestamp = self.grabResult.ChunkTimestamp.Value
                    to_us = (self.grabResult.ChunkTimestamp.Value - self.first_timestamp) / 1e3
                    self.data_out.append((self.grabResult.ChunkCounterValue.Value, round(to_us, 2), self.grabResult.ChunkExposureTime.Value))
        # print(self.data_out)

        if self.grabResult.GrabSucceeded() and self.imageWindow.IsVisible():
            self.imageWindow.SetImage(self.grabResult)
            if self.parameters['record']:
                image = self.converter.Convert(self.grabResult)
                img = image.GetArray()
                # Skvideo write
                self.output.writeFrame(img)
                # OpenCV write
                # self.output.write(img)
        elif not self.imageWindow.IsVisible():
                self.camera.StopGrabbing()
        else:
            print("Error: ", self.grabResult.ErrorCode)

    def record(self):
        """Toggle when not previewing."""
        self.parameters['record'] = True

    def start(self):
        """Main loop. Setup camera, run, close and save."""
        self.print_info()

        self.camera.Open()
        self.set_parameters()
        self.set_output_file()
        self.set_counter()
        self.set_exp_output()
        self.set_user_output()
        self.enable_chunks()

        self.imageWindow.Show()
        self.camera.StartGrabbing(pylon.GrabStrategy_OneByOne)

        while self.camera.IsGrabbing():
            self.counter  += 1
            self.grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            # Check to see if a buffer containing chunk data has been received.
            if pylon.PayloadType_ChunkData != self.grabResult.PayloadType:
                raise pylon.RUNTIME_EXCEPTION("Unexpected payload type received.")
            # Since we have activated the CRC Checksum feature, we can check
            # the integrity of the buffer first.
            # Note: Enabling the CRC Checksum feature is not a prerequisite for using
            # chunks. Chunks can also be handled when the CRC Checksum feature is deactivated.
            if self.grabResult.HasCRC() and self.grabResult.CheckCRC() == False:
                raise pylon.RUNTIME_EXCEPTION("Image was damaged!")
            self.grab_image()

        self.camera.Close()
        with open(self.parameters['output_csv'], 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.data_out)
        # self.disable_chunks()
        # Release OpenCV output file
        # self.output.release()
        # Close skvideo file
        self.output.close()
