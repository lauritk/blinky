"""
Quick and dirty GUI and command line user interface for blink detection application. Rework needed
for implementing better strcture (MVC?) and for performance via threading/multiprocessing.
"""
import sys, os
import copy
import csv
import cv2 as cv
import numpy as np

from pathlib import Path

from capture import Capture
from user_interface import VideoWindow
from filtering import VideoFiltering
from tracking import Tracking
from utils import Parameters

def init_gui():
    """Initialize GUI window"""
    window = VideoWindow("Eyeblink detector")
    return window

def set_controls(window, params):
    """Sets controls for the GUI. Default values from params dict. """
    if params is not None:
        window.pre_brightness = window.create_scale(params['pre_b_val'], 0, 255, "Pre-detection brightness:" )
        window.pre_contrast =  window.create_scale(params['pre_c_val'], 0, 255, "Pre-detection contrast:" )
        window.brightness = window.create_scale(params['b_val'], 0, 255, "Brightness:" )
        window.contrast =  window.create_scale(params['c_val'], 0, 255, "Contrast:" )
        window.threshold = window.create_scale(params['thres_val'], 0, 255, "Threshold:" )
        window.blur = window.create_scale(params['blur_val'], 0, 63, "Pre thresholding blur:" )
        # Padding for detected eye area
        window.pad = window.create_scale(params['pad_val'], -16, 64, "ROI padding:" )
        window.const_track = window.create_scale(params['const_track'], 0, 1, "Constant tracking (experimental):")
    window.create_controls()

def update_parameters(window, params):
    """Update parameters from GUI sliders."""
    if params is not None:
        params.params['pre_b_val'] = window.pre_brightness.get()
        params.params['pre_c_val'] = window.pre_contrast.get()
        params.params['b_val'] = window.brightness.get()
        params.params['c_val'] = window.contrast.get()
        params.params['thres_val'] = window.threshold.get()
        params.params['blur_val'] = window.blur.get()
        params.params['pad_val'] = window.pad.get()
        params.params['const_track'] = window.const_track.get()

def update_counter(counter, frame, cap):
    """Updates frame counter in the GUI."""
    counter.config(text = "Frame {} / {}".format(int(frame.frame.frame_num), int(cap.total_frames)))

def update_counter_cmd(frame, cap):
    """Updates frame counter (progress) in the command line. May be faster without."""
    print("Analyzing frame {} / {}".format(int(frame.frame.frame_num), int(cap.total_frames)), end='\r')

def append_frame_data(data, frame):
    """Appends frame number, time in ms and data (sum of white pixels) to output variable."""
    # frame number, time in ms, data
    data.append((frame.frame.frame_num, frame.frame.frame_time, frame.frequencies()))

def init_capture(input_file):
    """Initializes capture object from the input file."""
    cap = Capture(str(input_file))
    cap.capture_frame()
    return cap

