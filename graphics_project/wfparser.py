import numpy as np
#-------------------------------------------------------------------------------
WAVEFRONT_EXT = '.obj'
#-------------------------------------------------------------------------------
class WaveFrontModel(object):
    def __init__(self, vertices):
        self.vertices = vertices
#-------------------------------------------------------------------------------
def read(filename):
    """ Read only the vertices from a wavefront file
    """
    vertices = []
    with file(filename, 'r') as fp:
        for line in fp:
            ln = line.strip()
            if not ln.startswith('v'): continue
            vertices.append(map(float, ln.split(' ')[1:]))
    return WaveFrontModel(np.array(vertices))
