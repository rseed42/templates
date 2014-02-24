from OpenGL.arrays import vbo
import OpenGL.GL as gl
import numpy as np
#-------------------------------------------------------------------------------
class Model(object):
    """
    """
    def __init__(self, name, primitive=gl.GL_TRIANGLES):
        self.name = name
        self.primitive = primitive
        self.vertices = []
        self.vertex_start = 0
        self.vertex_end = 0
        self.vbo = None

    def load_vertices(self, vertices):
        """ Load vertices in homogenous coordinates
            Beware that 'f' means 32-bit floats and
            the vertices we receive from the wavefront objects
            are automatically converted from strings to float32s
        """
        self.vertices = np.zeros((len(vertices), 4), 'f')
        self.vertices[:,-1] = 1
        self.vertices[:,:3] = vertices
        # By default show all vertices
        self.vertex_end = len(vertices)

    def create_vbo(self):
        self.vbo = vbo.VBO(self.vertices)
