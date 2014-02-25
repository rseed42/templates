import numpy as np
#-------------------------------------------------------------------------------
class Camera(object):
    """ Using naming conventions from the OpenGL Bible
    """
    def __init__(self, position=np.array([0,0,10],'f'),
                       target=np.zeros(3,'f'),
                       orientation = np.array([0,0,1])):
        self.e = position
        self.p = target
        # Check for normalization
        if self.norm(orientation) != 1.0:
            raise Exception("Camera orientation is not normalized!")
        self.u = orientation

    def norm(self, x):
        return float(sum(x*x)**0.5)

    def normalize(self, x):
        # Just to be sure
        norm = self.norm(x)
        if norm == 0: return np.zeros(3, 'f')
        return x/norm

    def view_matrix(self):
        """ World space -> Eye space transformation
        """
        # Calculate the orthonormal basis of eye space first
        f = self.normalize(self.p - self.e)
        s = np.cross(f, self.u)
        up = np.cross(s, f)
        # Rotate camera to be upright with respect to up and looks
        # along f
        R = np.identity(4, 'f')
        R[0:3, 0:3] = np.array([s,up,f]).T
        T = np.identity(4, 'f')
        T[0:3, 0:4] = np.array([s,up,f,-self.e]).T
        # There may be some room for optimization here
        return np.dot(T,R)
