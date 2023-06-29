"""Use taichi and tkinter to create a controllable visualizing window."""
import tkinter as tk
import threading
import queue
from visualizers.taichi import ParticleVisualizer

SHOULD_SHOW = True


class _TaichiThread(threading.Thread):
    """Class to interface with the taichi rendering thread."""

    def __init__(self, visualizer, q):
        self.q = q
        self.visualizer = visualizer
        super(_TaichiThread, self).__init__()

    def beginRendering(self):
        self.start()

    def onThread(self, function, *args, **kwargs):
        self.q.put((function, args, kwargs))

    # this function started with the threading.Thread.start() method
    # runs on its own thread
    def run(self):
        global SHOULD_SHOW
        # causes issues after destroyed
        while self.visualizer.window.running:
            if self.q.qsize() > 0:
                function, args, kwargs = self.q.get()
                function(*args, **kwargs)
                self.visualizer.render()
                SHOULD_SHOW = True

    def queueEnd(self):
        self.onThread(self._endRunning)

    def _endRunning(self):
        self.visualizer.window.running = False

    def queueMoveBackwardDist(self, dist):
        self.onThread(self.visualizer.moveBackwardDist, dist)

    def queueMoveForwardDist(self, dist):
        self.onThread(self.visualizer.moveForwardDist, dist)

    def queueSetRotationH(self, deg):
        self.onThread(self.visualizer.setCameraRotationH, deg)

    def queueSetRotationV(self, deg):
        self.onThread(self.visualizer.setCameraRotationV, deg)


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
    scale = 0.2
    window = createWindow("Controller", scale, scale)
    # share everything equally
    weight = 1
    window.grid_rowconfigure(0, weight=weight)
    window.grid_rowconfigure(1, weight=weight)
    window.grid_columnconfigure(0, weight=weight)
    window.grid_columnconfigure(1, weight=weight)

    visualizer = ParticleVisualizer("Visualizer", points)
    taichi_thread = _TaichiThread(visualizer, queue.Queue())

    move_dist = 5

    tk.Button(window, text="Move Back",
              command=lambda:
              taichi_thread.queueMoveBackwardDist(move_dist)
              ).grid(row=0, column=0)

    tk.Button(window, text="Move Forward",
              command=lambda:
              taichi_thread.queueMoveForwardDist(move_dist)
              ).grid(row=0, column=1)

    angle_min = -90
    angle_max = 90
    h_angle_scroll = tk.Scale(window, from_=angle_min, to=angle_max,
                              orient=tk.HORIZONTAL)
    v_angle_scroll = tk.Scale(window, from_=angle_min, to=angle_max,
                              orient=tk.VERTICAL)
    # angle_scroll.grid(row=1, column=1)
    h_angle_scroll.grid(row=1, column=0)
    v_angle_scroll.grid(row=1, column=1)
    h_curr_angle = h_angle_scroll.get()
    v_curr_angle = v_angle_scroll.get()
    # angle_scroll.grid(row=1, column=0)
    was_change = True
    # render the first time and creates the visualizer
    global SHOULD_SHOW
    if SHOULD_SHOW:
        SHOULD_SHOW = False
        visualizer.render()
        visualizer.window.show()
    taichi_thread.beginRendering()
    while taichi_thread.is_alive() and _tk_window_active(window):
        if SHOULD_SHOW:
            SHOULD_SHOW = False
            visualizer.window.show()
        new_angle = h_angle_scroll.get()
        if new_angle != h_curr_angle:
            h_curr_angle = new_angle
            taichi_thread.queueSetRotationH(h_curr_angle)
        new_angle = v_angle_scroll.get()
        if new_angle != v_curr_angle:
            v_curr_angle = new_angle
            taichi_thread.queueSetRotationV(v_curr_angle)
        # render the tkinter window
        window.update()
        # render the visualizer window
        # only if there were changes than update the taichi window

        if was_change:
            was_change = False

    if _tk_window_active(window):
        window.destroy()

    # this kills the other thread
    if taichi_thread.is_alive():
        taichi_thread.queueEnd()
        taichi_thread.join()
        taichi_thread.visualizer.window.destroy()


# checks if a tk window is active
def _tk_window_active(window):
    try:
        window.state()
        return True
    except tk.TclError:
        return False


def createWindow(name, x_scale, y_scale):
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
