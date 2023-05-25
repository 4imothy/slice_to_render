import taichi as ti


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
        # simplify this down to renderer.render()
        self.camera.track_user_inputs(self.window,
            movement_speed=0.50, hold_key=ti.ui.RMB)
        self.scene.set_camera(self.camera)
        self.scene.ambient_light((0.8, 0.8, 0.8))
        self.scene.point_light(pos=(0.5, 1.5, 1.5), color=(1, 1, 1))
        # if it is just points than only render those other wise
        # do the whole mesh
        self.scene.particles(self.particles_pos, color=(1.0, 0.0, 0.0), radius=0.1)
        # scene.mesh(particles_pos, two_sided=True)
        self.canvas.scene(self.scene)
        self.window.show()