"""Use taichi and tkinter to create a controllable visualizing window."""
import tkinter as tk
import queue
from visualizers.taichi import ParticleVisualizer
import threading


class TaichiThread(threading.Thread):
    def __init__(self, visualizer, q):
        self.q = q
        self.visualizer = visualizer
        # threading.Thread.__init__(self)
        self.event = threading.Event()
        super(TaichiThread, self).__init__()

    def onThread(self, function, *args, **kwargs):
        self.q.put((function, args, kwargs))

    def run(self):
        while self.visualizer.window.running:
            if self.q.qsize() > 0:
                function, args, kwargs = self.q.get()
                print(function)
                function

    def render(self):
        self.visualizer.render()

    def moveBackwardDist(self, dist):
            self.visualizer.moveBackwardDist(dist)


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
    window = tk.Tk()
    window.title("Controller")
    camera_scale = tk.Scale(window, from_=0, to=100, orient=tk.HORIZONTAL)
    camera_scale.pack()
    # Set the window size
    visualizer = ParticleVisualizer("Visualize", points)
    taichi_thread = TaichiThread(visualizer, queue.Queue())
    taichi_thread.start()
    prev_scale = camera_scale.get()
    was_change = True
    # TODO sometimes closing causes issues, fix that
    while visualizer.window.running:
        new_scale = camera_scale.get()
        # render the tkinter window
        window.update()
        # render the visualizer window
        # only if there were changes than update the taichi window
        if prev_scale != new_scale:
            prev_scale = new_scale
            was_change = True

        if was_change:
            # go through one render loop
            taichi_thread.onThread(taichi_thread.moveBackwardDist(1))
            taichi_thread.onThread(taichi_thread.render())
            was_change = False

    taichi_thread.join()
