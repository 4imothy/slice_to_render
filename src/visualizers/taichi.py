"""Contain a visualizer that spawns a window utilizing taich."""
import taichi as ti
from taichi.lang.matrix import Vector
from visualizers.utils import vecToEuler, eulerToVec
import time
import math


def render(points):
    """
    Repeatedly draws points to the window.

    Controls to move camera:
        - w: forward
        - s: backward
        - a: left
        - d: right
        - e: up
        - q: down

    Parameters:
    - points (ti.vector.Field) containing
    the centers of the points

    Returns:
    None
    """
    p_viewer = ParticleVisualizer("Visualize", points)
    while p_viewer.window.running:
        p_viewer.handleInput()
        p_viewer.render()
        p_viewer.window.show()


class ParticleVisualizer():
    """A wrapper class for a taichi scene to render particles."""

    def __init__(self, window_name, particles_pos):
        """
        Initialize a new particle visualizer.

        Parameters:
        - window_name (str): The name of the window.
        - particles_pos (list or ndarray): The positions of the particles.

        Returns:
        - A new particle visualizer
        """
        self._particle_pos = particles_pos
        self.window = ti.ui.Window(window_name, (768, 768))
        self._canvas = self.window.get_canvas()
        self._scene = ti.ui.Scene()
        self._camera = ti.ui.Camera()
        # set defaults
        self._camera.position(0, 0, 0)
        # self._camera.lookat(0, 0, 0)  # set camera lookat

    def render(self):
        """
        Draws the particles to the screen while tracking user input.

        Doesn't contain loop to draw continuously. Doesn't show
        the resulting window.
        """
        self._scene.set_camera(self._camera)
        self._scene.point_light(pos=(0.5, 1.5, 1.5), color=(1, 1, 1))
        self._scene.ambient_light((0.8, 0.8, 0.8))
        self._scene.particles(self._particle_pos,
                              color=(1.0, 0.0, 0.0), radius=0.1)
        self._canvas.scene(self._scene)

    def handleInput(self):
        """
        Handle the user inputs and moves the camera accordingly.

        Controls to move camera:
        - w: forward
        - s: backward
        - a: left
        - d: right
        - e: up
        - q: down

        Returns:
        - None
        """
        movement_speed = 0.50
        yaw_speed: float = 10
        pitch_speed: float = 2.0
        # LMB = left mouse button
        hold_key = ti.ui.LMB
        front = self._getCameraFront()
        left = self._getCameraLeft(front)
        up = self._getCameraUp()
        position_change = Vector([0.0, 0.0, 0.0])

        if self._camera.last_time is None:
            self._camera.last_time = time.perf_counter_ns()
        time_elapsed = (time.perf_counter_ns() - self._camera.last_time) * 1e-9
        self._camera.last_time = time.perf_counter_ns()

        movement_speed *= time_elapsed * 60.0
        if self.window.is_pressed("w"):
            position_change += front * movement_speed
        if self.window.is_pressed("s"):
            position_change -= front * movement_speed
        if self.window.is_pressed("a"):
            position_change += left * movement_speed
        if self.window.is_pressed("d"):
            position_change -= left * movement_speed
        if self.window.is_pressed("e"):
            position_change += up * movement_speed
        if self.window.is_pressed("q"):
            position_change -= up * movement_speed
        self._camera.position(*(self._camera.curr_position + position_change))
        self._camera.lookat(*(self._camera.curr_lookat + position_change))

        curr_mouse_x, curr_mouse_y = self.window.get_cursor_pos()
        if (hold_key is None) or self.window.is_pressed(hold_key):
            if (self._camera.last_mouse_x is None) or \
               (self._camera.last_mouse_y is None):
                self._camera.last_mouse_x = curr_mouse_x
                self._camera.last_mouse_y = curr_mouse_y
            dx = curr_mouse_x - self._camera.last_mouse_x
            dy = curr_mouse_y - self._camera.last_mouse_y

            yaw, pitch = vecToEuler(front)

            yaw_speed *= time_elapsed * 60.0
            pitch_speed *= time_elapsed * 60.0
            yaw -= dx * yaw_speed
            pitch += dy * pitch_speed

            pitch_limit = math.pi / 2 * 0.99
            if pitch > pitch_limit:
                pitch = pitch_limit
            elif pitch < -pitch_limit:
                pitch = -pitch_limit

            front = eulerToVec(yaw, pitch)
            self._camera.lookat(*(self._camera.curr_position + front))

        self._camera.last_mouse_x = curr_mouse_x
        self._camera.last_mouse_y = curr_mouse_y

    # below functions are called in a /UI/
    def moveBackwardDist(self, dist, front=None):
        """
        Move the camera back a set distance.

        Does not rerender.

        Parameters:
        - dist (float): The amount

        Returns:
        - None
        """
        if front is None:
            front = self._getCameraFront()
        position_change = Vector([0.0, 0.0, 0.0])

        position_change -= front * dist
        self._camera.position(*(self._camera.curr_position + position_change))
        self._camera.lookat(*(self._camera.curr_lookat + position_change))

    def moveForwardDist(self, dist, front=None):
        """
        Move the camera forward a set distance.

        Does not rerender.

        Parameters:
        - dist (float): The amount

        Returns:
        - None
        """
        if front is None:
            front = self._getCameraFront()
        position_change = Vector([0.0, 0.0, 0.0])

        position_change += front * dist
        self._camera.position(*(self._camera.curr_position + position_change))
        self._camera.lookat(*(self._camera.curr_lookat + position_change))

    def moveLeftDist(self, dist, front=None):
        """
        Move the camera back a set distance.
        
        Does not rerender.

        Parameters:
        - dist (float): The amount

        Returns:
        - None
        """
        left = self._getCameraLeft(front)
        position_change = Vector([0.0, 0.0, 0.0])

        position_change += left * dist
        self._camera.position(*(self._camera.curr_position + position_change))
        self._camera.lookat(*(self._camera.curr_lookat + position_change))

    def moveRightDist(self, dist, front=None):
        """
        Move the camera right a set distance.

        Does not rerender

        Parameters:
        - dist (float): The amount

        Returns:
        - None
        """
        left = self._getCameraLeft(front)
        position_change = Vector([0.0, 0.0, 0.0])

        position_change -= left * dist
        self._camera.position(*(self._camera.curr_position + position_change))
        self._camera.lookat(*(self._camera.curr_lookat + position_change))

    def _getCameraFront(self):
        """
        Get the normalized direction that the camera is pointing.

        This function calculates the 'front' vector by subtracting the
        current position of the camera from the current
        look-at point of the camera. The resulting vector is then normalized.

        Returns:
        - front (Vector3): A normalized direction vector representing the
        'front' or viewing direction of the camera.
        """
        return (self._camera.curr_lookat -
                self._camera.curr_position).normalized()

    def _getCameraLeft(self, front=None):
        """
        Get the direction vector left of where the camera is pointing.

        This function calculates the 'left' vector by taking the cross
        product between the current up vector of the camera
        and the provided or calculated front vector. If no front vector
        is provided, it is obtained by calling the
        `get_camera_front` method. The resulting vector is then normalized.

        Parameters:
        - front (Vector3, optional): A pre-calculated front vector representing
        the viewing direction of the camera. If not provided, it is obtained by
        calling the `get_camera_front` method.

        Returns:
        - left (Vector3): A normalized direction vector representing the 'left'
        direction of the camera.

        """
        if front is None:
            front = self._getCameraFront()
        return self._camera.curr_up.cross(front)

    def _getCameraUp(self):
        """
        Get the current up vector of the camera.

        Returns:
        up (Vector3): The current up vector of the camera.
        """
        return self._camera.curr_up

    def setCameraRotationH(self, deg, front=None):
        """
        Set the rotation of the camera on horizontal plane.

        Parameters:
        - deg (float): The rotation angle in degrees.
        - front (Vector3, optional): A pre-calculated front vector representing
        the viewing direction of the camera.
        If not provided, it is obtained by calling `get_camera_front`
        """
        if front is None:
            front = self._getCameraFront()

        yaw, pitch = vecToEuler(front)
        yaw = -1 * math.radians(deg) % (2 * math.pi)
        front = eulerToVec(yaw, pitch)

        # Update the camera lookat position
        self._camera.lookat(*(self._camera.curr_position + front))

    def setCameraRotationV(self, deg, front=None):
        """
        Set the rotation of the camera in the vertical plane.

        Parameters:
        - deg (float): The rotation angle in degrees.
        - front (Vector3, optional): A pre-calculated front vector representing
        the viewing direction of the camera.
        If not provided, it is obtained by calling `get_camera_front`
        """
        if front is None:
            front = self._getCameraFront()

        yaw, pitch = vecToEuler(front)
        pitch = -1 * math.radians(deg) % (2 * math.pi)
        front = eulerToVec(yaw, pitch)

        # Update the camera lookat position
        self._camera.lookat(*(self._camera.curr_position + front))

    def rotateCamera(self, deg, front=None):
        """
        Rotates the camera by the specified degree amount to the right.

        Parameters:
        - deg (float): The rotation angle in degrees.
        - front (Vector3, optional): A pre-calculated front vector representing
        the viewing direction of the camera.
        If not provided, it is obtained by calling `get_camera_front`
        """
        # Set the desired rotation angles in degrees
        if front is None:
            front = self._getCameraFront()

        rotation_amount_rad = math.radians(deg)
        yaw, pitch = vecToEuler(front)
        yaw += rotation_amount_rad
        yaw = yaw % (2 * math.pi)
        front = eulerToVec(yaw, pitch)

        # Update the camera lookat position
        self._camera.lookat(*(self._camera.curr_position + front))
