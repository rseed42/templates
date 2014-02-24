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
        self.Ambient = np.array([0.4,0.4,0.4,1], 'f')
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
            if not fn.endswith(wfparser.WAVEFRONT_EXT): continue
            wfmodel = wfparser.read(os.path.join(model_dir, fn))
            m = model.Model(fn.split('.')[0])
            m.load_vertices(wfmodel.vertices)
#            print m.vertex_array
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
        program = shader.Program(vertex_shader, fragment_shader)
        # Before linking we need to bind attribute locations
        program.bind_attrib_location(0, 'vPos')
        program.bind_attrib_location(1, 'vCol')
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
        self.uniforms['Ambient'] = gl.glGetUniformLocation(pid, 'Ambient')

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
            gl.glUniform4f(self.uniforms['Ambient'], *self.Ambient)

            # Bind vbo
            m.vbo.bind()
            gl.glEnableVertexAttribArray(0)
            gl.glEnableVertexAttribArray(1)
            gl.glVertexAttribPointer(0,4,gl.GL_FLOAT,gl.GL_FALSE,32,m.vbo)
            gl.glVertexAttribPointer(1,4,gl.GL_FLOAT,gl.GL_FALSE,32,m.vbo+16)
            # Draw primitive
            gl.glDrawArrays(gl.GL_TRIANGLES, m.vertex_start, m.vertex_end)
            m.vbo.unbind()
            gl.glDisableVertexAttribArray(0)
            gl.glDisableVertexAttribArray(1)
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
