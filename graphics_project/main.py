#!/usr/bin/env python
""" This is a Python implementation of the C++ version
"""
import os
import sys
import sdl2 as sdl
import sdl2.ext as sdlx
import OpenGL.GL as gl
import numpy as np
# Serious OpenGL stuff
import OpenGL.GL as gl
import OpenGL.GLU as glu
from OpenGL.arrays import vbo
import src
import wfparser
import model
import camera
import util
import shader
import transform
#-------------------------------------------------------------------------------
WND_SIZE = (800, 600)
ASPECT_HW = float(WND_SIZE[1])/WND_SIZE[0]
WND_FLAGS = sdl.SDL_WINDOW_OPENGL | sdl.SDL_WINDOW_SHOWN | \
            sdl.SDL_WINDOW_RESIZABLE
MODEL_DIR = 'data'
FOV_BOX_SIDE = 2
NEAR_PLANE = 1
FAR_PLANE = 3
MODEL_EXT = '.dat'
#-------------------------------------------------------------------------------
# A very simple opengl app
#-------------------------------------------------------------------------------
class Game(object):
    def __init__(self):
        self.window = None
        self.glcontext = None
        self.running = True
        half_side = 0.5*FOV_BOX_SIDE
        self.viewbox = (-half_side, half_side,
                        -half_side*ASPECT_HW, half_side*ASPECT_HW,
                        NEAR_PLANE, FAR_PLANE)
        # Transformation matrices, etc. that are passed to shaders
        self.uniforms = {}
        #
        self.cam = camera.Camera(position=np.array([0,0,1.5],'f'),
                                 target=np.array([0,0,0],'f'),
                                 orientation=np.array([0,1,0],'f')
        )
        # Vertex Transformation Matrices (Default)
        trans = transform.Transform()
        trans.scale(0.5)
        trans.rotate_x(np.deg2rad(45))
        trans.rotate_y(np.deg2rad(45))
        #trans.translate_z(+0.2)
