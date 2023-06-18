"""Use taichi and tkinter to create a controllable visualizing window."""
import tkinter as tk
from visualizers.taichi import ParticleVisualizer


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
    # Set the window title
    window.title("Hello Tkinter!")
    # Set the window size
    visualizer = ParticleVisualizer("Visualize", points)
    # main loop, close taichi first when quitting to avoid
    # errors
    while visualizer.window.running:
        # render the tkinter window
        window.update()
        # render the visualizer window
        visualizer.render()
        visualizer.handleInput()
