import os
import cv2 as cv
import tkinter as tk
import tkinter.filedialog
# import from pillow
from PIL import ImageTk, Image

"""Handles tkinter GUI. Needs rework for better structure and to meet MVC criteria. No comments to
this version."""
class VideoWindow:
    def __init__(self, name="Video Window"):


        self.window = tk.Tk()
        self.window.title(name)

        self.status = True
        self.window.protocol('WM_DELETE_WINDOW', self.close_app)

        # Setup a GUI frames

        # GUI is divided two areas
        self.guiframe_left = tk.Frame(self.window, width=400, height = 600, borderwidth=2)
        self.guiframe_left.pack(side='left', fill='both')
        # self.guiframe_left.pack_propagate(0)
        self.guiframe_right = tk.Frame(self.window, width=400, height = 600, borderwidth=2)
        self.guiframe_right.pack(side='left', fill='both')
        self.guiframe_right.pack_propagate(0)


        # Setup a video frames to left side frame
        self.guiframe_video = tk.Frame(self.guiframe_left, borderwidth=2)
        self.guiframe_video.pack(side='top', fill='x')

        self.guiframe_video_1 = tk.Frame(self.guiframe_video, borderwidth=2)
        self.guiframe_video_1.pack(side='left', fill='y')

        self.guiframe_video_2 = tk.Frame(self.guiframe_video, borderwidth=2)
        self.guiframe_video_2.pack(side='right', fill='y')

        # Setup frame for right side controls
        self.guiframe_params = tk.Frame(self.guiframe_right, borderwidth=2)
        self.guiframe_params.pack(side='top', fill='x')

        self.param_label = tk.Label(self.guiframe_params, text="Detection parameter tuning:")
        self.param_label.pack(side='top', fill='x', pady=10)

        self.trackbars = {}
        self.frame = None
        self.width = None
        self.height = None
        self.canvas = None
        self.delay = 15
        self.video_1 = None
        self.video_2 = None

    def ask_file(self, file_title):
        return tk.filedialog.askopenfile(title = "file_title", filetypes = (("video files","*.avi *.mp4 *.mkv *.mpeg"),("all files","*.*"))).name

    def close_app(self):
        self.window.destroy()
        self.status = False

    def get_status(self):
        return self.status

    def add_video_frame_left(self, frame, size):
        self.frame = frame
        self.width = size[1]
        self.height = size[0]

        self.frame = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
        self.img = ImageTk.PhotoImage(image = Image.fromarray(self.frame))

        if self.video_1 is None:
            self.video_1 = tk.Label(self.guiframe_video_1, image=self.img)
            self.video_1.image = self.img
            self.video_1.pack(side='left', padx=10, pady=10)

        else:
            self.video_1.configure(image=self.img)
            self.video_1.image = self.img

    def add_video_frame_right(self, frame, size):
        self.frame = frame
        self.width = size[1]
        self.height = size[0]

        self.frame = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
        self.img = ImageTk.PhotoImage(image = Image.fromarray(self.frame))

        if self.video_2 is None:
            self.video_2 = tk.Label(self.guiframe_video_2, image=self.img)
            self.video_2.image = self.img
            self.video_2.pack(side='left', padx=10, pady=10)

        else:
            self.video_2.configure(image=self.img)
            self.video_2.image = self.img

    def create_scale(self, default, min=0, max=255,  text="Add text!", orient=tk.HORIZONTAL):
        text = tk.Label(self.guiframe_right, text=text)
        text.pack(side='top', fill='x', pady=2)
        scale = tk.Scale(self.guiframe_right, from_=min, to=max, orient=orient)
        scale.pack(side='top', fill='x')
        scale.set(default)
        return scale

    def create_controls(self):
        self.run = False
        self.prev = False
        self.reset = False
        self.save_params = False
        ctrl_frame = tk.Frame(self.guiframe_right)
        ctrl_frame.pack(side='top', fill='x', pady=10)

        tk.Button(ctrl_frame, text="Preview", bg='green', command=self.preview).pack(side='left', padx=2)
        tk.Button(ctrl_frame, text="Pause", command=self.pause).pack(side='left', padx=2)
        tk.Button(ctrl_frame, text="Reset Preview", command=self.reset_video).pack(side='left', padx=2)
        tk.Button(ctrl_frame, text="Analyze", bg='red', command=self.analyze).pack(side='left', padx=2)
        tk.Button(ctrl_frame, text="Save parameters", bg='yellow', command=self.save_parameters).pack(side='left', padx=2)

    def create_progress(self):
        progress = tk.Frame(self.guiframe_left)
        progress.pack(side='top', fill='x', pady=10)
        current = tk.Label(progress, text="Progress")
        current.pack(side='top', pady=10)
        return current

    def save_parameters(self):
        self.save_params = True

    def preview(self):
        self.prev = True

    def pause(self):
        self.prev = False

    def reset_video(self):
        self.reset = True

    def analyze(self):
        self.prev = False
        self.run = False
        self.reset_video()
        self.run = True

    def update_gui(self):
        # self.window.update_idletasks()
        self.window.update()

    def window_exist(self):
        return self.window.winfo_exists()