#        trans.translate_x(0.4)
#        trans.translate_y(20)
#        trans.translate_z(-10)
        self.ModelMatrix = trans.matrix
        self.ViewMatrix = self.cam.view_matrix()
        self.ProjectionMatrix = util.frustum(*self.viewbox)

        # ----------- Light -------------
        self.NormalMatrix = np.identity(3, 'f')
        self.Ambient = np.array([0.2, 0.2, 0.2], 'f')
        self.LightColor = np.array([1, 1, 1], 'f')
        # Light position is a vec3, but needs to be transformed to eye space
        light = np.array([1.0, 3.0, 2.0,1], 'f')
        self.LightPosition = np.dot(self.ViewMatrix, light)[:-1]
        self.Shininess = 0.2;
        self.Strength = 1.0;
        self.EyeDirection = np.array([0, 0, 1], 'f')
        self.ConstantAttenuation = 0.3
        self.LinearAttenuation = 0.2
        self.QuadraticAttenuation = 0.2

        # Models (later to be scene graph)
        self.cube = self.load_model('data/cube')
        self.skybox = self.load_model('data/skybox')

    def load_model(self, model_dir):
        """ Load model from object file
        """
        for fn in os.listdir(model_dir):
            # Assuming only one file
            if not fn.endswith(MODEL_EXT): continue
            data = np.loadtxt(os.path.join(model_dir, fn), 'f')
            m = model.Model(fn.split('.')[0])
            m.load_data(data)
            return m
        return None

    def init_gl(self):
        # Clear buffers
        gl.glClearColor(0,0,0,0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        # Viewport
        gl.glViewport(0,0,WND_SIZE[0], WND_SIZE[1])
        # Is this enable by default?
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glFrontFace(gl.GL_CCW)
        # ------------- Shaders -------------
        vertex_point_light = shader.Shader(src.VERTEX_POINT_LIGHT,
                                           gl.GL_VERTEX_SHADER)
        vertex_point_light.compile()
        fragment_point_light = shader.Shader(src.FRAGMENT_POINT_LIGHT,
                                             gl.GL_FRAGMENT_SHADER)
        fragment_point_light.compile()
        # Attach to a program
        self.program_light = shader.Program(vertex_point_light,
                                            fragment_point_light)
        # Before linking we need to bind attribute locations
        self.program_light.bind_attrib_location(0, 'VertexPosition')
        self.program_light.bind_attrib_location(1, 'VertexNormal')
        self.program_light.bind_attrib_location(2, 'VertexColor')

        # We are ready
        self.program_light.link()
        #-----------------------------------------------
        # Prepare vertex buffer objects
        self.cube.create_vbo()
        # Shader parameters
        pid = self.program_light.program_id
        self.uniforms['ViewMatrix'] =  gl.glGetUniformLocation(pid,
                                                               'ViewMatrix')
        self.uniforms['ModelMatrix'] =  gl.glGetUniformLocation(pid,
                                                                'ModelMatrix')
        self.uniforms['ProjectionMatrix'] = gl.glGetUniformLocation(pid,
                                                             'ProjectionMatrix')
        self.uniforms['NormalMatrix'] = gl.glGetUniformLocation(pid,
                                                                'NormalMatrix')
        self.uniforms['Ambient'] = gl.glGetUniformLocation(pid, 'Ambient')
        self.uniforms['LightColor'] = gl.glGetUniformLocation(pid, 'LightColor')
        self.uniforms['LightPosition'] = gl.glGetUniformLocation(pid,
                                                              'LightPosition')
        self.uniforms['Shininess'] = gl.glGetUniformLocation(pid, 'Shininess')
        self.uniforms['Strength'] = gl.glGetUniformLocation(pid, 'Strength')
        self.uniforms['EyeDirection'] = gl.glGetUniformLocation(pid,
                                                                'EyeDirection')
        self.uniforms['ConstantAttenuation'] = gl.glGetUniformLocation(pid,
                                                          'ConstantAttenuation')
        self.uniforms['LinearAttenuation'] = gl.glGetUniformLocation(pid,
                                                            'LinearAttenuation')
        self.uniforms['QuadraticAttenuation'] = gl.glGetUniformLocation(pid,
                                                         'QuadraticAttenuation')
    #---------------------------------------
    # Init the whole system
    #---------------------------------------
    def initialize(self):
        """ Init in a C++ compatible way
        """
        if sdl.SDL_Init(sdl.SDL_INIT_EVERYTHING) < 0:
            return False

        sdl.SDL_GL_SetAttribute(sdl.SDL_GL_DOUBLEBUFFER, 1)
        self.window = sdl.SDL_CreateWindow('PySDL2 OpenGL',
                                           sdl.SDL_WINDOWPOS_CENTERED,
                                           sdl.SDL_WINDOWPOS_CENTERED,
                                           WND_SIZE[0], WND_SIZE[1],
                                           WND_FLAGS
        )
        if not self.window: return False
        self.glcontext = sdl.SDL_GL_CreateContext(self.window)
        # Open GL
        self.init_gl()
        return True

    def start(self):
        """ Main Loop
        """
        if not self.initialize():
            sys.exit(-1)
        while self.running:
            events = sdlx.get_events()
            for event in events:
                self.process_event(event)
            self.render()
        self.cleanup()
        sys.exit(0)

    #---------------------------------------
    # Render
    #---------------------------------------
    def show_skybox(self):
        pass

    def show_model(self, m):
        # 1. Use shaders for this vbo
        self.program_light.use()
        # (location, count, transpose, value)
        gl.glUniformMatrix4fv(self.uniforms['ViewMatrix'], 1, True,
                              self.ViewMatrix)
        gl.glUniformMatrix4fv(self.uniforms['ModelMatrix'], 1, True,
                              self.ModelMatrix)
        gl.glUniformMatrix4fv(self.uniforms['ProjectionMatrix'], 1, True,
                              self.ProjectionMatrix)
        gl.glUniformMatrix3fv(self.uniforms['NormalMatrix'], 1, True,
                              self.NormalMatrix)
        gl.glUniform3f(self.uniforms['Ambient'], *self.Ambient)
        gl.glUniform3f(self.uniforms['LightColor'], *self.LightColor)
        gl.glUniform3f(self.uniforms['LightPosition'],
                                     *self.LightPosition)
        gl.glUniform1f(self.uniforms['Shininess'], self.Shininess)
        gl.glUniform1f(self.uniforms['Strength'], self.Strength)
        gl.glUniform3f(self.uniforms['EyeDirection'], *self.EyeDirection)

        gl.glUniform1f(self.uniforms['ConstantAttenuation'],
                       self.ConstantAttenuation)
        gl.glUniform1f(self.uniforms['LinearAttenuation'],
                       self.LinearAttenuation)
        gl.glUniform1f(self.uniforms['QuadraticAttenuation'],
                       self.QuadraticAttenuation)
        # Bind vbo
        m.vbo.bind()
        gl.glEnableVertexAttribArray(0)
        gl.glEnableVertexAttribArray(1)
        gl.glEnableVertexAttribArray(2)
        gl.glVertexAttribPointer(0,4,gl.GL_FLOAT,gl.GL_FALSE,44,m.vbo)
        gl.glVertexAttribPointer(1,3,gl.GL_FLOAT,gl.GL_FALSE,44,m.vbo+16)
        gl.glVertexAttribPointer(2,4,gl.GL_FLOAT,gl.GL_FALSE,44,m.vbo+28)
        # Draw primitive
        gl.glDrawArrays(gl.GL_TRIANGLES, m.start_id, m.end_id)
        m.vbo.unbind()
        gl.glDisableVertexAttribArray(0)
        gl.glDisableVertexAttribArray(1)
        gl.glDisableVertexAttribArray(2)
        # Deactivate shader program
        gl.glUseProgram(0)

    def render(self):
        """ Show scene: mostly automatic
        """
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.show_skybox()
        self.show_model(self.cube)
        # Double buffering
        sdl.SDL_GL_SwapWindow(self.window)

    def cleanup(self):
        sdl.SDL_GL_DeleteContext(self.glcontext)
        sdl.SDL_DestroyWindow(self.window)
        sdl.SDL_Quit()

    def process_event(self, event):
        """ Event processing
        """
        if event.type == sdl.SDL_KEYDOWN:
            self.key_down(event.key.keysym)
        if event.type == sdl.SDL_QUIT:
            self.exit_()

    def exit_(self):
        self.running = False

    def key_down(self, keysym):
        if keysym.sym == sdl.SDLK_q:
            self.exit_()

if __name__ == '__main__':
    game = Game()
    game.start()
