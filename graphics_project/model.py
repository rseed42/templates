from OpenGL.arrays import vbo
import OpenGL.GL as gl
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
        self.vertices = vertices
        # By default show all vertices
        self.vertex_end = len(vertices)

    def create_vbo(self):
        self.vbo = vbo.VBO(self.vertices)
