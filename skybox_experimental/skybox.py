# Author: Simulan

from direct.showbase.ShowBase import ShowBase
from direct.stdpy import threading2
from direct.filter.CommonFilters import CommonFilters
from panda3d.core import load_prc_file_data
from panda3d.core import BitMask32
from panda3d.core import Shader, ShaderAttrib
from panda3d.core import TransformState
from panda3d.core import PointLight
from panda3d.core import Spotlight
from panda3d.core import PerspectiveLens
from panda3d.core import ConfigVariableManager
from panda3d.core import FrameBufferProperties
from panda3d.core import AntialiasAttrib
from panda3d.core import Fog
from direct.interval.LerpInterval import LerpPosHprInterval
import sys
import random
import time
from panda3d.core import LPoint3f, Point3, Vec3, LVecBase3f, VBase4
from panda3d.core import WindowProperties
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
# gui imports
from direct.gui.DirectGui import *
from panda3d.core import TextNode
# new pbr imports
import gltf
# local imports
# import actor_data


class app(ShowBase):
    def __init__(self):
        load_prc_file_data("", """
            win-size 1680 1050
            window-title P3D Space Tech Demo Skybox Test 1
            show-frame-rate-meter #t
            framebuffer-srgb #t
            framebuffer-multisample 1
            multisamples 4
            view-frustum-cull 0
            textures-power-2 none
            hardware-animated-vertices #t
            gl-depth-zero-to-one true
            clock-frame-rate 60
            interpolate-frames 1
            cursor-hidden #t
            fullscreen #f
        """)

        # Initialize the showbase
        super().__init__()
        gltf.patch_loader(self.loader)
        
        props = WindowProperties()
        props.set_mouse_mode(WindowProperties.M_relative)
        base.win.request_properties(props)
        base.set_background_color(0.5, 0.5, 0.8)
        
        self.camLens.set_fov(80)
        self.camLens.set_near_far(0.01, 90000)
        self.camLens.set_focal_length(7)
        self.camera.set_pos(-300, -300, 0)
        
        # ConfigVariableManager.getGlobalPtr().listVariables()
        
        # point light generator
        for x in range(0, 3):
            plight_1 = PointLight('plight')
            # add plight props here
            plight_1_node = self.render.attach_new_node(plight_1)
            # group the lights close to each other to create a sun effect
            plight_1_node.set_pos(random.uniform(-21, -20), random.uniform(-21, -20), random.uniform(20, 21))
            self.render.set_light(plight_1_node)
        
        # point light for volumetric lighting filter
        plight_1 = PointLight('plight')
        # add plight props here
        plight_1_node = self.render.attach_new_node(plight_1)
        # group the lights close to each other to create a sun effect
        plight_1_node.set_pos(random.uniform(-21, -20), random.uniform(-21, -20), random.uniform(20, 21))
        self.render.set_light(plight_1_node)
            
        scene_filters = CommonFilters(base.win, base.cam)
        scene_filters.set_bloom()
        scene_filters.set_high_dynamic_range()
        scene_filters.set_exposure_adjust(0.6)
        scene_filters.set_gamma_adjust(1.1)
        # scene_filters.set_volumetric_lighting(plight_1_node, 32, 0.5, 0.7, 0.1)
        # scene_filters.set_blur_sharpen(0.9)
        # scene_filters.set_ambient_occlusion(32, 0.05, 2.0, 0.01, 0.000002)

        self.accept("f3", self.toggle_wireframe)
        self.accept("escape", sys.exit, [0])
        
        exponential_fog = Fog('world_fog')
        exponential_fog.set_color(0.6, 0.7, 0.7)
        # this is a very low fog value, set it higher for a greater effect
        exponential_fog.set_exp_density(0.00009)
        # self.render.set_fog(exponential_fog)
        
        self.game_start = 0
        
        skybox = self.loader.load_model('skyboxes/40k_test.gltf')
        skybox.reparent_to(self.render)
        skybox.set_scale(100)
        
        aster_bool = False
        
        # add some asteroids
        for x in range(100):
            ran_pos = Vec3(random.uniform(-300, 300), random.uniform(-300, 300), random.uniform(-300, 300))
            
            if not aster_bool:
                asteroid = self.loader.load_model('models/asteroid_1.gltf')
                aster_bool = True
                
            if aster_bool:
                asteroid = self.loader.load_model('models/asteroid_2.gltf')
                aster_bool = False
                
            asteroid.reparent_to(self.render)
            asteroid.set_pos(ran_pos)
            asteroid.set_scale(random.uniform(0.1, 10))
            a_pos = asteroid.get_pos()
            ran_inter = random.uniform(-20, 20)
            ran_h = random.uniform(-180, 180)
            asteroid.set_h(ran_h)
            a_rotate = LerpPosHprInterval(asteroid, 100, (a_pos[0] + ran_inter, a_pos[1] + ran_inter, a_pos[2] + ran_inter), (360, 360, 0)).loop()

        # load the scene shader
        scene_shader = Shader.load(Shader.SL_GLSL, "shaders/simplepbr_vert_mod_1.vert", "shaders/simplepbr_frag_mod_1.frag")
        self.render.set_shader(scene_shader)
        self.render.set_antialias(AntialiasAttrib.MMultisample)
        scene_shader = ShaderAttrib.make(scene_shader)
        scene_shader = scene_shader.setFlag(ShaderAttrib.F_hardware_skinning, True)
        
        # directly make a text node to display text
        text_2 = TextNode('text_2_node')
        text_2.set_text("P3D Space Tech Demo Skybox Test")
        text_2_node = self.aspect2d.attach_new_node(text_2)
        text_2_node.set_scale(0.04)
        text_2_node.set_pos(-1.4, 0, 0.8)
        # import font and set pixels per unit font quality
        nunito_font = self.loader.load_font('fonts/Nunito/Nunito-Light.ttf')
        nunito_font.set_pixels_per_unit(100)
        nunito_font.set_page_size(512, 512)
        # apply font
        text_2.set_font(nunito_font)
        text_2.set_text_color(0.1, 0.1, 0.1, 1)

        # 3D player movement system begins
        self.keyMap = {"left": 0, "right": 0, "forward": 0, "backward": 0, "run": 0, "jump": 0, "up": 0, "down": 0}

        def setKey(key, value):
            self.keyMap[key] = value

        # define button map
        self.accept("a", setKey, ["left", 1])
        self.accept("a-up", setKey, ["left", 0])
        self.accept("d", setKey, ["right", 1])
        self.accept("d-up", setKey, ["right", 0])
        self.accept("w", setKey, ["forward", 1])
        self.accept("w-up", setKey, ["forward", 0])
        self.accept("s", setKey, ["backward", 1])
        self.accept("s-up", setKey, ["backward", 0])
        self.accept("lshift", setKey, ["up", 1])
        self.accept("lshift-up", setKey, ["up", 0])
        self.accept("lcontrol", setKey, ["down", 1])
        self.accept("lcontrol-up", setKey, ["down", 0])
        self.accept("space", setKey, ["jump", 1])
        self.accept("space-up", setKey, ["jump", 0])
        # disable mouse
        self.disable_mouse()

        # the player movement speed
        self.inc_var = 1
        self.max_speed_inc = 0.02
        self.max_abs_speed = 0.2
        self.inertia_x = 0
        self.inertia_y = 0
        self.inertia_z = 0

        def move(Task):
            if self.game_start > 0:
                # get mouse data
                mouse_watch = base.mouseWatcherNode
                if mouse_watch.has_mouse():
                    pointer = base.win.get_pointer(0)
                    mouseX = pointer.get_x()
                    mouseY = pointer.get_y()
                    
                # screen sizes
                window_Xcoord_halved = base.win.get_x_size() // 2
                window_Ycoord_halved = base.win.get_y_size() // 2
                # mouse speed
                mouseSpeedX = 0.2
                mouseSpeedY = 0.2
                # maximum and minimum pitch
                maxPitch = 90
                minPitch = -50
                # cam view target initialization
                camViewTarget = LVecBase3f()
                # clock
                dt = globalClock.get_dt()

                if base.win.movePointer(0, window_Xcoord_halved, window_Ycoord_halved):
                    p = 0

                    if mouse_watch.has_mouse():
                        # calculate the pitch of camera
                        p = self.camera.get_p() - (mouseY - window_Ycoord_halved) * mouseSpeedY

                    # sanity checking
                    if p < minPitch:
                        p = minPitch
                    elif p > maxPitch:
                        p = maxPitch

                    if mouse_watch.has_mouse():
                        # directly set the camera pitch
                        self.camera.set_p(p)
                        camViewTarget.set_y(p)

                    # rotate the self.player's heading according to the mouse x-axis movement
                    if mouse_watch.has_mouse():
                        h = self.camera.get_h() - (mouseX - window_Xcoord_halved) * mouseSpeedX

                    if mouse_watch.has_mouse():
                        # sanity checking
                        if h < -360:
                            h += 360

                        elif h > 360:
                            h -= 360

                        self.camera.set_h(h)
                        camViewTarget.set_x(h)
                        
                if self.inertia_x > self.max_abs_speed:
                    self.inertia_x = self.max_abs_speed

                if self.inertia_y > self.max_abs_speed:
                    self.inertia_y = self.max_abs_speed
                    
                if self.inertia_z > self.max_abs_speed:
                    self.inertia_z = self.max_abs_speed

                if self.keyMap["right"]:            
                    if self.inertia_x > 0:
                        self.inertia_x += self.inc_var * dt
                    else:
                        self.inertia_x = self.max_speed_inc
                        
                    self.camera.set_x(self.camera, self.inertia_x)

                if self.keyMap["left"]:
                    if self.inertia_x < 0:
                        self.inertia_x -= self.inc_var * dt
                    
                    else:
                        self.inertia_x = -self.max_speed_inc
                        
                    self.camera.set_x(self.camera, self.inertia_x)
                    
                if self.keyMap["forward"]:
                    # print(self.inertia_y)
                    if self.inertia_y > 0:
                        self.inertia_y += self.inc_var * dt
                    
                    else:
                        self.inertia_y = self.max_speed_inc
                        
                    self.camera.set_y(self.camera, self.inertia_y)
                    
                if self.keyMap["backward"]:
                    if self.inertia_y < 0:
                        self.inertia_y -= self.inc_var * dt
                    
                    else:
                        self.inertia_y = -self.max_speed_inc
                        
                    self.camera.set_y(self.camera, self.inertia_y)
                    
                if self.keyMap["up"]:
                    if self.inertia_z > 0:
                        self.inertia_z += self.inc_var * dt
                    
                    else:
                        self.inertia_z = self.max_speed_inc
                        
                    self.camera.set_z(self.camera, self.inertia_z)
                    
                elif self.keyMap["down"]:
                    if self.inertia_z < 0:
                        self.inertia_z -= self.inc_var * dt
                    
                    else:
                        self.inertia_z = -self.max_speed_inc
                        
                    self.camera.set_z(self.camera, self.inertia_z)
                    
                else:
                    self.camera.set_x(self.camera, self.inertia_x)
                    self.camera.set_y(self.camera, self.inertia_y)
                    self.camera.set_z(self.camera, self.inertia_z)
                
            return Task.cont

        def update(Task):
            if self.game_start < 1:
                self.game_start = 1
            return Task.cont

        self.task_mgr.add(move)
        self.task_mgr.add(update)

app().run()

