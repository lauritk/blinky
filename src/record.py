"""Quick and dirty high speed video recording application for Basler USB-cameras. Needs rework, but
works."""
from camera import Camera
import tkinter as tk
import tkinter.filedialog
from PIL import Image, ImageTk


def close_app():
    """Destroy GUI."""
    window.destroy()

def create_entry(default, text="Add text!"):
    """Creates text entry for adjusting recording parameters."""
    param_frame = tk.Frame(params)
    param_frame.pack(side='top', fill='x')
    text = tk.Label(param_frame, text=text)
    text.pack(side='left')
    entry = tk.Entry(param_frame)
    entry.insert(10, default)
    entry.pack(side='left')
    return entry

def ask_file(file_title):
    """Asks output file name."""
    return tk.filedialog.asksaveasfilename(title = "file_title", defaultextension='.avi', filetypes = (("video files","*.avi"),("all files","*.*")))

def set_parameters():
    """Updates parameters from text entries and updates cameras settings."""
    parameters['width'] = int(width.get())
    parameters['height'] = int(height.get())
    parameters['fps'] = float(fps.get())
    parameters['exposure_time'] = float(exposure_time.get())
    cam.update_parameters(parameters)
    preview_video()

def preview_video():
    """Updates preview image from camera. Grabs one frame. Fix to support live stream."""
    global preview_label
    preview = Image.fromarray(cam.grab_one())
    prev_img = ImageTk.PhotoImage(preview)
    if preview_label is None:
        preview_label = tk.Label(right, image=prev_img)
        preview_label.image = prev_img
        preview_label.pack(side="left", padx=10, pady=10)
    else:
        preview_label.configure(image=prev_img)
        preview_label.image = prev_img


def record_video():
    """Toggles recording and closes the initial windows. Recording video stream is opened in new
    Basler Video Window. Recording is stopped by closing the Basler Video Window."""
    global record
    record = True
    close_app()

# Setup tkinter GUI
window = tk.Tk()
window.title("Video Recorder")
window.protocol('WM_DELETE_WINDOW', close_app)

left = tk.Frame(window, width=400, height=600)
left.pack(side='left', fill='both')
left.pack_propagate(0)

right = tk.Frame(window, width=700, height=600)
right.pack(side='right', fill='both')
# right.pack_propagate(0)

params_label = tk.Label(left, text="Set video parameters:")
params_label.pack(side='top', fill='x', pady=10)

params = tk.Frame(left)
params.pack(side='top', fill='x')

preview_label = None
record = False

width = create_entry(160, "Width:")
height = create_entry(160, "Height:")
fps = create_entry(500.0, "Frames per second:")
exposure_time = create_entry(1000.0, "Frame exposure time in µs:")

set_button = tk.Button(params, text="Set parameters", command=set_parameters).pack(side='left')
prev_button = tk.Button(params, text="Preview", command=preview_video).pack(side='left')
record_button = tk.Button(params, bg='red', text="Record!", command=record_video).pack(side='left')

parameters = dict()
output_file = ask_file("Output video file")
# Fixes text fields that are uneditable after asking filename
window.deiconify()
parameters['width'] = int(width.get())
parameters['height'] = int(height.get())
parameters['fps'] = float(fps.get())
parameters['exposure_time'] = float(exposure_time.get())
parameters['output_file'] = output_file

# Setup connection to Basler USB camera
cam = Camera(parameters)
preview_video()

# parameters = {
#     'output_file': 'C:\MyTemp\Github\high-speed-video-eyeblink-detector/test.avi',
#     'width': 160,
#     'height': 160,
#     'fps': 200.0,
#     'exposure_time': 4000.0
#     }


window.mainloop()

# If recording toggled, we start recording. Implemented in the Camera class.
if record:
    cam.start()
