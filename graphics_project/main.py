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
from OpenGL.GL import shaders
import src
import wfparser
import model
#-------------------------------------------------------------------------------
WND_SIZE = (800, 600)
WND_FLAGS = sdl.SDL_WINDOW_OPENGL | sdl.SDL_WINDOW_SHOWN | \
            sdl.SDL_WINDOW_RESIZABLE
MODEL_DIR = 'data'

#-------------------------------------------------------------------------------
# A very simple opengl app
#-------------------------------------------------------------------------------
class Game(object):
    def __init__(self):
        self.window = None
        self.glcontext = None
        self.running = True
        # Transformation matrices, etc. that are passed to shaders
        self.uniforms = {}
        #
        self.View = np.identity(4, 'f')
        self.Model = np.identity(4, 'f')
        self.Projection = np.identity(4, 'f')
        #
        # Models (later to be scene graph)
        self.models = []
        for pardir, subdirs, files in os.walk(MODEL_DIR):
            if pardir != MODEL_DIR: continue
            for subdir in subdirs:
                model = self.load_model(os.path.join(pardir, subdir))
                if not model: continue
                self.models.append(model)

    def load_model(self, model_dir):
        """ Load model from object file
        """
        for fn in os.listdir(model_dir):
            # Assuming only one file
            if not fn.endswith(wfparser.WAVEFRONT_EXT): continue
            wfmodel = wfparser.read(os.path.join(model_dir, fn))
            m = model.Model(fn.split('.')[0])
            m.load_vertices(wfmodel.vertices)
            return m
        return None

    def init_gl(self):
        # Clear buffers
        gl.glClearColor(0,0,0,0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        # Viewport
        gl.glViewport(0,0,WND_SIZE[0], WND_SIZE[1])
        # Shaders
        vertex_shader = shaders.compileShader(src.VERTEX_SHADER,
                                              gl.GL_VERTEX_SHADER)
        fragment_shader = shaders.compileShader(src.FRAGMENT_SHADER,
                                                gl.GL_FRAGMENT_SHADER)
        self.shader = shaders.compileProgram(vertex_shader, fragment_shader)
        # Prepare vertex buffer objects
        for m in self.models:
            m.create_vbo()

        # Shader parameters
        self.uniforms['View'] =  gl.glGetUniformLocation(self.shader, 'View')
        self.uniforms['Model'] =  gl.glGetUniformLocation(self.shader, 'Model')
        self.uniforms['Projection'] = gl.glGetUniformLocation(self.shader,
                                                              'Projection')
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
        # Draw stuff here
        shaders.glUseProgram(self.shader)
        # (location, count, transpose, value)
        gl.glUniformMatrix4fv(self.uniforms['View'], 1, True, self.View)
        gl.glUniformMatrix4fv(self.uniforms['Model'], 1, True, self.Model)
        gl.glUniformMatrix4fv(self.uniforms['Projection'], 1, True,
                              self.Projection)
        for m in self.models:
            try:
                m.vbo.bind()
                try:
                    gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
                    gl.glVertexPointerf(m.vbo)
                    gl.glDrawArrays(m.primitive, m.vertex_start, m.vertex_end)
                finally:
                    m.vbo.unbind()
                    gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
            finally:
                shaders.glUseProgram(0)

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