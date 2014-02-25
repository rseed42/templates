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

UNIFORM_MODEL = ['ViewMatrix', 'ModelMatrix', 'ProjectionMatrix',
                 'NormalMatrix', 'Ambient', 'LightColor', 'LightPosition',
                 'Shininess', 'Strength', 'EyeDirection', 'ConstantAttenuation',
                 'LinearAttenuation', 'QuadraticAttenuation']
UNIFORM_SKYBOX = ['ViewMatrix', 'ModelMatrix', 'ProjectionMatrix']
UNIFORM_TYPES = dict(ViewMatrix='mat4', ModelMatrix='mat4',
                     ProjectionMatrix='mat4', NormalMatrix='mat3',
                     Ambient='vec3', LightColor='vec3', LightPosition='vec3',
                     Shininess='float', Strength='float', EyeDirection='vec3',
                     ConstantAttenuation='float', LinearAttenuation='float',
                     QuadraticAttenuation='float'
)
UNIFORM_FUNCTIONS = {'mat4':lambda i,x: gl.glUniformMatrix4fv(i,1,True,x),
                     'mat3':lambda i,x: gl.glUniformMatrix3fv(i,1,True,x),
                     'vec3':lambda i,x: gl.glUniform3f(i,*x),
                     'float':lambda i,x: gl.glUniform1f(i,x)
}
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
        self.cam = camera.Camera(position=np.array([0,0,1.5],'f'),
                                 target=np.array([0,0,0],'f'),
                                 orientation=np.array([0,1,0],'f')
        )
        # Vertex Transformation Matrices (Default)
        self.uniform_values_model = self.define_model_uniform_values()
        self.uniform_values_skybox = dict([(k, self.uniform_values_model[k]) \
                                            for k in UNIFORM_SKYBOX])
        # Models (later to be scene graph)
        self.cube = self.load_model('data/cube')
        self.skybox = self.load_model('data/skybox')

    def define_model_uniform_values(self):
        uniform = {}
        trans = transform.Transform()
        trans.scale(0.5)
        trans.rotate_x(np.deg2rad(45))
        trans.rotate_y(np.deg2rad(45))
        #trans.translate_z(+0.2)
#        trans.translate_x(0.4)
#        trans.translate_y(20)
#        trans.translate_z(-10)
        uniform['ModelMatrix'] = trans.matrix
        uniform['ViewMatrix'] = self.cam.view_matrix()
        uniform['ProjectionMatrix'] = util.frustum(*self.viewbox)

        # ----------- Light -------------
        uniform['NormalMatrix'] = np.identity(3, 'f')
        uniform['Ambient'] = np.array([0.2, 0.2, 0.2], 'f')
        uniform['LightColor'] = np.array([1, 1, 1], 'f')
        # Light position is a vec3, but needs to be transformed to eye space
        light = np.array([1.0, 3.0, 2.0,1], 'f')
        uniform['LightPosition'] = np.dot(uniform['ViewMatrix'], light)[:-1]
        uniform['Shininess'] = 0.2;
        uniform['Strength'] = 1.0;
        uniform['EyeDirection'] = np.array([0, 0, 1], 'f')
        uniform['ConstantAttenuation'] = 0.3
        uniform['LinearAttenuation'] = 0.2
        uniform['QuadraticAttenuation'] = 0.2
        return uniform

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

    def shader_program(self, src_vertex, src_fragment):
        vertex = shader.Shader(src_vertex, gl.GL_VERTEX_SHADER)
        vertex.compile()
        fragment = shader.Shader(src_fragment, gl.GL_FRAGMENT_SHADER)
        fragment.compile()
        # Attach to a program
        program = shader.Program(vertex, fragment)
        # Before linking we need to bind attribute locations
        program.bind_attrib_location(0, 'VertexPosition')
        program.bind_attrib_location(1, 'VertexNormal')
        program.bind_attrib_location(2, 'VertexColor')
        # We are ready
        program.link()
        return program

    def get_uniform_ids(self, program_id, params):
        """ Find out the location indices of uniform shader parameters
        """
        mapping = {}
        for name in params:
            mapping[name] = gl.glGetUniformLocation(program_id, name)
        return mapping

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
        self.program_model = self.shader_program(src.VERTEX_POINT_LIGHT,
                                                 src.FRAGMENT_POINT_LIGHT,
        )
#        self.program_skybox = self.shader_program(src.VERTEX_SIMPLE,
#                                                  src.FRAGMENT_SIMPLE)
        #-----------------------------------------------
        # Prepare vertex buffer objects
        self.cube.create_vbo()
        # Shader parameters
        self.uniform_ids_model = self.get_uniform_ids(
                                                  self.program_model.program_id,
                                                  UNIFORM_MODEL)
#        self.uniform_ids_skybox = self.get_uniform_ids(
#                                                  self.progam_skybox.program_id,
#                                                  UNIFORM_SKYBOX)
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
    def show_object(self, program, uniform_names, uniform_ids, uniform_values,
                          model):
        # 1. Use shaders for this vbo
        program.use()
        # (location, count, transpose, value)
        for name in uniform_names:
            type_ = UNIFORM_TYPES[name]
            id_ = uniform_ids[name]
            val = uniform_values[name]
            UNIFORM_FUNCTIONS[type_](id_, val)

        # Bind vbo
        model.vbo.bind()
        for i in xrange(3):
            gl.glEnableVertexAttribArray(i)

        gl.glVertexAttribPointer(0,4,gl.GL_FLOAT,gl.GL_FALSE,44,model.vbo)
        gl.glVertexAttribPointer(1,3,gl.GL_FLOAT,gl.GL_FALSE,44,model.vbo+16)
        gl.glVertexAttribPointer(2,4,gl.GL_FLOAT,gl.GL_FALSE,44,model.vbo+28)
        # Draw primitive
        gl.glDrawArrays(model.primitive, model.start_id, model.end_id)
        model.vbo.unbind()
        for i in xrange(3):
            gl.glDisableVertexAttribArray(i)
        # Deactivate shader program
        gl.glUseProgram(0)

    def render(self):
        """ Show scene: mostly automatic
        """
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.show_object(self.program_model, UNIFORM_MODEL,
                         self.uniform_ids_model, self.uniform_values_model,
                         self.cube)
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
