import numpy as np
#-------------------------------------------------------------------------------
# Transform
#-------------------------------------------------------------------------------
class Transform(object):
    """ Transformation of homogenous coordinates
    """
    def __init__(self, matrix=np.identity(4,'f')):
        self.matrix = matrix

    # Decorators anyone?
    def rotate_x(self, phi):
        T = np.identity(4, 'f')
        T[1,1] =  np.cos(phi)
        T[1,2] = -np.sin(phi)
        T[2,1] =  np.sin(phi)
        T[2,2] =  np.cos(phi)
        self.update(T)

    def rotate_y(self, phi):
        T = np.identity(4, 'f')
        T[0,0] =  np.cos(phi)
        T[0,2] = -np.sin(phi)
        T[2,0] =  np.sin(phi)
        T[2,2] =  np.cos(phi)
        self.update(T)

    def rotate_z(self, phi):
        """ phi is in radians
        """
        T = np.identity(4, 'f')
        T[0,0] =  np.cos(phi)
        T[0,1] = -np.sin(phi)
        T[1,0] =  np.sin(phi)
        T[1,1] =  np.cos(phi)
        self.update(T)

    def scale(self, factor):
        T = np.identity(4, 'f')
        T[0,0] = factor
        T[1,1] = factor
        T[2,2] = factor
        self.update(T)

    def scale_x(self, scale):
        T = np.identity(4, 'f')
        T[0,0] = scale
        self.update(T)

    def scale_y(self, scale):
        T = np.identity(4, 'f')
        T[1,1] = scale
        self.update(T)

    def scale_z(self, scale):
        T = np.identity(4, 'f')
        T[2,2] = scale
        self.update(T)

    def translate_x(self, dx):
        T = np.identity(4, 'f')
        T[0,3] = dx
        self.update(T)

    def translate_y(self, dy):
        T = np.identity(4, 'f')
        T[1,3] = dy
        self.update(T)

    def translate_z(self, dz):
        T = np.identity(4, 'f')
        T[2,3] = dz
        self.update(T)

    def update(self, T):
        self.matrix = np.dot(T, self.matrix)

    def transform(self, vector):
        return np.dot(self.matrix, vector)

    def reset(self):
        self.matrix = np.identity(4, 'f')
