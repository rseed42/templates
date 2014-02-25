""" Explicit compilation and linkiing of shaders in Python. Same steps as in C++.
"""
import sys
import OpenGL
import OpenGL.GL as gl
from OpenGL.GL import shaders
#-------------------------------------------------------------------------------
# Shader
#-------------------------------------------------------------------------------
class Shader(object):
    """ 1. Create a shader object.
        2. Compile the shader source into a shader object.
        3. Verify that the shader compiled successfully.
    """
    def __init__(self, src, type_):
        self.src = src
        self.shader_id = gl.glCreateShader(type_)
        if self.shader_id == 0:
            raise Exception("glCreateShader() failed")
        gl.glShaderSource(self.shader_id, self.src)

    def compile(self):
        gl.glCompileShader(self.shader_id)
        result = gl.glGetShaderiv(self.shader_id, gl.GL_COMPILE_STATUS)
        if result != 1:
            sys.stderr.write(gl.glGetShaderInfoLog(self.shader_id))
            raise Exception("Couldn't compile shader")

#-------------------------------------------------------------------------------
# Shader Program
#-------------------------------------------------------------------------------
class Program(object):
    """ 1. Create a shader program.
        2. Attach the shader objects to the shader program.
        3. Link the shader program.
        4. Verify that the shader link phase completed successfully.
        5. Use the shader for processing.
    """
    def __init__(self, *args):
        self.program_id = gl.glCreateProgram()
        if self.program_id == 0:
            raise Exception("glCreateProgram() failed")
        for shader in args:
            gl.glAttachShader(self.program_id, shader.shader_id)

    def link(self):
        """ Link is a separate step because we might use
            glBindAttribLocation before it.
        """
        gl.glLinkProgram(self.program_id)

    def bind_attrib_location(self, index, var_name):
        """ This is necessary if GLDL 330 is not available (@ 130)
        """
        gl.glBindAttribLocation(self.program_id, index, var_name)

    def use(self):
        try:
            gl.glUseProgram(self.program_id)
        except OpenGL.error.GLError:
            sys.stderr.write(gl.glGetProgramInfoLog(self.program_id))
            raise Exception("Couldn't use program {0}".format(self.program_id))
