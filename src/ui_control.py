"""Use taichi and tkinter to create a controllable visualizing window."""
import tkinter as tk
from concurrent import futures
import threading
import queue
from visualizers.taichi import ParticleVisualizer


# tried using taichi render as a seperate thread but taichi
# doesn't seem to work well with not being on the main thread
class _TkinterThread(threading.Thread):
    """A thread that runs to control the taichi render window."""
    def __init__(self, window)
        self.window = createWindow()
        super(_TaichiThread, self).__init__()

    def createWindow():
        return tk.Tk()
        
    def run(self):
        while self.windowActive():
            self.window.update()
    # checks if a tk window is active
    def windowActive(self):
        try:
            self.window.state()
            return True
        except tk.TclError:
            return False

class _TaichiThread(threading.Thread):
    """Class to interface with the taichi rendering thread."""

    def __init__(self, window_name, points, q):
        self.q = q
        self.window_name = window_name
        self.points = points
        self.visualizer = None
        super(_TaichiThread, self).__init__()

    def beginRendering(self):
        self.start()

    def onThread(self, function, *args, **kwargs):
        self.q.put((function, args, kwargs))

    # this function started with the threading.Thread.start() method
    # runs on its own thread
    def run(self):
        self.visualizer = ParticleVisualizer(self.window_name, self.points)
        self.visualizer.render()
        while self.visualizer.window.running:
            function, args, kwargs = self.q.get()
            function(*args, **kwargs)
            self.visualizer.render()

    def queueMoveBackwardDist(self, dist):
        self.onThread(self.visualizer.moveBackwardDist, dist)

    def queueMoveForwardDist(self, dist):
        self.onThread(self.visualizer.moveForwardDist, dist)


# make the proper things private in the Particlevisualizer class
def renderUI(points):
    """
    Create 2 windows to render and manipulate the point cloud.

    This function contains the render loop

    Parameters:
        - Points (taichi.Vector.field): the points to render

    Create the tk window in this file
    Returns:
        - None
    """
    # tk must be instantiated first
    window = _createWindow("Controller", 0.2, 0.2)
    taichi_thread = _TaichiThread("Visualize", points, queue.Queue())

    move_dist = 5

    tk.Button(window, text="Move Back",
              command=lambda:
              taichi_thread.queueMoveBackwardDist(move_dist)
              ).grid(row=0, column=0)

    tk.Button(window, text="Move Forward",
              command=lambda:
              taichi_thread.queueMoveForwardDist(move_dist)
              ).grid(row=0, column=1)

    camera_scale = tk.Scale(window, from_=0, to=100, orient=tk.HORIZONTAL)
    prev_scale = camera_scale.get()
    camera_scale.grid(row=1, column=0)
    was_change = True
    # render the first time and creates the visualizer
    taichi_thread.beginRendering()
    while taichi_thread.visualizer is None:
        pass
    # restructure for taichi to be on the main thread,
    # lock the rendering loop until there is an update
    # the tkinter runs on a seperate loop that is always running
    # calls functions on the main thread, only one loop necessary that just
    # calls functions to the main thread
    while taichi_thread.visualizer.window.running and _tk_window_active(window):
        new_scale = camera_scale.get()
        # render the tkinter window
        window.update()
        # render the visualizer window
        # only if there were changes than update the taichi window
        if prev_scale != new_scale:
            prev_scale = new_scale
            was_change = True

        if was_change:
            was_change = False

    if _tk_window_active(window):
        window.destroy()
    taichi_thread.visualizer.window.destroy()


# checks if a tk window is active
def _tk_window_active(window):
    try:
        window.state()
        return True
    except tk.TclError:
        return False


def _createWindow(name, x_scale, y_scale):
    """
    Create a tk window to control the taichi visualizer.

    Parameters:
        - name (str): Name of the window
        - x_scale (float): Percent of width of screen to take up
        - y_scale (float): Percent of height of screen to take up

    Returns
        - Window (tkinter.Tk): Top level widget
    """
    window = tk.Tk()
    window.title(name)
    # Get screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    # Calculate desired width and height
    desired_width = int(screen_width * x_scale)
    desired_height = int(screen_height * y_scale)
    # Set the window size
    window.geometry(f"{desired_width}x{desired_height}")

    return window
