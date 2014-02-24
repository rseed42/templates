import numpy as np
#-------------------------------------------------------------------------------
# Transform
#-------------------------------------------------------------------------------
class Transform(object):
    """ Transformation of homogenous coordinates
    """
    def __init__(self, matrix=np.identity(4,'f')):
        self.matrix = matrix

    def rotate_x(self, phi):
        rot = np.identity(4, 'f')
        rot[1,1] =  np.cos(phi)
        rot[1,2] = -np.sin(phi)
        rot[2,1] =  np.sin(phi)
        rot[2,2] =  np.cos(phi)
        self.matrix = np.dot(rot, self.matrix)

    def rotate_y(self, phi):
        rot = np.identity(4, 'f')
        rot[0,0] =  np.cos(phi)
        rot[0,2] = -np.sin(phi)
        rot[2,0] =  np.sin(phi)
        rot[2,2] =  np.cos(phi)
        self.matrix = np.dot(rot, self.matrix)

    def rotate_z(self, phi):
        """ phi is in radians
        """
        rot = np.identity(4, 'f')
        rot[0,0] =  np.cos(phi)
        rot[0,1] = -np.sin(phi)
        rot[1,0] =  np.sin(phi)
        rot[1,1] =  np.cos(phi)
        self.matrix = np.dot(rot, self.matrix)

    def scale(self, factor):
        scale = np.identity(4, 'f')
        scale[0,0] = factor
        scale[1,1] = factor
        scale[2,2] = factor
        self.matrix = np.dot(scale, self.matrix)

    def scale_x(self, scale):
        pass

    def scale_y(self, scale):
        pass

    def scale_z(self, scale):
        pass

    def translate_x(self, dx):
        pass

    def translate_y(self, dy):
        pass

    def translate_z(self, dz):
        pass

    def transform(self, vector):
        return np.dot(self.matrix, vector)
