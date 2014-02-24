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
WND_FLAGS = sdl.SDL_WINDOW_OPENGL | sdl.SDL_WINDOW_SHOWN | \
            sdl.SDL_WINDOW_RESIZABLE
MODEL_DIR = 'data'
FOV_BOX_SIDE = 100
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
        self.viewbox = (-half_side, half_side, -half_side, half_side,
                        10, 110)
        # Transformation matrices, etc. that are passed to shaders
        self.uniforms = {}
        #
        self.cam = camera.Camera(eye=np.array([0,0,10]))
        # Vertex Transformation Matrices (Default)
        trans = transform.Transform()
        trans.rotate_y(np.deg2rad(10))
        self.Model = trans.matrix
        self.View = self.cam.view_matrix()
#        self.Projection = util.orthographic(*self.viewbox)
        self.Projection = util.frustrum(*self.viewbox)
        # Light
        self.Normal = np.identity(3, 'f')
        self.Ambient = np.array([0.4,0.4,0.4,1], 'f')
#        self.LightColor = np.ones(3, 'f')
        self.LightColor = np.array([0,0,1], 'f')
        self.LightDirection = np.array([0,0,1], 'f')
        self.HalfVector = np.array([0,0,-1], 'f')
        self.Shininess = 0.8;
        self.Strength = 1.;

        # Models (later to be scene graph)
        self.models = []
        for pardir, subdirs, files in os.walk(MODEL_DIR):
            if pardir != MODEL_DIR: continue
            for subdir in subdirs:
                if subdir.startswith('-'): continue
                model = self.load_model(os.path.join(pardir, subdir))
                if not model: continue
                self.models.append(model)
        # Keep track of shaders/programs
        self.shaders = {}
        self.programs = {}

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
        # Shaders

        vertex_shader = shader.Shader(src.VERTEX_SHADER, gl.GL_VERTEX_SHADER)
        vertex_shader.compile()
        self.shaders['std_vertex_shader'] = vertex_shader
        fragment_shader = shader.Shader(src.FRAGMENT_SHADER,
                                        gl.GL_FRAGMENT_SHADER)
        fragment_shader.compile()
        self.shaders['std_fragment_shader'] = fragment_shader
        vertex_shader_light = shader.Shader(src.VERTEX_SHADER_LIGHT,
                                            gl.GL_VERTEX_SHADER)
        vertex_shader_light.compile()
        self.shaders['light_vertex'] = vertex_shader_light
        fragment_shader_light = shader.Shader(src.FRAGMENT_SHADER_LIGHT,
                                              gl.GL_FRAGMENT_SHADER)
        fragment_shader_light.compile()
        self.shaders['light_fragment'] = fragment_shader_light
        #
        program = shader.Program(vertex_shader_light, fragment_shader_light)


        # Before linking we need to bind attribute locations
        program.bind_attrib_location(0, 'vPos')
        program.bind_attrib_location(1, 'vCol')
        program.bind_attrib_location(2, 'vNorm')
        # We are ready
        program.link()
        self.programs['std_program'] = program
        # Prepare vertex buffer objects
        for m in self.models:
            m.create_vbo()
        # Shader parameters
        pid = self.programs['std_program'].program_id
        self.uniforms['View'] =  gl.glGetUniformLocation(pid, 'View')
        self.uniforms['Model'] =  gl.glGetUniformLocation(pid, 'Model')
        self.uniforms['Projection'] = gl.glGetUniformLocation(pid, 'Projection')
        self.uniforms['Normal'] = gl.glGetUniformLocation(pid, 'Normal')
        self.uniforms['Ambient'] = gl.glGetUniformLocation(pid, 'Ambient')
        self.uniforms['LightColor'] = gl.glGetUniformLocation(pid, 'LightColor')
        self.uniforms['LightDirection'] = gl.glGetUniformLocation(pid,
                                                              'LightDirection')
        self.uniforms['HalfVector'] = gl.glGetUniformLocation(pid, 'HalfVector')
        self.uniforms['Shininess'] = gl.glGetUniformLocation(pid, 'Shininess')
        self.uniforms['Strength'] = gl.glGetUniformLocation(pid, 'Strength')

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
    def render(self):
        """ Show scene: mostly automatic
        """
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        for m in self.models:
            # 1. Use shaders for this vbo
            self.programs['std_program'].use()
            # (location, count, transpose, value)
            gl.glUniformMatrix4fv(self.uniforms['View'], 1, True, self.View)
            gl.glUniformMatrix4fv(self.uniforms['Model'], 1, True, self.Model)
            gl.glUniformMatrix4fv(self.uniforms['Projection'], 1, True,
                                  self.Projection)
            gl.glUniformMatrix3fv(self.uniforms['Normal'], 1, True,
                                  self.Normal)
            gl.glUniform4f(self.uniforms['Ambient'], *self.Ambient)
            gl.glUniform3f(self.uniforms['LightColor'], *self.LightColor)
            gl.glUniform3f(self.uniforms['LightDirection'],
                                         *self.LightDirection)
            gl.glUniform3f(self.uniforms['HalfVector'], *self.HalfVector)
            gl.glUniform1f(self.uniforms['Shininess'], self.Shininess)
            gl.glUniform1f(self.uniforms['Strength'], self.Strength)

            # Bind vbo
            m.vbo.bind()
            gl.glEnableVertexAttribArray(0)
            gl.glEnableVertexAttribArray(1)
            gl.glEnableVertexAttribArray(2)
            gl.glVertexAttribPointer(0,4,gl.GL_FLOAT,gl.GL_FALSE,48,m.vbo)
            gl.glVertexAttribPointer(1,4,gl.GL_FLOAT,gl.GL_FALSE,48,m.vbo+16)
            gl.glVertexAttribPointer(2,4,gl.GL_FLOAT,gl.GL_FALSE,48,m.vbo+32)
            # Draw primitive
            gl.glDrawArrays(gl.GL_TRIANGLES, m.start_id, m.end_id)
            m.vbo.unbind()
            gl.glDisableVertexAttribArray(0)
            gl.glDisableVertexAttribArray(1)
            gl.glDisableVertexAttribArray(2)
            # Deactivate shader program
            gl.glUseProgram(0)

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