def run(input_file, parameters_file, output_file, cascade_file, gui):
    data_out = [] # Output variable
    save = True # Toggle save function
    rec_reset = True # Toggle reset for analyzing in the cmd

    # Setup default settings if GUI in use
    if gui:
        # Save false, because we don't want to save/overwrite automaticly when in GUI
        save = False
        window = init_gui()
        input_file = Path(window.ask_file("Input video file"))
        output_file = input_file.parent / (input_file.stem + "_analysis.csv")
        parameters_file = input_file.parent / (input_file.stem + "_analysis.prm")

    # Init Parameters object where all the parameters are saved
    params = Parameters(parameters_file)

    # Loads parameters from file, if exists
    if parameters_file.exists():
        print("Loading parameters from file.")
        params.load_parameters()
    else:
        # No parameter file, so using defaults
        print("No parameters file. Loading default parameters." )
        # Default parameters
        params.params['pre_b_val'] = 128
        params.params['pre_c_val'] = 0
        params.params['b_val'] = 118
        params.params['c_val'] = 61
        params.params['thres_val'] = 85
        params.params['blur_val'] = 3
        params.params['pad_val'] = 12
        params.params['area_x'] = 160
        params.params['area_y'] = 160
        params.params['const_track'] = 0
        params.save_parameters()


    # Init capture
    cap = init_capture(input_file)

    # If GUI, set controls and add progress frame counter
    if gui:
        set_controls(window, params.params)
        counter = window.create_progress()

    # Setup filters
    pre_filt = VideoFiltering()
    out_filt = VideoFiltering()
    disp_filt = VideoFiltering()

    pre_filt.frame = copy.deepcopy(cap.frame)
    pre_filt.clahe()
    pre_filt.brightness_contrast(params.params['pre_b_val'], params.params['pre_c_val'])


    # Setup tracking and identify eye area
    tracker = Tracking(copy.deepcopy(pre_filt.frame))
    tracker.haar_classifier(cascadeFile=str(cascade_file))
    haar_pt = tracker.get_tracking_point('haar')
    # while not haar_pt:
    #     print("Did not find eye. Trying again next frame.")
    #     cap.capture_frame()
    #     tracker = Tracking(copy.deepcopy(cap.frame))
    #     tracker.haar_classifier(cascadeFile=str(cascade_file))
    #     haar_pt = tracker.get_tracking_point('haar')

    # Display video stats
    print("\nFrame count of the video: {}".format(int(cap.get_total_frames())))
    print("FPS of the video: {}".format(int(cap.get_fps())))
    print("Runtime in seconds: {}".format(cap.get_lenght_in_s()))

    # Main loop
    # Rework to work with threading and in the tkinter mainloop
    while(cap.capture_open()):

        if not haar_pt:
            # print("Did not find eye. Trying again.")
            tracker.haar_classifier(cascadeFile=str(cascade_file))
            haar_pt = tracker.get_tracking_point('haar')

        # Copy current frame to all filters and trackers
        pre_filt.frame = copy.deepcopy(cap.frame)
        out_filt.frame = copy.deepcopy(cap.frame)
        # Tracking is done for pre filtered frame
        pre_filt.clahe()
        pre_filt.brightness_contrast(params.params['pre_b_val'], params.params['pre_c_val'])
        tracker.frame = copy.deepcopy(pre_filt.frame)
        disp_filt.frame = copy.deepcopy(pre_filt.frame)


        # Draw bounding box for detected area and select region of interest for the ouput frame
        if haar_pt is not None and haar_pt:
            disp_filt.draw_bounding_box(haar_pt, params.params['pad_val'])
            out_filt.crop_roi(haar_pt, params.params['pad_val'])

        # Filtering the output
        out_filt.blur((params.params['blur_val'], params.params['blur_val']))
        out_filt.brightness_contrast(params.params['b_val'], params.params['c_val'])
        out_filt.threshold(params.params['thres_val'])
        out_filt.resize((params.params['area_x'], params.params['area_y']))

        # These will be run, if in GUI
        if gui:
            # Updating GUI if window is still open
            if window.get_status():
                update_counter(counter, out_filt, cap)
                update_parameters(window, params)
                window.add_video_frame_left(disp_filt.frame.frame, disp_filt.frame.get_frame_size())
                window.add_video_frame_right(out_filt.frame.frame, out_filt.frame.get_frame_size())
                window.update_gui()

            # Check status of preview and analyze buttons in the GUI
            if window.run or window.prev:
                # Resets video before running analysis or previw
                if window.reset or not out_filt.frame.frame_num < cap.get_total_frames() - 1:
                    cap.reset()
                    window.reset = False
                elif window.run:
                    # Flag save if analysis started
                    save = True
                    # Update progress in command line and append frame data to end result
                    update_counter_cmd(out_filt, cap)
                    append_frame_data(data_out, out_filt)
                cap.capture_frame()

            # Check parameters save button status and saves
            if window.save_params:
                print("Saving parameters to file.")
                window.save_params = False
                params.save_parameters()

            # Exit capture and program if window not open anymore
            if not window.get_status():
                cap.release_capture()

        # These run only in when in command line
        else:
            if rec_reset:
                cap.reset()
                rec_reset = False
            else:
                update_counter_cmd(out_filt, cap)
                append_frame_data(data_out, out_filt)
            cap.capture_frame()

        # Detect eye location and update if tracking enabled
        if params.params['const_track']:
            tracker.haar_classifier(cascadeFile=str(cascade_file), minSize=(24, 54))
            haar_pt = tracker.get_tracking_point('haar')

    # Save data to csv if save flag enabled
    if save:
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data_out)
