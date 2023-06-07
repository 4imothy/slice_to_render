import taichi as ti
from taichi.lang.matrix import Vector
from visualizers.utils import vec_to_euler, euler_to_vec
import time
import math


def render(points):
    p_viewer = ParticleVisualizer("Visualize", points)
    while p_viewer.window.running:
        p_viewer.render()


class ParticleVisualizer():
    def __init__(self, window_name, particles_pos):
        self.particles_pos = particles_pos
        self.window = ti.ui.Window(window_name, (768, 768))
        self.canvas = self.window.get_canvas()
        self.scene = ti.ui.Scene()
        self.camera = ti.ui.Camera()
        # set defaults
        self.camera.position(5, 2, 2)

    # render the particles given
    def render(self):
        # This line handles the user inputs
        # self.camera.track_user_inputs(self.window,
        #                               movement_speed=0.50,
        #                               hold_key=ti.ui.RMB)
        self.handle_input()
        self.scene.set_camera(self.camera)
        self.scene.ambient_light((0.8, 0.8, 0.8))
        self.scene.point_light(pos=(0.5, 1.5, 1.5), color=(1, 1, 1))
        self.scene.particles(self.particles_pos,
                             color=(1.0, 0.0, 0.0), radius=0.1)
        self.canvas.scene(self.scene)
        self.window.show()

    # these are relative to the camera
    def handle_input(self):
        movement_speed = 0.50
        yaw_speed: float = 10
        pitch_speed: float = 2.0
        # LMB = left mouse button
        hold_key = ti.ui.LMB
        front = self.get_camera_front()
        left = self.get_camera_left(front)
        up = self.get_camera_up()
        position_change = Vector([0.0, 0.0, 0.0])

        if self.camera.last_time is None:
            self.camera.last_time = time.perf_counter_ns()
        time_elapsed = (time.perf_counter_ns() - self.camera.last_time) * 1e-9
        self.camera.last_time = time.perf_counter_ns()

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
        self.camera.position(*(self.camera.curr_position + position_change))
        self.camera.lookat(*(self.camera.curr_lookat + position_change))

        curr_mouse_x, curr_mouse_y = self.window.get_cursor_pos()
        if (hold_key is None) or self.window.is_pressed(hold_key):
            if (self.camera.last_mouse_x is None) or \
               (self.camera.last_mouse_y is None):
                self.camera.last_mouse_x = curr_mouse_x
                self.camera.last_mouse_y = curr_mouse_y
            dx = curr_mouse_x - self.camera.last_mouse_x
            dy = curr_mouse_y - self.camera.last_mouse_y

            yaw, pitch = vec_to_euler(front)

            yaw_speed *= time_elapsed * 60.0
            pitch_speed *= time_elapsed * 60.0
            yaw -= dx * yaw_speed
            pitch += dy * pitch_speed

            pitch_limit = math.pi / 2 * 0.99
            if pitch > pitch_limit:
                pitch = pitch_limit
            elif pitch < -pitch_limit:
                pitch = -pitch_limit

            front = euler_to_vec(yaw, pitch)
            self.camera.lookat(*(self.camera.curr_position + front))

        self.camera.last_mouse_x = curr_mouse_x
        self.camera.last_mouse_y = curr_mouse_y

    """
    These functions will be called from console or a ui
    """

    def move_backward_dist(self, dist, front=None):
        # LMB = left mouse button
        front = self.get_camera_front()
        position_change = Vector([0.0, 0.0, 0.0])

        position_change -= front * dist
        self.camera.position(*(self.camera.curr_position + position_change))
        self.camera.lookat(*(self.camera.curr_lookat + position_change))

    def move_forward_dist(self, dist):
        # LMB = left mouse button
        front = self.get_camera_front()
        position_change = Vector([0.0, 0.0, 0.0])

        position_change += front * dist
        self.camera.position(*(self.camera.curr_position + position_change))
        self.camera.lookat(*(self.camera.curr_lookat + position_change))

    def move_left_dist(self, dist, front=None):
        left = self.get_camera_left(front)
        position_change = Vector([0.0, 0.0, 0.0])

        position_change += left * dist
        self.camera.position(*(self.camera.curr_position + position_change))
        self.camera.lookat(*(self.camera.curr_lookat + position_change))

    def move_right_dist(self, dist, front=None):
        left = self.get_camera_left(front)
        position_change = Vector([0.0, 0.0, 0.0])

        position_change -= left * dist
        self.camera.position(*(self.camera.curr_position + position_change))
        self.camera.lookat(*(self.camera.curr_lookat + position_change))

    def get_camera_front(self):
        return (self.camera.curr_lookat -
                self.camera.curr_position).normalized()

    def get_camera_left(self, front=None):
        if front is None:
            front = self.get_camera_front()
        return self.camera.curr_up.cross(front)

    def get_camera_up(self):
        return self.camera.curr_up

    def rotate_camera(self, deg, front=None):
        # Set the desired rotation angles in degrees
        if front is None:
            front = self.get_camera_front()

        rotation_amount_rad = math.radians(deg)
        yaw, pitch = vec_to_euler(front)
        yaw += rotation_amount_rad
        yaw = yaw % (2 * math.pi)
        front = euler_to_vec(yaw, pitch)

        # Update the camera lookat position
        self.camera.lookat(*(self.camera.curr_position + front))
