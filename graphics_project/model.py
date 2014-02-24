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
        self.data_array = []
        self.start_id = 0
        self.end_id = 0
        self.vertex_start = 0
        self.vertex_end = 0
        self.colors = []
        self.vbo = None

    def load_data(self, data):
        self.data_array = data
        self.end_id = len(data)

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
        # Vertices & Colors
        self.vertex_array = np.ones((self.vertices.shape[0], 8), 'f')
        self.vertex_array[:,:4] = self.vertices
        # Small modifications for the cube
        # face color
        self.vertex_array[:6, 4:-1] = (0,0,1)
        # left
        self.vertex_array[6:12, 4:-1] = (1,0,0)
        # right
        self.vertex_array[12:18, 4:-1] = (0,1,0)



    def create_vbo(self):
        self.vbo = vbo.VBO(self.data_array, usage=gl.GL_STATIC_DRAW)
#        print self.data_array
