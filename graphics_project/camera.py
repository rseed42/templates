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
        """ eye, target, up are 3-vectors in world space
        """
        # Calculate the orthonormal basis of eye space first
        f = self.normalize(self.p - self.e)
        s = np.cross(f, self.u)
        up = np.cross(s, f)
#        print 'Basis:'
#        print s
#        print up
#        print f
        # Rotate camera to be upright with respect to up and looks
        # along f
        R = np.identity(4, 'f')
#        R[0:3, 0] = s
#        R[0:3, 1] = up
#        R[0:3, 2] = f
#        print R
        R[0:3, 0:3] = np.array([s,up,f]).T
#        print 'R:'
#        print R

        T = np.identity(4, 'f')
#        print '-e:', -self.e

        T[0:3, 0:4] = np.array([s,up,f,-self.e]).T
#        print 'T:'
#        print T
        return np.dot(T,R)

#        mat[0,3] = 0
#        return mat
#        # Check the optimization later
#        zaxis = self.normalize(self.eye - self.target)
#        xaxis = self.normalize(np.cross(self.up, zaxis))
#        yaxis = np.cross(zaxis, xaxis)
#        orientation = np.identity(4, 'f')
#        orientation[0:3,0] = xaxis
#        orientation[0:3,1] = yaxis
#        orientation[0:3,2] = zaxis
#        translation = np.identity(4, 'f')
#        translation[3,0:3] = -self.eye
#        return np.dot(orientation, translation)
